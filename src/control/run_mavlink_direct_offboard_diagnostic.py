"""Diagnose active-control path using direct MAVLink setpoints.

This script does not arm and does not take off. It uses pymavlink directly,
instead of MAVSDK Offboard, to send local-NED setpoints and request OFFBOARD
mode. The purpose is to separate a MAVSDK plugin issue from a lower-level
PX4/MAVLink issue.
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


VELOCITY_ONLY_TYPE_MASK = (
    mavutil.mavlink.POSITION_TARGET_TYPEMASK_X_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_Y_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_Z_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_AX_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_AY_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_AZ_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_YAW_IGNORE
    | mavutil.mavlink.POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE
)


def run_diagnostic(args: argparse.Namespace) -> Path | None:
    if not args.confirm_send:
        print("Safety stop: this script sends MAVLink setpoints and a mode request.")
        print("Re-run with --confirm-send only with PX4 SITL ready and disarmed.")
        return None

    load_dotenv(PROJECT_ROOT / "configs" / "px4_airsim.env")
    connection_string = args.connection or os.getenv(
        "PX4_MAVLINK_DIRECT_ADDRESS",
        "udpin:0.0.0.0:14601",
    )
    config = ControlConfig.from_json()
    run_id = build_run_id(config.logging.run_id_prefix)
    output_path = config.logging.logs_dir / f"{run_id}_mavlink_direct_offboard_diagnostic.csv"

    print(f"Connecting with pymavlink on {connection_string} ...")
    print("Do not run this at the same time as MAVSDK on the same UDP port.")
    master = mavutil.mavlink_connection(connection_string)
    heartbeat = master.wait_heartbeat(timeout=args.timeout)
    if heartbeat is None:
        raise RuntimeError("No MAVLink heartbeat received.")

    target_system = master.target_system
    target_component = master.target_component
    initial_mode = mavutil.mode_string_v10(heartbeat)
    print(
        "Heartbeat received: "
        f"system={target_system}, component={target_component}, mode={initial_mode}"
    )
    print(f"Log: {output_path}")

    local_position = wait_local_position(master, args.timeout)
    x, y, z = local_position if local_position is not None else (0.0, 0.0, 0.0)

    start_time = time.time()
    setpoints_sent = 0
    while time.time() - start_time < args.prime_seconds:
        send_zero_velocity_setpoint(master, target_system, target_component)
        setpoints_sent += 1
        time.sleep(args.period)

    try:
        mode_request_note = request_offboard_mode(master)
        ack_note, post_heartbeat, post_setpoints_sent = stream_after_mode_request(
            master,
            target_system,
            target_component,
            args.post_seconds,
            args.period,
        )
    except Exception as exc:  # pragma: no cover - validated against PX4/AirSimNH
        mode_request_note = f"mode_request_error={type(exc).__name__}:{exc}"
        ack_note = "command_ack=not_checked"
        post_heartbeat = None
        post_setpoints_sent = 0
    if post_heartbeat is None:
        post_heartbeat = wait_heartbeat(master, args.timeout)
    post_mode, heartbeat_note, px4_main_mode = describe_heartbeat(post_heartbeat)
    final_position = wait_local_position(master, 1.0)
    final_x, final_y, final_z = final_position if final_position is not None else (x, y, z)

    notes = (
        f"initial_mode={initial_mode}; post_mode={post_mode}; "
        f"setpoints_sent={setpoints_sent}; post_setpoints_sent={post_setpoints_sent}; "
        f"{mode_request_note}; {ack_note}; {heartbeat_note}"
    )
    status = "ok" if post_mode == "OFFBOARD" or px4_main_mode == 6 else "diagnostic"
    if status != "ok" and "MAV_RESULT_ACCEPTED" in ack_note:
        status = "accepted"
    if mode_request_note.startswith("mode_request_error="):
        status = "error"
    print(notes)

    with Phase04CsvLogger(output_path) as logger:
        logger.write(
            {
                "run_id": run_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "phase": "fase04",
                "treatment": "pilot",
                "scenario_id": "P04_V02C_MAVLINK_DIRECT_OFFBOARD_DIAGNOSTIC",
                "sample_idx": 0,
                "controller_phase": "mavlink_direct_offboard_diagnostic",
                "controller_reason": "pymavlink_zero_velocity_setpoints",
                "event": "mavlink_direct_offboard_diagnostic",
                "command_forward_m_s": 0.0,
                "command_right_m_s": 0.0,
                "command_down_m_s": 0.0,
                "command_yawspeed_deg_s": 0.0,
                "command_sent": True,
                "flight_mode": post_mode,
                "north_m": final_x,
                "east_m": final_y,
                "down_m": final_z,
                "altitude_m": max(0.0, -float(final_z)),
                "status": status,
                "notes": notes,
            }
        )

    return output_path


def wait_local_position(master, timeout: float) -> tuple[float, float, float] | None:
    message = master.recv_match(type="LOCAL_POSITION_NED", blocking=True, timeout=timeout)
    if message is None:
        return None
    return float(message.x), float(message.y), float(message.z)


def send_zero_velocity_setpoint(master, target_system: int, target_component: int) -> None:
    master.mav.set_position_target_local_ned_send(
        int(time.time() * 1000) & 0xFFFFFFFF,
        target_system,
        target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        VELOCITY_ONLY_TYPE_MASK,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )


def request_offboard_mode(master) -> str:
    mode_mapping = master.mode_mapping()
    if mode_mapping is None or "OFFBOARD" not in mode_mapping:
        return "offboard_mode_mapping_missing"
    base_mode, custom_mode, custom_sub_mode = mode_mapping["OFFBOARD"]
    master.set_mode(base_mode, custom_mode, custom_sub_mode)
    return (
        "requested_OFFBOARD_px4_mode="
        f"base={base_mode},custom={custom_mode},sub={custom_sub_mode}"
    )


def wait_command_ack(master, timeout: float) -> str:
    ack = master.recv_match(type="COMMAND_ACK", blocking=True, timeout=timeout)
    if ack is None:
        return "command_ack=none"
    return describe_command_ack(ack)


def describe_command_ack(ack) -> str:
    command_name = mavutil.mavlink.enums["MAV_CMD"].get(ack.command)
    result_name = mavutil.mavlink.enums["MAV_RESULT"].get(ack.result)
    command_label = command_name.name if command_name else str(ack.command)
    result_label = result_name.name if result_name else str(ack.result)
    return f"command_ack={command_label}:{result_label}"


def wait_heartbeat(master, timeout: float):
    heartbeat = master.recv_match(type="HEARTBEAT", blocking=True, timeout=timeout)
    return heartbeat


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


def stream_after_mode_request(
    master,
    target_system: int,
    target_component: int,
    duration_s: float,
    period_s: float,
) -> tuple[str, object | None, int]:
    ack_note = "command_ack=none"
    heartbeat = None
    setpoints_sent = 0
    deadline = time.time() + max(0.0, duration_s)

    while time.time() < deadline:
        send_zero_velocity_setpoint(master, target_system, target_component)
        setpoints_sent += 1

        while True:
            message = master.recv_match(type=["COMMAND_ACK", "HEARTBEAT"], blocking=False)
            if message is None:
                break
            message_type = message.get_type()
            if message_type == "COMMAND_ACK" and ack_note == "command_ack=none":
                ack_note = describe_command_ack(message)
            elif message_type == "HEARTBEAT":
                heartbeat = message

        time.sleep(period_s)

    if ack_note == "command_ack=none":
        ack_note = wait_command_ack(master, 0.2)

    return ack_note, heartbeat, setpoints_sent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose direct MAVLink OFFBOARD control path.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument("--connection", default=None)
    parser.add_argument("--prime-seconds", type=float, default=3.0)
    parser.add_argument("--post-seconds", type=float, default=2.0)
    parser.add_argument("--period", type=float, default=0.05)
    parser.add_argument("--timeout", type=float, default=5.0)
    return parser.parse_args()


def main() -> None:
    run_diagnostic(parse_args())


if __name__ == "__main__":
    main()
