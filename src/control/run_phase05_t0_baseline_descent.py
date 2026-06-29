"""Phase 05 T0 baseline descent without visual correction.

This script assumes the vehicle is already airborne. It does not arm and does
not take off. It streams direct MAVLink OFFBOARD velocity setpoints with zero
forward/right velocity and a fixed positive-down velocity. The bottom-camera
detector may run passively for metrics, but its output is never used to correct
the vehicle.
"""
from __future__ import annotations

import argparse
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
from src.control.run_mavlink_visual_servo_test import (
    BodyVelocityCommand,
    clamp,
    describe_heartbeat,
    drain_state_messages,
    heartbeat_is_armed,
    prime_velocity_setpoints,
    request_px4_mode,
    send_velocity_setpoint,
    spatial_error_row,
    stream_until_offboard,
    wait_attitude_yaw,
    wait_heartbeat,
    wait_local_position,
)
from src.experiments.phase05_config import (
    load_phase05_config,
    phase05_logging_paths,
    resolve_project_path,
    trial_metadata_from_args,
)
from src.logging.experiment_logger import build_run_id
from src.logging.phase05_logger import Phase05CsvLogger
from src.perception.detector_factory import build_marker_detector
from src.perception.landing_marker_detector import DetectionResult


def run_baseline_descent(args: argparse.Namespace) -> Path | None:
    if not args.confirm_send:
        print("Safety stop: this script sends active MAVLink OFFBOARD setpoints.")
        print("Re-run with --confirm-send only after PX4 takeoff and marker setup.")
        return None

    load_dotenv(PROJECT_ROOT / "configs" / "px4_airsim.env")
    connection_string = args.connection or os.getenv(
        "PX4_MAVLINK_DIRECT_ADDRESS",
        "udpin:0.0.0.0:14601",
    )
    control_config = ControlConfig.from_json()
    phase05_config = load_phase05_config()
    phase05_paths = phase05_logging_paths(phase05_config)
    raw_logs_dir = resolve_project_path(args.logs_dir) if args.logs_dir else phase05_paths["raw_logs_dir"]
    figures_root = (
        resolve_project_path(args.figures_dir)
        if args.figures_dir
        else phase05_paths["figures_dir"]
    )
    trial_metadata = trial_metadata_from_args(args, phase05_config)

    environment = args.environment or control_config.airsim.environment
    camera_name = args.camera_name or control_config.airsim.camera_name
    detector = build_marker_detector(environment, args.detector)
    run_id = build_run_id("phase05")
    scenario_id = args.scenario_id or "P05_PILOT_T0_BASELINE_DESCENT"
    output_path = raw_logs_dir / f"{run_id}_baseline_descent.csv"
    figures_dir = figures_root / "baseline_descent" / run_id

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
    if not armed:
        raise RuntimeError("Safety stop: vehicle is not armed; take off first.")
    if altitude_m < args.min_altitude:
        raise RuntimeError(
            "Safety stop: vehicle altitude is below baseline minimum: "
            f"altitude={altitude_m:.2f} m, min={args.min_altitude:.2f} m"
        )

    descent_rate_m_s = clamp(
        float(args.descent_rate),
        0.0,
        control_config.offboard.max_down_m_s,
    )
    if descent_rate_m_s <= 0.0:
        raise RuntimeError("Safety stop: T0 descent_rate must be greater than 0.")
    landing_complete_altitude_m = float(args.landing_complete_altitude)
    if landing_complete_altitude_m >= altitude_m:
        raise RuntimeError(
            "Safety stop: landing_complete_altitude must be below current altitude: "
            f"threshold={landing_complete_altitude_m:.2f} m, altitude={altitude_m:.2f} m"
        )

    airsim_client = connect_airsim_vehicle(control_config.airsim.vehicle_name)
    hold_z = z
    control_period = args.control_period or control_config.offboard.control_period_seconds
    setpoint_period = min(args.setpoint_period, control_period)
    control_period = max(0.05, float(control_period))
    setpoint_period = max(0.02, float(setpoint_period))

    start_wall = time.time()
    sample_idx = 0
    latest_mode = mode
    latest_heartbeat_note = heartbeat_note
    latest_px4_main_mode = px4_main_mode
    latest_position = local_position
    latest_yaw_rad = yaw_rad
    accepted_count = 0
    missing_detections = 0
    descent_command_count = 0
    landing_threshold_reached = False
    aborted = False
    command_ack = "command_ack=none"

    print(
        "Initial MAVLink state: "
        f"mode={mode}, armed={armed}, altitude={altitude_m:.2f} m, "
        f"yaw={latest_yaw_rad:.3f} rad, {heartbeat_note}"
    )
    print(f"Scenario ID: {scenario_id}")
    print(f"Log: {output_path}")

    with Phase05CsvLogger(output_path) as logger:
        def log_row(
            event: str,
            command: BodyVelocityCommand,
            detection: DetectionResult | None,
            status: str,
            command_sent: bool,
            latency_ms: float | None,
            notes: str,
            row_extra: dict[str, object] | None = None,
        ) -> None:
            extra_fields = dict(trial_metadata)
            if row_extra:
                extra_fields.update(row_extra)
            write_row(
                logger=logger,
                run_id=run_id,
                scenario_id=scenario_id,
                sample_idx=log_row.sample_idx,
                start_wall=start_wall,
                event=event,
                command=command,
                detection=detection,
                flight_mode=latest_mode,
                armed=heartbeat_is_armed(heartbeat) if heartbeat else armed,
                position=latest_position,
                status=status,
                command_sent=command_sent,
                latency_ms=latency_ms,
                notes=notes,
                extra_fields=extra_fields,
            )
            log_row.sample_idx += 1

        log_row.sample_idx = sample_idx  # type: ignore[attr-defined]

        try:
            log_row(
                event="precheck",
                command=BodyVelocityCommand.hover(reason="precheck"),
                detection=None,
                status="ok",
                command_sent=False,
                latency_ms=None,
                notes=(
                    f"baseline_no_visual_correction=True; "
                    f"descent_rate_m_s={descent_rate_m_s:.3f}; "
                    f"landing_complete_altitude_m={landing_complete_altitude_m:.3f}; "
                    f"{latest_heartbeat_note}"
                ),
                row_extra=spatial_error_row(
                    airsim_client,
                    control_config.airsim.vehicle_name,
                    args.marker_object_name,
                ),
            )

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
            latest_mode, latest_heartbeat_note, latest_px4_main_mode = describe_heartbeat(heartbeat)
            latest_position = wait_local_position(master, 0.5) or latest_position
            latest_yaw_rad = wait_attitude_yaw(master, 0.5) or latest_yaw_rad
            status = "ok" if latest_mode == "OFFBOARD" or latest_px4_main_mode == 6 else "error"
            log_row(
                event="offboard_start",
                command=BodyVelocityCommand.hover(reason="baseline_prime"),
                detection=None,
                status=status,
                command_sent=True,
                latency_ms=None,
                notes=f"{request_note}; {command_ack}; {latest_heartbeat_note}",
            )
            print(f"[{log_row.sample_idx - 1}] offboard_start mode={latest_mode} status={status}")
            if status != "ok":
                raise RuntimeError("OFFBOARD was not confirmed by heartbeat.")

            deadline = time.time() + args.duration
            next_control_time = time.time()
            while time.time() < deadline:
                if time.time() >= next_control_time:
                    cycle_start = time.perf_counter()
                    image_bgr = capture_scene_bgr(
                        airsim_client,
                        control_config.airsim.vehicle_name,
                        camera_name,
                    )
                    detection = detector.detect(image_bgr)
                    if detection.detected:
                        accepted_count += 1
                        missing_detections = 0
                    else:
                        missing_detections += 1

                    if args.save_annotated:
                        figures_dir.mkdir(parents=True, exist_ok=True)
                        annotated = detector.annotate(image_bgr, detection)
                        cv2.imwrite(
                            str(figures_dir / f"{log_row.sample_idx:04d}_annotated.png"),
                            annotated,
                        )

                    heartbeat, latest_position, latest_yaw_rad = drain_state_messages(
                        master,
                        heartbeat,
                        latest_position,
                        latest_yaw_rad,
                    )
                    latest_mode, latest_heartbeat_note, latest_px4_main_mode = describe_heartbeat(
                        heartbeat
                    )
                    altitude = max(0.0, -latest_position[2])
                    status = (
                        "ok"
                        if latest_mode == "OFFBOARD" or latest_px4_main_mode == 6
                        else "warning"
                    )
                    if status == "warning":
                        aborted = True

                    command = BodyVelocityCommand(
                        forward_m_s=0.0,
                        right_m_s=0.0,
                        down_m_s=descent_rate_m_s,
                        yawspeed_deg_s=0.0,
                        accepted_detection=bool(detection.detected),
                        centered=is_passively_centered(detection, control_config.visual_servo.center_tolerance_norm),
                        reason="baseline_descent_no_visual_correction",
                    )
                    send_velocity_setpoint(
                        master,
                        target_system,
                        target_component,
                        hold_z,
                        0.0,
                        0.0,
                        descent_rate_m_s,
                    )
                    descent_command_count += 1
                    latency_ms = (time.perf_counter() - cycle_start) * 1000.0
                    if altitude <= landing_complete_altitude_m and not aborted:
                        status = "landing_ready"
                        landing_threshold_reached = True

                    log_row(
                        event="baseline_descent",
                        command=command,
                        detection=detection,
                        status=status,
                        command_sent=True,
                        latency_ms=latency_ms,
                        notes=(
                            f"{command_ack}; baseline_no_visual_correction=True; "
                            f"missing={missing_detections}; {latest_heartbeat_note}"
                        ),
                    )
                    print(
                        f"[{log_row.sample_idx - 1}] baseline_descent "
                        f"mode={latest_mode} alt={altitude:.2f} "
                        f"detected={detection.detected} down={descent_rate_m_s:.3f} "
                        f"status={status}"
                    )
                    next_control_time += control_period
                    if aborted or landing_threshold_reached:
                        break

                send_velocity_setpoint(
                    master,
                    target_system,
                    target_component,
                    hold_z,
                    0.0,
                    0.0,
                    descent_rate_m_s,
                )
                heartbeat, latest_position, latest_yaw_rad = drain_state_messages(
                    master,
                    heartbeat,
                    latest_position,
                    latest_yaw_rad,
                )
                time.sleep(setpoint_period)

            summary_extra = spatial_error_row(
                airsim_client,
                control_config.airsim.vehicle_name,
                args.marker_object_name,
            )
            summary_extra["landing_success"] = bool(landing_threshold_reached and not aborted)
            summary_extra["abort_reason"] = "offboard_lost" if aborted else ""
            log_row(
                event="summary",
                command=BodyVelocityCommand.hover(reason="summary"),
                detection=None,
                status="abort" if aborted else "landing_ready" if landing_threshold_reached else "ok",
                command_sent=False,
                latency_ms=None,
                notes=(
                    f"accepted_count={accepted_count}; "
                    f"missing_detections={missing_detections}; "
                    f"descent_command_count={descent_command_count}; "
                    f"landing_threshold_reached={landing_threshold_reached}; "
                    f"aborted={aborted}; baseline_no_visual_correction=True"
                ),
                row_extra=summary_extra,
            )

        except Exception as exc:
            latest_position = wait_local_position(master, 0.5) or latest_position
            heartbeat = wait_heartbeat(master, 0.5) or heartbeat
            latest_mode, latest_heartbeat_note, _ = describe_heartbeat(heartbeat)
            error_extra = spatial_error_row(
                airsim_client,
                control_config.airsim.vehicle_name,
                args.marker_object_name,
            )
            error_extra["landing_success"] = False
            error_extra["abort_reason"] = f"{type(exc).__name__}: {exc}"
            log_row(
                event="error",
                command=BodyVelocityCommand.hover(reason="error"),
                detection=None,
                status="error",
                command_sent=False,
                latency_ms=None,
                notes=f"{type(exc).__name__}: {exc}; {latest_heartbeat_note}",
                row_extra=error_extra,
            )
            print(f"Error: {exc}")

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
                        log_row(
                            event="land_monitor",
                            command=BodyVelocityCommand.hover(reason="landing"),
                            detection=None,
                            status="landing",
                            command_sent=True,
                            latency_ms=None,
                            notes=f"{land_note}; {latest_heartbeat_note}",
                        )
                        print(
                            f"[{log_row.sample_idx - 1}] landing_monitor "
                            f"mode={latest_mode} alt={altitude:.2f}"
                        )
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
                    control_config.airsim.vehicle_name,
                    args.marker_object_name,
                )
                final_extra["landing_success"] = bool(landing_threshold_reached and not aborted)
                final_extra["abort_reason"] = "offboard_lost" if aborted else ""
                log_row(
                    event="land_complete",
                    command=BodyVelocityCommand.hover(reason="land_complete"),
                    detection=None,
                    status="landing",
                    command_sent=True,
                    latency_ms=None,
                    notes=f"{land_note}; {recovery_note}; {latest_heartbeat_note}",
                    row_extra=final_extra,
                )
                print(
                    f"[{log_row.sample_idx - 1}] landing complete "
                    f"mode={latest_mode} {land_note} {recovery_note}"
                )

    return output_path


