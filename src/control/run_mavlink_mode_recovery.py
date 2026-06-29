"""Recover PX4 from a stale mode using direct MAVLink.

Use this after an interrupted Offboard/MAVLink test leaves PX4 disarmed on the
ground in OFFBOARD or LAND, causing the next arm command to be denied.
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


def run_recovery(args: argparse.Namespace) -> Path | None:
    if not args.confirm_send:
        print("Safety stop: this script sends a PX4 mode request.")
        print("Re-run with --confirm-send only when PX4 SITL is ready.")
        return None

    load_dotenv(PROJECT_ROOT / "configs" / "px4_airsim.env")
    connection_string = args.connection or os.getenv(
        "PX4_MAVLINK_DIRECT_ADDRESS",
        "udpin:0.0.0.0:14601",
    )
    config = ControlConfig.from_json()
    run_id = build_run_id(config.logging.run_id_prefix)
    output_path = config.logging.logs_dir / f"{run_id}_mavlink_mode_recovery.csv"

    print(f"Connecting with pymavlink on {connection_string} ...")
    print("Do not run this at the same time as MAVSDK on the same UDP port.")
    master = mavutil.mavlink_connection(connection_string)
    heartbeat = master.wait_heartbeat(timeout=args.timeout)
    if heartbeat is None:
        raise RuntimeError("No MAVLink heartbeat received.")

    position = wait_local_position(master, args.timeout)
    mode, heartbeat_note, px4_main_mode, px4_sub_mode = describe_heartbeat(heartbeat)
    armed = heartbeat_is_armed(heartbeat)
    altitude_m = max(0.0, -position[2]) if position is not None else None

    print(
        "Initial MAVLink state: "
        f"mode={mode}, armed={armed}, altitude={altitude_m}, {heartbeat_note}"
    )
    print(f"Log: {output_path}")

    if (
        not args.allow_airborne
        and armed
        and altitude_m is not None
        and altitude_m > args.max_ground_altitude
    ):
        raise RuntimeError(
            "Safety stop: vehicle appears airborne and armed. "
            "Use --allow-airborne only for a deliberate mode recovery."
        )

    request_note = request_px4_mode(master, args.mode)
    ack_note = wait_command_ack(master, args.timeout)
    post_heartbeat = wait_heartbeat(master, args.timeout)
    post_position = wait_local_position(master, 1.0) or position
    post_mode, post_heartbeat_note, post_main_mode, post_sub_mode = describe_heartbeat(
        post_heartbeat
    )
    post_armed = heartbeat_is_armed(post_heartbeat) if post_heartbeat else armed
    post_altitude_m = max(0.0, -post_position[2]) if post_position is not None else altitude_m

    expected = px4_mode_expected(args.mode)
    status = "ok" if (post_main_mode, post_sub_mode) == expected else "diagnostic"
    if "MAV_RESULT_ACCEPTED" not in ack_note:
        status = "warning"

    notes = f"{request_note}; {ack_note}; {post_heartbeat_note}"
    print(
        "Recovery result: "
        f"post_mode={post_mode}, armed={post_armed}, altitude={post_altitude_m}, "
        f"status={status}; {notes}"
    )

    x, y, z, vx, vy, vz = post_position or (None, None, None, None, None, None)
    with Phase04CsvLogger(output_path) as logger:
        logger.write(
            {
                "run_id": run_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "phase": "fase04",
                "treatment": "pilot",
                "scenario_id": "P04_V02D_MAVLINK_MODE_RECOVERY",
                "sample_idx": 0,
                "controller_phase": "mavlink_mode_recovery",
                "controller_reason": "recover_from_stale_offboard_or_land",
                "event": "mode_recovery",
                "command_sent": True,
                "armed": post_armed,
                "flight_mode": post_mode,
                "north_m": x,
                "east_m": y,
                "down_m": z,
                "altitude_m": post_altitude_m,
                "velocity_north_m_s": vx,
                "velocity_east_m_s": vy,
                "velocity_down_m_s": vz,
                "status": status,
                "notes": notes,
            }
        )

    return output_path


def wait_local_position(master, timeout: float):
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


def describe_heartbeat(heartbeat):
    if heartbeat is None:
        return "", "heartbeat=none", None, None
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
    return mode, note, px4_main_mode, px4_sub_mode


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


def px4_mode_expected(mode_name: str) -> tuple[int, int]:
    if mode_name == "LOITER":
        return (4, 3)
    if mode_name == "LAND":
        return (4, 6)
    return (-1, -1)


def wait_command_ack(master, timeout: float) -> str:
    ack = master.recv_match(type="COMMAND_ACK", blocking=True, timeout=timeout)
    if ack is None:
        return "command_ack=none"
    command_name = mavutil.mavlink.enums["MAV_CMD"].get(ack.command)
    result_name = mavutil.mavlink.enums["MAV_RESULT"].get(ack.result)
    command_label = command_name.name if command_name else str(ack.command)
    result_label = result_name.name if result_name else str(ack.result)
    return f"command_ack={command_label}:{result_label}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recover PX4 mode using direct MAVLink.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument("--connection", default=None)
    parser.add_argument("--mode", choices=["LOITER", "LAND"], default="LOITER")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--max-ground-altitude", type=float, default=0.3)
    parser.add_argument("--allow-airborne", action="store_true")
    return parser.parse_args()


def main() -> None:
    run_recovery(parse_args())


if __name__ == "__main__":
    main()
