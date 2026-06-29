"""Minimal hover test using direct MAVLink Offboard setpoints.

This script assumes the vehicle is already airborne. It does not arm and does
not take off. It holds the current local NED position through direct MAVLink
setpoints, requests PX4 OFFBOARD, streams the hold setpoint for a short duration,
and then requests PX4 LAND by default.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

try:
    from pymavlink import mavutil
except ImportError as exc:  # pragma: no cover - user validates in .venv
    raise SystemExit(
        "Missing dependency: pymavlink. Install requirements before running:\n"
        "python -m pip install -r requirements.txt"
    ) from exc

from src.control.control_config import ControlConfig
from src.logging.experiment_logger import Phase04CsvLogger, build_run_id


POSITION_HOLD_TYPE_MASK = (
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_VX_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_VY_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_VZ_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_AX_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_AY_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_AZ_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_YAW_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE
)


def run_hover_test(args: argparse.Namespace) -> Path | None:
    if not args.confirm_send:
        print("Safety stop: this script sends MAVLink OFFBOARD setpoints.")
        print("Re-run with --confirm-send only after PX4 takeoff and stable hover.")
        return None

    load_dotenv(PROJECT_ROOT / "configs" / "px4_airsim.env")
    connection_string = args.connection or os.getenv(
        "PX4_MAVLINK_DIRECT_ADDRESS",
        "udpin:0.0.0.0:14601",
    )
    config = ControlConfig.from_json()
    run_id = build_run_id(config.logging.run_id_prefix)
    output_path = config.logging.logs_dir / f"{run_id}_mavlink_direct_hover.csv"

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

    x, y, z, vx, vy, vz = local_position
    altitude_m = max(0.0, -z)
    armed = heartbeat_is_armed(heartbeat)

    print(
        "Initial MAVLink state: "
        f"mode={mode}, armed={armed}, altitude={altitude_m:.2f} m, {heartbeat_note}"
    )
    print(f"Log: {output_path}")

    if not armed:
        raise RuntimeError("Safety stop: vehicle is not armed; take off first.")
    if altitude_m < args.min_altitude:
        raise RuntimeError(
            "Safety stop: vehicle altitude is below hover-test minimum: "
            f"altitude={altitude_m:.2f} m, min={args.min_altitude:.2f} m"
        )

    hold_x, hold_y, hold_z = x, y, z
    start_wall = time.time()
    sample_idx = 0
    command_ack = "command_ack=none"
    status = "diagnostic"
    latest_mode = mode
    latest_heartbeat_note = heartbeat_note
    latest_px4_main_mode = px4_main_mode
    latest_position = local_position

    with Phase04CsvLogger(output_path) as logger:
        try:
            write_row(
                logger,
                run_id,
                sample_idx,
                start_wall,
                "precheck",
                latest_mode,
                armed,
                latest_position,
                status="ok",
                notes=f"hold_setpoint=({hold_x:.3f},{hold_y:.3f},{hold_z:.3f}); {latest_heartbeat_note}",
            )
            sample_idx += 1

            prime_setpoints(
                master,
                target_system,
                target_component,
                hold_x,
                hold_y,
                hold_z,
                args.prime_seconds,
                args.period,
            )
            request_note = request_px4_mode(master, "OFFBOARD")
            command_ack, heartbeat = stream_until_mode(
                master,
                target_system,
                target_component,
                hold_x,
                hold_y,
                hold_z,
                args.mode_timeout,
                args.period,
                target_main_mode=6,
            )
            if heartbeat is None:
                heartbeat = wait_heartbeat(master, args.heartbeat_grace)
            latest_mode, latest_heartbeat_note, latest_px4_main_mode = describe_heartbeat(heartbeat)
            latest_position = wait_local_position(master, 0.5) or latest_position
            status = "ok" if latest_mode == "OFFBOARD" or latest_px4_main_mode == 6 else "error"

            write_row(
                logger,
                run_id,
                sample_idx,
                start_wall,
                "offboard_start",
                latest_mode,
                heartbeat_is_armed(heartbeat) if heartbeat else armed,
                latest_position,
                status=status,
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

            next_log_time = time.time()
            deadline = time.time() + args.duration
            while time.time() < deadline:
                send_position_hold_setpoint(
                    master,
                    target_system,
                    target_component,
                    hold_x,
                    hold_y,
                    hold_z,
                )
                heartbeat, latest_position = drain_state_messages(
                    master,
                    heartbeat,
                    latest_position,
                )

                if time.time() >= next_log_time:
                    latest_mode, latest_heartbeat_note, latest_px4_main_mode = describe_heartbeat(
                        heartbeat
                    )
                    status = (
                        "ok"
                        if latest_mode == "OFFBOARD" or latest_px4_main_mode == 6
                        else "warning"
                    )
                    write_row(
                        logger,
                        run_id,
                        sample_idx,
                        start_wall,
                        "hover",
                        latest_mode,
                        heartbeat_is_armed(heartbeat) if heartbeat else armed,
                        latest_position,
                        status=status,
                        notes=f"{command_ack}; {latest_heartbeat_note}",
                    )
                    altitude = max(0.0, -latest_position[2])
                    print(
                        f"[{sample_idx}] hover mode={latest_mode} "
                        f"alt={altitude:.2f} status={status}"
                    )
                    sample_idx += 1
                    next_log_time += args.log_interval

                time.sleep(args.period)

        except Exception as exc:
            latest_position = wait_local_position(master, 0.5) or latest_position
            heartbeat = wait_heartbeat(master, 0.5) or heartbeat
            latest_mode, latest_heartbeat_note, _ = describe_heartbeat(heartbeat)
            write_row(
                logger,
                run_id,
                sample_idx,
                start_wall,
                "error",
                latest_mode,
                heartbeat_is_armed(heartbeat) if heartbeat else armed,
                latest_position,
                status="error",
                notes=f"{type(exc).__name__}: {exc}; {latest_heartbeat_note}",
            )
            print(f"Error: {exc}")
            sample_idx += 1

        finally:
            if not args.no_land_after:
                land_note = request_land_mode(master)
                landing_deadline = time.time() + args.land_timeout
                next_land_log_time = time.time()
                recovery_note = ""
                while time.time() < landing_deadline:
                    heartbeat, latest_position = drain_state_messages(
                        master,
                        heartbeat,
                        latest_position,
                    )
                    if time.time() >= next_land_log_time:
                        latest_mode, latest_heartbeat_note, _ = describe_heartbeat(heartbeat)
                        altitude = max(0.0, -latest_position[2])
                        print(
                            f"[{sample_idx}] landing_monitor mode={latest_mode} "
                            f"alt={altitude:.2f}"
                        )
                        write_row(
                            logger,
                            run_id,
                            sample_idx,
                            start_wall,
                            "land_monitor",
                            latest_mode,
                            heartbeat_is_armed(heartbeat) if heartbeat else armed,
                            latest_position,
                            status="landing",
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
                    time.sleep(args.period)

                latest_mode, latest_heartbeat_note, _ = describe_heartbeat(heartbeat)
                latest_position = wait_local_position(master, 0.5) or latest_position
                write_row(
                    logger,
                    run_id,
                    sample_idx,
                    start_wall,
                    "land_complete",
                    latest_mode,
                    heartbeat_is_armed(heartbeat) if heartbeat else armed,
                    latest_position,
                    status="landing",
                    notes=f"{land_note}; {recovery_note}; {latest_heartbeat_note}",
                )
                print(f"[{sample_idx}] landing complete mode={latest_mode} {land_note} {recovery_note}")

    return output_path


def wait_local_position(master, timeout: float) -> tuple[float, float, float, float, float, float] | None:
    message = master.recv_match(type="LOCAL_POSITION_NED", blocking=True, timeout=timeout)
    if message is None:
        return None
    return (
        float(message.x),
        float(message.y),
        float(message.z),
        float(message.vx),
        float(message.vy),
        float(message.vz),
    )


def wait_heartbeat(master, timeout: float):
    return master.recv_match(type="HEARTBEAT", blocking=True, timeout=timeout)


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


def send_position_hold_setpoint(
    master,
    target_system: int,
    target_component: int,
    x: float,
    y: float,
    z: float,
) -> None:
    master.mav.set_position_target_local_ned_send(
        int(time.time() * 1000) & 0xFFFFFFFF,
        target_system,
        target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        POSITION_HOLD_TYPE_MASK,
        x,
        y,
        z,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )


def prime_setpoints(
    master,
    target_system: int,
    target_component: int,
    x: float,
    y: float,
    z: float,
    duration_s: float,
    period_s: float,
) -> None:
    deadline = time.time() + max(0.0, duration_s)
    while time.time() < deadline:
        send_position_hold_setpoint(master, target_system, target_component, x, y, z)
        time.sleep(period_s)


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


def request_land_mode(master) -> str:
    return request_px4_mode(master, "LAND")


def stream_until_mode(
    master,
    target_system: int,
    target_component: int,
    x: float,
    y: float,
    z: float,
    timeout_s: float,
    period_s: float,
    target_main_mode: int,
) -> tuple[str, object | None]:
    ack_note = "command_ack=none"
    latest_heartbeat = None
    deadline = time.time() + max(0.0, timeout_s)
    while time.time() < deadline:
        send_position_hold_setpoint(master, target_system, target_component, x, y, z)
        while True:
            message = master.recv_match(type=["COMMAND_ACK", "HEARTBEAT"], blocking=False)
            if message is None:
                break
            if message.get_type() == "COMMAND_ACK" and ack_note == "command_ack=none":
                ack_note = describe_command_ack(message)
            elif message.get_type() == "HEARTBEAT":
                latest_heartbeat = message
                _, _, px4_main_mode = describe_heartbeat(message)
                if px4_main_mode == target_main_mode:
                    return ack_note, latest_heartbeat
        time.sleep(period_s)
    return ack_note, latest_heartbeat


def describe_command_ack(ack) -> str:
    command_name = mavutil.mavlink.enums["MAV_CMD"].get(ack.command)
    result_name = mavutil.mavlink.enums["MAV_RESULT"].get(ack.result)
    command_label = command_name.name if command_name else str(ack.command)
    result_label = result_name.name if result_name else str(ack.result)
    return f"command_ack={command_label}:{result_label}"


def drain_state_messages(master, heartbeat, position):
    while True:
        message = master.recv_match(type=["LOCAL_POSITION_NED", "HEARTBEAT"], blocking=False)
        if message is None:
            break
        if message.get_type() == "LOCAL_POSITION_NED":
            position = (
                float(message.x),
                float(message.y),
                float(message.z),
                float(message.vx),
                float(message.vy),
                float(message.vz),
            )
        elif message.get_type() == "HEARTBEAT":
            heartbeat = message
    return heartbeat, position


def write_row(
    logger: Phase04CsvLogger,
    run_id: str,
    sample_idx: int,
    start_wall: float,
    event: str,
    flight_mode: str,
    armed: bool,
    position: tuple[float, float, float, float, float, float],
    status: str,
    notes: str,
) -> None:
    x, y, z, vx, vy, vz = position
    logger.write(
        {
            "run_id": run_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "phase": "fase04",
            "treatment": "pilot",
            "scenario_id": "P04_V03B_MAVLINK_DIRECT_HOVER",
            "sample_idx": sample_idx,
            "elapsed_seconds": f"{time.time() - start_wall:.3f}",
            "controller_phase": "mavlink_direct_hover",
            "controller_reason": "pymavlink_position_hold_setpoint",
            "event": event,
            "command_forward_m_s": 0.0,
            "command_right_m_s": 0.0,
            "command_down_m_s": 0.0,
            "command_yawspeed_deg_s": 0.0,
            "command_sent": event in {"offboard_start", "hover", "land"},
            "armed": armed,
            "flight_mode": flight_mode,
            "north_m": x,
            "east_m": y,
            "down_m": z,
            "altitude_m": max(0.0, -z),
            "velocity_north_m_s": vx,
            "velocity_east_m_s": vy,
            "velocity_down_m_s": vz,
            "status": status,
            "notes": notes,
        }
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal direct MAVLink hover test.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument("--connection", default=None)
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--prime-seconds", type=float, default=2.0)
    parser.add_argument("--mode-timeout", type=float, default=5.0)
    parser.add_argument("--heartbeat-grace", type=float, default=2.0)
    parser.add_argument("--period", type=float, default=0.05)
    parser.add_argument("--log-interval", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--min-altitude", type=float, default=0.8)
    parser.add_argument("--land-timeout", type=float, default=20.0)
    parser.add_argument("--landed-altitude", type=float, default=0.25)
    parser.add_argument("--no-land-after", action="store_true")
    parser.add_argument("--no-recover-after-land", action="store_true")
    return parser.parse_args()


def main() -> None:
    run_hover_test(parse_args())


if __name__ == "__main__":
    main()