def is_passively_centered(detection: DetectionResult, tolerance_norm: float) -> bool:
    if not detection.detected:
        return False
    error_x = float(detection.error_x_norm or 0.0)
    error_y = float(detection.error_y_norm or 0.0)
    return abs(error_x) <= tolerance_norm and abs(error_y) <= tolerance_norm


def write_row(
    logger: Phase05CsvLogger,
    run_id: str,
    scenario_id: str,
    sample_idx: int,
    start_wall: float,
    event: str,
    command: BodyVelocityCommand,
    detection: DetectionResult | None,
    flight_mode: str,
    armed: bool,
    position: tuple[float, float, float, float, float, float],
    status: str,
    command_sent: bool,
    latency_ms: float | None,
    notes: str,
    extra_fields: dict[str, object] | None = None,
) -> None:
    x, y, z, vx, vy, vz = position
    row = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(timespec="milliseconds"),
        "phase": "fase05",
        "treatment": "T0",
        "scenario_id": scenario_id,
        "sample_idx": sample_idx,
        "elapsed_seconds": f"{time.time() - start_wall:.3f}",
        "controller_phase": "baseline_descent",
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


def parse_args() -> argparse.Namespace:
    frozen = load_phase05_config().get("frozen_t1", {})
    parser = argparse.ArgumentParser(description="Run Phase 05 T0 baseline descent.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument("--connection", default=None)
    parser.add_argument("--environment", default=None, choices=["Blocks", "AirSimNH"])
    parser.add_argument("--camera-name", default=None)
    parser.add_argument("--duration", type=float, default=25.0)
    parser.add_argument("--prime-seconds", type=float, default=2.0)
    parser.add_argument("--mode-timeout", type=float, default=5.0)
    parser.add_argument("--heartbeat-grace", type=float, default=2.0)
    parser.add_argument("--setpoint-period", type=float, default=0.05)
    parser.add_argument("--control-period", type=float, default=None)
    parser.add_argument("--log-interval", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--min-altitude", type=float, default=0.8)
    parser.add_argument("--descent-rate", type=float, default=float(frozen.get("descent_rate_m_s", 0.08)))
    parser.add_argument(
        "--landing-complete-altitude",
        type=float,
        default=float(frozen.get("landing_complete_altitude_m", 0.80)),
    )
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
    )
    return parser.parse_args()


def main() -> None:
    run_baseline_descent(parse_args())


if __name__ == "__main__":
    main()
