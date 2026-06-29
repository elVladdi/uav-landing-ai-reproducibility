"""Active visual-servo correction using direct MAVLink setpoints.

This Phase 04 pilot assumes the vehicle is already airborne. It does not arm or
take off. By default it only performs lateral visual-servo correction; with
--enable-descent it adds a conservative positive-down velocity after the marker
has remained centered for several cycles. It captures the bottom camera image
from AirSim, computes the visual correction, converts body-frame forward/right
velocity to local NED using PX4 yaw, streams velocity setpoints through direct
MAVLink, and lands by default when finished.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
from dotenv import load_dotenv

try:
    from pymavlink import mavutil
except ImportError as exc:  # pragma: no cover - user validates in .venv
    raise SystemExit(
        "Missing dependency: pymavlink. Install requirements before running:\n"
        "python -m pip install -r requirements.txt"
    ) from exc

from src.control.airsim_vision import capture_scene_bgr, connect_airsim_vehicle
from src.control.control_config import ControlConfig
from src.control.visual_servo_controller import BodyVelocityCommand, VisualServoController
from src.experiments.phase05_config import (
    load_phase05_config,
    phase05_logging_paths,
    resolve_project_path,
    trial_metadata_from_args,
)
from src.logging.experiment_logger import Phase04CsvLogger, build_run_id
from src.logging.phase05_logger import Phase05CsvLogger
from src.perception.detector_factory import active_detector_name, build_marker_detector
from src.perception.landing_marker_detector import DetectionResult


def _mask_constant(name: str, fallback: int) -> int:
    return int(getattr(mavutil.mavlink, name, fallback))


VELOCITY_ONLY_TYPE_MASK = (
    _mask_constant("POSITION_TARGET_TYPEMASK_X_IGNORE", 1)
    | _mask_constant("POSITION_TARGET_TYPEMASK_Y_IGNORE", 2)
    | _mask_constant("POSITION_TARGET_TYPEMASK_Z_IGNORE", 4)
    | _mask_constant("POSITION_TARGET_TYPEMASK_AX_IGNORE", 64)
    | _mask_constant("POSITION_TARGET_TYPEMASK_AY_IGNORE", 128)
    | _mask_constant("POSITION_TARGET_TYPEMASK_AZ_IGNORE", 256)
    | _mask_constant("POSITION_TARGET_TYPEMASK_YAW_IGNORE", 1024)
    | _mask_constant("POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE", 2048)
)


def run_visual_servo_test(args: argparse.Namespace) -> Path | None:
    if not args.confirm_send:
        print("Safety stop: this script sends active MAVLink OFFBOARD setpoints.")
        print("Re-run with --confirm-send only after dry-run signs and hover are validated.")
        return None

    load_dotenv(PROJECT_ROOT / "configs" / "px4_airsim.env")
    connection_string = args.connection or os.getenv(
        "PX4_MAVLINK_DIRECT_ADDRESS",
        "udpin:0.0.0.0:14601",
    )
    config = ControlConfig.from_json()
    phase_label = getattr(args, "phase_label", "fase04")
    treatment_label = getattr(args, "treatment_label", "pilot")
    run_id_prefix = getattr(args, "run_id_prefix", None) or config.logging.run_id_prefix
    logs_dir = config.logging.logs_dir
    figures_root = config.logging.figures_dir
    trial_metadata: dict[str, object] = {}
    logger_class = Phase04CsvLogger
    if phase_label == "fase05":
        phase05_config = load_phase05_config()
        phase05_paths = phase05_logging_paths(phase05_config)
        run_id_prefix = getattr(args, "run_id_prefix", None) or phase05_config.get(
            "logging", {}
        ).get("run_id_prefix", "phase05")
        logs_dir = phase05_paths["raw_logs_dir"]
        figures_root = phase05_paths["figures_dir"]
        trial_metadata = trial_metadata_from_args(args, phase05_config)
        logger_class = Phase05CsvLogger
    if getattr(args, "logs_dir", None):
        logs_dir = resolve_project_path(args.logs_dir)
    if getattr(args, "figures_dir", None):
        figures_root = resolve_project_path(args.figures_dir)
    environment = args.environment or config.airsim.environment
    camera_name = args.camera_name or config.airsim.camera_name
    selected_detector = (args.detector or active_detector_name()).strip().lower()
    detector = build_marker_detector(environment, selected_detector)
    controller = VisualServoController(config.visual_servo, config.offboard)

    run_id = build_run_id(str(run_id_prefix))
    output_path = logs_dir / f"{run_id}_mavlink_visual_servo.csv"
    figures_dir = figures_root / "visual_servo_active" / run_id
    scenario_id = args.scenario_id or "P04_V07_MAVLINK_VISUAL_SERVO_LATERAL"

    print(f"Connecting with pymavlink on {connection_string} ...")
    print("Do not run this at the same time as MAVSDK on the same UDP port.")
    master = mavutil.mavlink_connection(connection_string)
    heartbeat = master.wait_heartbeat(timeout=args.timeout)
    if heartbeat is None:
        raise RuntimeError("No MAVLink heartbeat received.")

    target_system = master.target_system
    target_component = master.target_component
    mode, heartbeat_note, px4_main_mode = describe_heartbeat(heartbeat)
    local_position = wait_local_position(master, args.timeout)
    if local_position is None:
        raise RuntimeError("No LOCAL_POSITION_NED received.")
    yaw_rad = wait_attitude_yaw(master, args.timeout)
    if yaw_rad is None:
        raise RuntimeError("No ATTITUDE yaw received.")

    x, y, z, vx, vy, vz = local_position
    altitude_m = max(0.0, -z)
    armed = heartbeat_is_armed(heartbeat)

    print(
        "Initial MAVLink state: "
        f"mode={mode}, armed={armed}, altitude={altitude_m:.2f} m, "
        f"yaw={math.degrees(yaw_rad):.1f} deg, {heartbeat_note}"
    )
    print(f"Detector: {selected_detector}")
    print(f"Scenario ID: {scenario_id}")
    print(f"Log: {output_path}")

    if not armed:
        raise RuntimeError("Safety stop: vehicle is not armed; take off first.")
    if altitude_m < args.min_altitude:
        raise RuntimeError(
            "Safety stop: vehicle altitude is below visual-servo minimum: "
            f"altitude={altitude_m:.2f} m, min={args.min_altitude:.2f} m"
        )

    airsim_client = connect_airsim_vehicle(config.airsim.vehicle_name)
    hold_z = z
    control_period = args.control_period or config.offboard.control_period_seconds
    setpoint_period = min(args.setpoint_period, control_period)
    max_missing = args.max_missing_detections
    if max_missing is None:
        max_missing = config.visual_servo.max_missing_detections
    control_period = max(0.05, float(control_period))
    setpoint_period = max(0.02, float(setpoint_period))

    start_wall = time.time()
    sample_idx = 0
    command_ack = "command_ack=none"
    latest_mode = mode
    latest_heartbeat_note = heartbeat_note
    latest_px4_main_mode = px4_main_mode
    latest_position = local_position
    latest_yaw_rad = yaw_rad
    latest_command = BodyVelocityCommand.hover(reason="precheck")
    missing_detections = 0
    first_abs_error_x: float | None = None
    last_abs_error_x: float | None = None
    accepted_count = 0
    aborted = False
    centered_cycles = 0
    descent_started = False
    descent_started_once = False
    descent_command_count = 0
    landing_threshold_reached = False
    first_visual_altitude_m: float | None = None
    last_visual_altitude_m: float | None = None
    min_visual_altitude_m: float | None = None
    centered_cycles_required = args.centered_cycles_required or config.landing.centered_cycles_required
    centered_cycles_required = max(1, int(centered_cycles_required))
    descent_rate_m_s = args.descent_rate
    if descent_rate_m_s is None:
        descent_rate_m_s = config.landing.descent_rate_m_s
    descent_rate_m_s = clamp(float(descent_rate_m_s), 0.0, config.offboard.max_down_m_s)
    landing_complete_altitude_m = args.landing_complete_altitude
    if landing_complete_altitude_m is None:
        landing_complete_altitude_m = config.landing.landing_complete_altitude_m
    landing_complete_altitude_m = max(0.0, float(landing_complete_altitude_m))
    if args.enable_descent and descent_rate_m_s <= 0.0:
        raise RuntimeError("Safety stop: --enable-descent requires descent_rate_m_s > 0.")
    if args.enable_descent and landing_complete_altitude_m >= altitude_m:
        raise RuntimeError(
            "Safety stop: landing_complete_altitude must be below current altitude: "
            f"threshold={landing_complete_altitude_m:.2f} m, altitude={altitude_m:.2f} m"
        )
    controller_phase = "mavlink_visual_landing" if args.enable_descent else "mavlink_visual_servo"

    with logger_class(output_path) as logger:
        def log_row(row_extra: dict[str, object] | None = None, **kwargs) -> None:
            extra_fields = dict(trial_metadata)
            if row_extra:
                extra_fields.update(row_extra)
            write_row(
                phase_label=phase_label,
                treatment_label=treatment_label,
                extra_fields=extra_fields,
                **kwargs,
            )

        try:
            log_row(
                row_extra=spatial_error_row(
                    airsim_client,
                    config.airsim.vehicle_name,
                    getattr(args, "marker_object_name", None),
                ),
                logger=logger,
                run_id=run_id,
                scenario_id=scenario_id,
                sample_idx=sample_idx,
                start_wall=start_wall,
                event="precheck",
                controller_phase=controller_phase,
                command=latest_command,
                detection=None,
                flight_mode=latest_mode,
                armed=armed,
                position=latest_position,
                status="ok",
                command_sent=False,
                latency_ms=None,
                notes=(
                    f"initial_z={hold_z:.3f}; yaw_rad={latest_yaw_rad:.4f}; "
                    f"max_horizontal_speed={args.max_horizontal_speed:.3f}; "
                    f"enable_descent={args.enable_descent}; "
                    f"descent_rate_m_s={descent_rate_m_s:.3f}; "
                    f"centered_cycles_required={centered_cycles_required}; "
                    f"landing_complete_altitude_m={landing_complete_altitude_m:.3f}; "
                    f"{latest_heartbeat_note}"
                ),
            )
            sample_idx += 1

            prime_velocity_setpoints(
                master,
                target_system,
                target_component,
                hold_z,
                args.prime_seconds,
                setpoint_period,
            )
            request_note = request_px4_mode(master, "OFFBOARD")
            command_ack, heartbeat = stream_until_offboard(
                master,
                target_system,
                target_component,
                hold_z,
                args.mode_timeout,
                setpoint_period,
            )
            if heartbeat is None:
                heartbeat = wait_heartbeat(master, args.heartbeat_grace)
            latest_mode, latest_heartbeat_note, latest_px4_main_mode = describe_heartbeat(
                heartbeat
            )
            latest_position = wait_local_position(master, 0.5) or latest_position
            latest_yaw_rad = wait_attitude_yaw(master, 0.5) or latest_yaw_rad
            status = "ok" if latest_mode == "OFFBOARD" or latest_px4_main_mode == 6 else "error"

            log_row(
                logger=logger,
                run_id=run_id,
                scenario_id=scenario_id,
                sample_idx=sample_idx,
                start_wall=start_wall,
                event="offboard_start",
                controller_phase=controller_phase,
                command=latest_command,
                detection=None,
                flight_mode=latest_mode,
                armed=heartbeat_is_armed(heartbeat) if heartbeat else armed,
                position=latest_position,
                status=status,
                command_sent=True,
                latency_ms=None,
                notes=f"{request_note}; {command_ack}; {latest_heartbeat_note}",
            )
            print(
                f"[{sample_idx}] offboard_start mode={latest_mode} "
                f"status={status} {command_ack}"
            )
            sample_idx += 1
            if status != "ok":
                raise RuntimeError(
                    "OFFBOARD was not confirmed by heartbeat after accepted setpoints."
                )

            deadline = time.time() + args.duration
            next_control_time = time.time()
            while time.time() < deadline:
                if time.time() >= next_control_time:
                    cycle_start = time.perf_counter()
                    image_bgr = capture_scene_bgr(
                        airsim_client,
                        config.airsim.vehicle_name,
                        camera_name,
                    )
                    detection = detector.detect(image_bgr)
                    command = controller.command_from_detection(detection)
                    command = limit_horizontal_command(command, args.max_horizontal_speed)

                    if command.accepted_detection:
                        missing_detections = 0
                        accepted_count += 1
                        abs_error_x = abs(float(detection.error_x_norm or 0.0))
                        if first_abs_error_x is None:
                            first_abs_error_x = abs_error_x
                        last_abs_error_x = abs_error_x
                        if command.centered:
                            centered_cycles += 1
                        else:
                            centered_cycles = 0
                            descent_started = False
                    else:
                        missing_detections += 1
                        command = BodyVelocityCommand.hover(reason=command.reason)
                        centered_cycles = 0
                        descent_started = False

                    if args.save_annotated:
                        figures_dir.mkdir(parents=True, exist_ok=True)
                        annotated = detector.annotate(image_bgr, detection)
                        cv2.imwrite(str(figures_dir / f"{sample_idx:04d}_annotated.png"), annotated)

                    heartbeat, latest_position, latest_yaw_rad = drain_state_messages(
                        master,
                        heartbeat,
                        latest_position,
                        latest_yaw_rad,
                    )
                    latest_mode, latest_heartbeat_note, latest_px4_main_mode = describe_heartbeat(
                        heartbeat
                    )
                    status = (
                        "ok"
                        if latest_mode == "OFFBOARD" or latest_px4_main_mode == 6
                        else "warning"
                    )
                    altitude = max(0.0, -latest_position[2])
                    if first_visual_altitude_m is None:
                        first_visual_altitude_m = altitude
                    last_visual_altitude_m = altitude
                    min_visual_altitude_m = (
                        altitude
                        if min_visual_altitude_m is None
                        else min(min_visual_altitude_m, altitude)
                    )
                    if missing_detections > max_missing:
                        status = "abort"
                        aborted = True
                        command = BodyVelocityCommand.hover(
                            reason=f"marker_missing_limit:{missing_detections}>{max_missing}"
                        )
                    elif args.enable_descent and command.accepted_detection:
                        if command.centered and centered_cycles >= centered_cycles_required:
                            descent_started = True
                        if descent_started and command.centered:
                            descent_started_once = True
                            command = with_down_command(
                                command,
                                descent_rate_m_s,
                                "vision_descent",
                            )
                        else:
                            command = with_down_command(command, 0.0, "align")

                    latest_command = command
                    if latest_command.down_m_s > 0.0:
                        descent_command_count += 1
                    latency_ms = (time.perf_counter() - cycle_start) * 1000.0
                    local_vn, local_ve, local_vd = body_to_local_ned(
                        latest_command.forward_m_s,
                        latest_command.right_m_s,
                        latest_command.down_m_s,
                        latest_yaw_rad,
                    )
                    send_velocity_setpoint(
                        master,
                        target_system,
                        target_component,
                        hold_z,
                        local_vn,
                        local_ve,
                        local_vd,
                    )

                    if (
                        args.enable_descent
                        and not aborted
                        and altitude <= landing_complete_altitude_m
                    ):
                        status = "landing_ready"
                        landing_threshold_reached = True

                    log_row(
                        logger=logger,
                        run_id=run_id,
                        scenario_id=scenario_id,
                        sample_idx=sample_idx,
                        start_wall=start_wall,
                        event="visual_servo",
                        controller_phase=controller_phase,
                        command=latest_command,
                        detection=detection,
                        flight_mode=latest_mode,
                        armed=heartbeat_is_armed(heartbeat) if heartbeat else armed,
                        position=latest_position,
                        status=status,
                        command_sent=True,
                        latency_ms=latency_ms,
                        notes=(
                            f"{command_ack}; local_velocity_ned="
                            f"({local_vn:.3f},{local_ve:.3f},{local_vd:.3f}); "
                            f"yaw_rad={latest_yaw_rad:.4f}; missing={missing_detections}; "
                            f"centered_cycles={centered_cycles}; "
                            f"descent_started={descent_started}; "
                            f"{latest_heartbeat_note}"
                        ),
                    )
                    print(
                        f"[{sample_idx}] visual_servo mode={latest_mode} alt={altitude:.2f} "
                        f"detected={detection.detected} centered={latest_command.centered} "
                        f"cmd(fwd={latest_command.forward_m_s:.3f}, "
                        f"right={latest_command.right_m_s:.3f}, "
                        f"down={latest_command.down_m_s:.3f}) status={status}"
                    )
                    sample_idx += 1
                    next_control_time += control_period
                    if aborted or landing_threshold_reached:
                        break

                local_vn, local_ve, local_vd = body_to_local_ned(
                    latest_command.forward_m_s,
                    latest_command.right_m_s,
                    latest_command.down_m_s,
                    latest_yaw_rad,
                )
                send_velocity_setpoint(
                    master,
                    target_system,
                    target_component,
                    hold_z,
                    local_vn,
                    local_ve,
                    local_vd,
                )
                heartbeat, latest_position, latest_yaw_rad = drain_state_messages(
                    master,
                    heartbeat,
                    latest_position,
                    latest_yaw_rad,
                )
                time.sleep(setpoint_period)

            summary_note = (
                f"accepted_count={accepted_count}; "
                f"first_abs_error_x={format_optional(first_abs_error_x)}; "
                f"last_abs_error_x={format_optional(last_abs_error_x)}; "
                f"reduced_abs_error_x={last_abs_error_x is not None and first_abs_error_x is not None and last_abs_error_x < first_abs_error_x}; "
                f"aborted={aborted}; "
                f"missing_detections={missing_detections}; "
                f"max_missing_detections={max_missing}; "
                f"enable_descent={args.enable_descent}; "
                f"descent_started={descent_started_once}; "
                f"descent_active_at_end={descent_started}; "
                f"descent_command_count={descent_command_count}; "
                f"landing_threshold_reached={landing_threshold_reached}; "
                f"centered_cycles={centered_cycles}; "
                f"first_visual_altitude_m={format_optional(first_visual_altitude_m)}; "
                f"last_visual_altitude_m={format_optional(last_visual_altitude_m)}; "
                f"min_visual_altitude_m={format_optional(min_visual_altitude_m)}"
            )
            summary_extra = spatial_error_row(
                airsim_client,
                config.airsim.vehicle_name,
                getattr(args, "marker_object_name", None),
            )
            summary_extra["landing_success"] = bool(landing_threshold_reached and not aborted)
            summary_extra["abort_reason"] = "marker_missing_or_controller_abort" if aborted else ""
            log_row(
                row_extra=summary_extra,
                logger=logger,
                run_id=run_id,
                scenario_id=scenario_id,
                sample_idx=sample_idx,
                start_wall=start_wall,
                event="summary",
                controller_phase=controller_phase,
                command=BodyVelocityCommand.hover(reason="summary"),
                detection=None,
                flight_mode=latest_mode,
                armed=heartbeat_is_armed(heartbeat) if heartbeat else armed,
                position=latest_position,
                status=(
                    "abort"
                    if aborted
                    else "landing_ready"
                    if landing_threshold_reached
                    else "ok"
                ),
                command_sent=False,
                latency_ms=None,
                notes=summary_note,
            )
            print(f"[{sample_idx}] summary {summary_note}")
            sample_idx += 1

        except Exception as exc:
            latest_position = wait_local_position(master, 0.5) or latest_position
            heartbeat = wait_heartbeat(master, 0.5) or heartbeat
            latest_yaw_rad = wait_attitude_yaw(master, 0.5) or latest_yaw_rad
            latest_mode, latest_heartbeat_note, _ = describe_heartbeat(heartbeat)
            error_extra = spatial_error_row(
                airsim_client,
                config.airsim.vehicle_name,
                getattr(args, "marker_object_name", None),
            )
            error_extra["landing_success"] = False
            error_extra["abort_reason"] = f"{type(exc).__name__}: {exc}"
            log_row(
                row_extra=error_extra,
                logger=logger,
                run_id=run_id,
                scenario_id=scenario_id,
                sample_idx=sample_idx,
                start_wall=start_wall,
                event="error",
                controller_phase=controller_phase,
                command=BodyVelocityCommand.hover(reason="error"),
                detection=None,
                flight_mode=latest_mode,
                armed=heartbeat_is_armed(heartbeat) if heartbeat else armed,
                position=latest_position,
                status="error",
                command_sent=False,
                latency_ms=None,
                notes=f"{type(exc).__name__}: {exc}; {latest_heartbeat_note}",
            )
            print(f"Error: {exc}")
            sample_idx += 1

        finally:
            if not args.no_land_after:
                land_note = request_px4_mode(master, "LAND")
                landing_deadline = time.time() + args.land_timeout
                next_land_log_time = time.time()
                recovery_note = ""
                while time.time() < landing_deadline:
                    heartbeat, latest_position, latest_yaw_rad = drain_state_messages(
                        master,
                        heartbeat,
                        latest_position,
                        latest_yaw_rad,
                    )
                    if time.time() >= next_land_log_time:
                        latest_mode, latest_heartbeat_note, _ = describe_heartbeat(heartbeat)
                        altitude = max(0.0, -latest_position[2])
                        print(
                            f"[{sample_idx}] landing_monitor mode={latest_mode} "
                            f"alt={altitude:.2f}"
                        )
                        log_row(
                            logger=logger,
                            run_id=run_id,
                            scenario_id=scenario_id,
                            sample_idx=sample_idx,
                            start_wall=start_wall,
                            event="land_monitor",
                            controller_phase=controller_phase,
                            command=BodyVelocityCommand.hover(reason="landing"),
                            detection=None,
                            flight_mode=latest_mode,
                            armed=heartbeat_is_armed(heartbeat) if heartbeat else armed,
                            position=latest_position,
                            status="landing",
                            command_sent=True,
                            latency_ms=None,
                            notes=f"{land_note}; {latest_heartbeat_note}",
                        )
                        sample_idx += 1
                        next_land_log_time += args.log_interval

                    altitude = max(0.0, -latest_position[2])
                    is_armed = heartbeat_is_armed(heartbeat) if heartbeat else armed
                    if altitude <= args.landed_altitude and not is_armed:
                        if not args.no_recover_after_land:
                            recovery_note = request_px4_mode(master, "LOITER")
                            time.sleep(0.5)
                            heartbeat = wait_heartbeat(master, 1.0) or heartbeat
                        break
                    time.sleep(setpoint_period)

                latest_mode, latest_heartbeat_note, _ = describe_heartbeat(heartbeat)
                latest_position = wait_local_position(master, 0.5) or latest_position
                final_extra = spatial_error_row(
                    airsim_client,
                    config.airsim.vehicle_name,
                    getattr(args, "marker_object_name", None),
                )
                final_extra["landing_success"] = bool(
                    landing_threshold_reached and not aborted
                )
                final_extra["abort_reason"] = (
                    "marker_missing_or_controller_abort" if aborted else ""
                )
                log_row(
                    row_extra=final_extra,
                    logger=logger,
                    run_id=run_id,
                    scenario_id=scenario_id,
                    sample_idx=sample_idx,
                    start_wall=start_wall,
                    event="land_complete",
                    controller_phase=controller_phase,
                    command=BodyVelocityCommand.hover(reason="land_complete"),
                    detection=None,
                    flight_mode=latest_mode,
                    armed=heartbeat_is_armed(heartbeat) if heartbeat else armed,
                    position=latest_position,
                    status="landing",
                    command_sent=True,
                    latency_ms=None,
                    notes=f"{land_note}; {recovery_note}; {latest_heartbeat_note}",
                )
                print(
                    f"[{sample_idx}] landing complete mode={latest_mode} "
                    f"{land_note} {recovery_note}"
                )

    return output_path


def limit_horizontal_command(
    command: BodyVelocityCommand,
    max_horizontal_speed: float,
) -> BodyVelocityCommand:
    limit = abs(float(max_horizontal_speed))
    return BodyVelocityCommand(
        forward_m_s=clamp(command.forward_m_s, -limit, limit),
        right_m_s=clamp(command.right_m_s, -limit, limit),
        down_m_s=0.0,
        yawspeed_deg_s=0.0,
        accepted_detection=command.accepted_detection,
        centered=command.centered,
        reason=command.reason,
    )


def with_down_command(
    command: BodyVelocityCommand,
    down_m_s: float,
    reason: str,
) -> BodyVelocityCommand:
    return BodyVelocityCommand(
        forward_m_s=command.forward_m_s,
        right_m_s=command.right_m_s,
        down_m_s=down_m_s,
        yawspeed_deg_s=command.yawspeed_deg_s,
        accepted_detection=command.accepted_detection,
        centered=command.centered,
        reason=reason,
    )


def body_to_local_ned(
    forward_m_s: float,
    right_m_s: float,
    down_m_s: float,
    yaw_rad: float,
) -> tuple[float, float, float]:
    cos_yaw = math.cos(yaw_rad)
    sin_yaw = math.sin(yaw_rad)
    north_m_s = forward_m_s * cos_yaw - right_m_s * sin_yaw
    east_m_s = forward_m_s * sin_yaw + right_m_s * cos_yaw
    return north_m_s, east_m_s, down_m_s


def send_velocity_setpoint(
    master,
    target_system: int,
    target_component: int,
    z: float,
    vx: float,
    vy: float,
    vz: float,
) -> None:
    master.mav.set_position_target_local_ned_send(
        int(time.time() * 1000) & 0xFFFFFFFF,
        target_system,
        target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        VELOCITY_ONLY_TYPE_MASK,
        0.0,
        0.0,
        z,
        vx,
        vy,
        vz,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )


def prime_velocity_setpoints(
    master,
    target_system: int,
    target_component: int,
    hold_z: float,
    duration_s: float,
    period_s: float,
) -> None:
    deadline = time.time() + max(0.0, duration_s)
    while time.time() < deadline:
        send_velocity_setpoint(
            master,
            target_system,
            target_component,
            hold_z,
            0.0,
            0.0,
            0.0,
        )
        time.sleep(period_s)


def stream_until_offboard(
    master,
    target_system: int,
    target_component: int,
    hold_z: float,
    timeout_s: float,
    period_s: float,
) -> tuple[str, object | None]:
    ack_note = "command_ack=none"
    latest_heartbeat = None
    deadline = time.time() + max(0.0, timeout_s)
    while time.time() < deadline:
        send_velocity_setpoint(
            master,
            target_system,
            target_component,
            hold_z,
            0.0,
            0.0,
            0.0,
        )
        while True:
            message = master.recv_match(type=["COMMAND_ACK", "HEARTBEAT"], blocking=False)
            if message is None:
                break
            if message.get_type() == "COMMAND_ACK" and ack_note == "command_ack=none":
                ack_note = describe_command_ack(message)
            elif message.get_type() == "HEARTBEAT":
                latest_heartbeat = message
                _, _, px4_main_mode = describe_heartbeat(message)
                if px4_main_mode == 6:
                    return ack_note, latest_heartbeat
        time.sleep(period_s)
    return ack_note, latest_heartbeat


def wait_local_position(master, timeout: float) -> tuple[float, float, float, float, float, float] | None:
    message = master.recv_match(type="LOCAL_POSITION_NED", blocking=True, timeout=timeout)
    if message is None:
        return None
    return local_position_from_message(message)


def wait_heartbeat(master, timeout: float):
    return master.recv_match(type="HEARTBEAT", blocking=True, timeout=timeout)


def wait_attitude_yaw(master, timeout: float) -> float | None:
    message = master.recv_match(type="ATTITUDE", blocking=True, timeout=timeout)
    if message is None:
        return None
    return float(message.yaw)


def local_position_from_message(message) -> tuple[float, float, float, float, float, float]:
    return (
        float(message.x),
        float(message.y),
        float(message.z),
        float(message.vx),
        float(message.vy),
        float(message.vz),
    )


def heartbeat_is_armed(heartbeat) -> bool:
    if heartbeat is None:
        return False
    return bool(int(getattr(heartbeat, "base_mode", 0)) & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)


def describe_heartbeat(heartbeat) -> tuple[str, str, int | None]:
    if heartbeat is None:
        return "", "heartbeat=none", None
    mode = mavutil.mode_string_v10(heartbeat)
    base_mode = int(getattr(heartbeat, "base_mode", 0))
    custom_mode = int(getattr(heartbeat, "custom_mode", 0))
    px4_main_mode = (custom_mode & 0xFF0000) >> 16
    px4_sub_mode = (custom_mode & 0xFF000000) >> 24
    if px4_main_mode == 6:
        mode = "OFFBOARD"
    note = (
        "heartbeat="
        f"base_mode={base_mode},custom_mode={custom_mode},"
        f"px4_main_mode={px4_main_mode},px4_sub_mode={px4_sub_mode}"
    )
    return mode, note, px4_main_mode


def request_px4_mode(master, mode_name: str) -> str:
    mode_mapping = master.mode_mapping()
    if mode_mapping is None or mode_name not in mode_mapping:
        return f"{mode_name.lower()}_mode_mapping_missing"
    base_mode, custom_mode, custom_sub_mode = mode_mapping[mode_name]
    master.set_mode(base_mode, custom_mode, custom_sub_mode)
    return (
        f"requested_{mode_name}_px4_mode="
        f"base={base_mode},custom={custom_mode},sub={custom_sub_mode}"
    )


def describe_command_ack(ack) -> str:
    command_name = mavutil.mavlink.enums["MAV_CMD"].get(ack.command)
    result_name = mavutil.mavlink.enums["MAV_RESULT"].get(ack.result)
    command_label = command_name.name if command_name else str(ack.command)
    result_label = result_name.name if result_name else str(ack.result)
    return f"command_ack={command_label}:{result_label}"


def drain_state_messages(master, heartbeat, position, yaw_rad: float):
    while True:
        message = master.recv_match(
            type=["LOCAL_POSITION_NED", "HEARTBEAT", "ATTITUDE"],
            blocking=False,
        )
        if message is None:
            break
        if message.get_type() == "LOCAL_POSITION_NED":
            position = local_position_from_message(message)
        elif message.get_type() == "HEARTBEAT":
            heartbeat = message
        elif message.get_type() == "ATTITUDE":
            yaw_rad = float(message.yaw)
    return heartbeat, position, yaw_rad


def write_row(
    logger,
    run_id: str,
    scenario_id: str,
    sample_idx: int,
    start_wall: float,
    event: str,
    controller_phase: str,
    command: BodyVelocityCommand,
    detection: DetectionResult | None,
    flight_mode: str,
    armed: bool,
    position: tuple[float, float, float, float, float, float],
    status: str,
    command_sent: bool,
    latency_ms: float | None,
    notes: str,
    phase_label: str = "fase04",
    treatment_label: str = "pilot",
    extra_fields: dict[str, object] | None = None,
) -> None:
    x, y, z, vx, vy, vz = position
    row = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "phase": phase_label,
            "treatment": treatment_label,
            "scenario_id": scenario_id,
            "sample_idx": sample_idx,
            "elapsed_seconds": f"{time.time() - start_wall:.3f}",
            "controller_phase": controller_phase,
            "controller_reason": command.reason,
            "event": event,
            "detector_method": detection.method if detection else "",
            "detected": detection.detected if detection else "",
            "accepted_detection": command.accepted_detection,
            "centered": command.centered,
            "confidence": detection.confidence if detection else "",
            "error_x_norm": detection.error_x_norm if detection else "",
            "error_y_norm": detection.error_y_norm if detection else "",
            "error_x_px": detection.error_x_px if detection else "",
            "error_y_px": detection.error_y_px if detection else "",
            "command_forward_m_s": command.forward_m_s,
            "command_right_m_s": command.right_m_s,
            "command_down_m_s": command.down_m_s,
            "command_yawspeed_deg_s": command.yawspeed_deg_s,
            "command_sent": command_sent,
            "armed": armed,
            "flight_mode": flight_mode,
            "north_m": x,
            "east_m": y,
            "down_m": z,
            "altitude_m": max(0.0, -z),
            "velocity_north_m_s": vx,
            "velocity_east_m_s": vy,
            "velocity_down_m_s": vz,
            "latency_ms": f"{latency_ms:.2f}" if latency_ms is not None else "",
            "status": status,
            "detection_notes": detection.notes if detection else "",
            "notes": notes,
        }
    if extra_fields:
        row.update(extra_fields)
    logger.write(row)


def spatial_error_row(airsim_client, vehicle_name: str, marker_object_name: str | None) -> dict[str, object]:
    if not marker_object_name:
        return {}
    try:
        vehicle_pose = airsim_client.simGetVehiclePose(vehicle_name=vehicle_name)
        marker_pose = airsim_client.simGetObjectPose(marker_object_name)
    except Exception as exc:
        return {"abort_reason": f"spatial_error_unavailable:{type(exc).__name__}"}

    vehicle_position = vehicle_pose.position
    marker_position = marker_pose.position
    coordinates = [
        float(vehicle_position.x_val),
        float(vehicle_position.y_val),
        float(vehicle_position.z_val),
        float(marker_position.x_val),
        float(marker_position.y_val),
        float(marker_position.z_val),
    ]
    if any(math.isnan(value) for value in coordinates):
        return {"abort_reason": "spatial_error_unavailable:nan_pose"}
    error_x = float(vehicle_position.x_val) - float(marker_position.x_val)
    error_y = float(vehicle_position.y_val) - float(marker_position.y_val)
    return {
        "airsim_position_x": float(vehicle_position.x_val),
        "airsim_position_y": float(vehicle_position.y_val),
        "airsim_position_z": float(vehicle_position.z_val),
        "marker_object_name": marker_object_name,
        "marker_x_m": float(marker_position.x_val),
        "marker_y_m": float(marker_position.y_val),
        "marker_z_m": float(marker_position.z_val),
        "final_error_x_m": error_x,
        "final_error_y_m": error_y,
        "final_error_m": math.hypot(error_x, error_y),
    }


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def format_optional(value: float | None) -> str:
    return "" if value is None else f"{value:.4f}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Active MAVLink visual-servo correction test.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument("--connection", default=None)
    parser.add_argument("--environment", default=None, choices=["Blocks", "AirSimNH"])
    parser.add_argument("--camera-name", default=None)
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--prime-seconds", type=float, default=2.0)
    parser.add_argument("--mode-timeout", type=float, default=5.0)
    parser.add_argument("--heartbeat-grace", type=float, default=2.0)
    parser.add_argument("--setpoint-period", type=float, default=0.05)
    parser.add_argument("--control-period", type=float, default=None)
    parser.add_argument("--log-interval", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--min-altitude", type=float, default=0.8)
    parser.add_argument("--max-horizontal-speed", type=float, default=0.12)
    parser.add_argument("--max-missing-detections", type=int, default=None)
    parser.add_argument("--enable-descent", action="store_true")
    parser.add_argument("--descent-rate", type=float, default=None)
    parser.add_argument("--centered-cycles-required", type=int, default=None)
    parser.add_argument("--landing-complete-altitude", type=float, default=None)
    parser.add_argument("--land-timeout", type=float, default=20.0)
    parser.add_argument("--landed-altitude", type=float, default=0.25)
    parser.add_argument("--no-land-after", action="store_true")
    parser.add_argument("--no-recover-after-land", action="store_true")
    parser.add_argument("--save-annotated", action="store_true")
    parser.add_argument("--scenario-id", default=None)
    parser.add_argument("--marker-object-name", default=None)
    parser.add_argument("--treatment-pair-id", default=None)
    parser.add_argument("--repetition", type=int, default=None)
    parser.add_argument("--planned-initial-height-m", type=float, default=None)
    parser.add_argument("--planned-offset-x-m", type=float, default=None)
    parser.add_argument("--planned-offset-y-m", type=float, default=None)
    parser.add_argument("--planned-yaw-deg", type=float, default=None)
    parser.add_argument("--logs-dir", default=None)
    parser.add_argument("--figures-dir", default=None)
    parser.add_argument(
        "--detector",
        choices=["hsv", "hsv_color_contour", "aruco", "aruco_fiducial", "fiducial"],
        default="aruco",
        help="Perception backend. Use aruco for the Phase 04 fiducial marker.",
    )
    return parser.parse_args()


def main() -> None:
    run_visual_servo_test(parse_args())


if __name__ == "__main__":
    main()
