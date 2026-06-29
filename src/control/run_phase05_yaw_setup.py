"""Set up the initial yaw condition for Phase 05 formal scenarios.

This helper is intended to run after takeoff and before spawning the marker.
The default method uses direct MAVLink OFFBOARD yaw-rate setpoints because
MAV_CMD_CONDITION_YAW was observed to be ignored by PX4 SITL in this setup.
It does not perform landing.
"""
from __future__ import annotations

import argparse
import math
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

from src.control.run_mavlink_visual_servo_test import (
    describe_heartbeat,
    heartbeat_is_armed,
    request_px4_mode,
    wait_attitude_yaw,
    wait_heartbeat,
    wait_local_position,
)


def _mask_constant(name: str, fallback: int) -> int:
    return int(getattr(mavutil.mavlink, name, fallback))


YAW_RATE_TYPE_MASK = (
    _mask_constant("POSITION_TARGET_TYPEMASK_X_IGNORE", 1)
    | _mask_constant("POSITION_TARGET_TYPEMASK_Y_IGNORE", 2)
    | _mask_constant("POSITION_TARGET_TYPEMASK_Z_IGNORE", 4)
    | _mask_constant("POSITION_TARGET_TYPEMASK_AX_IGNORE", 64)
    | _mask_constant("POSITION_TARGET_TYPEMASK_AY_IGNORE", 128)
    | _mask_constant("POSITION_TARGET_TYPEMASK_AZ_IGNORE", 256)
    | _mask_constant("POSITION_TARGET_TYPEMASK_YAW_IGNORE", 1024)
)


def run_yaw_setup(args: argparse.Namespace) -> None:
    if not args.confirm_send:
        print("Safety stop: this script sends MAVLink yaw commands.")
        print("Re-run with --confirm-send only after PX4 takeoff is stable.")
        return

    load_dotenv(PROJECT_ROOT / "configs" / "px4_airsim.env")
    connection_string = args.connection or os.getenv(
        "PX4_MAVLINK_DIRECT_ADDRESS",
        "udpin:0.0.0.0:14601",
    )
    master = mavutil.mavlink_connection(connection_string)
    heartbeat = wait_heartbeat(master, args.timeout)
    if heartbeat is None:
        raise RuntimeError("No MAVLink heartbeat received.")

    local_position = wait_local_position(master, args.timeout)
    if local_position is None:
        raise RuntimeError("No LOCAL_POSITION_NED received before yaw setup.")

    start_yaw_rad = wait_attitude_yaw(master, args.timeout)
    if start_yaw_rad is None:
        raise RuntimeError("No ATTITUDE yaw received before yaw setup.")

    mode, heartbeat_note, _ = describe_heartbeat(heartbeat)
    armed = heartbeat_is_armed(heartbeat)
    altitude_m = max(0.0, -local_position[2])
    if not armed:
        raise RuntimeError("Safety stop: vehicle is not armed; take off first.")
    if altitude_m < args.min_altitude:
        raise RuntimeError(
            "Safety stop: vehicle altitude is below yaw setup minimum: "
            f"altitude={altitude_m:.2f} m, min={args.min_altitude:.2f} m"
        )

    start_yaw_deg = _normalize_degrees(math.degrees(start_yaw_rad))
    if args.absolute_yaw_deg is not None:
        yaw_mode = "absolute"
        target_yaw_deg = _normalize_degrees(float(args.absolute_yaw_deg))
        target_delta_deg = _signed_angle_error(target_yaw_deg, start_yaw_deg)
    else:
        yaw_mode = "relative"
        target_delta_deg = float(args.relative_yaw_deg)
        target_yaw_deg = _normalize_degrees(start_yaw_deg + target_delta_deg)

    print(
        "Phase 05 yaw setup: "
        f"method={args.method}, mode={mode}, armed={armed}, altitude={altitude_m:.2f} m, "
        f"yaw_mode={yaw_mode}, start={start_yaw_deg:.2f} deg, "
        f"relative={target_delta_deg:.2f} deg, "
        f"target={target_yaw_deg:.2f} deg, {heartbeat_note}"
    )
    if args.method == "condition-yaw":
        _run_condition_yaw(
            master,
            args,
            target_delta_deg,
            target_yaw_deg,
            start_yaw_rad,
            relative=(yaw_mode == "relative"),
        )
    else:
        _run_offboard_yaw_rate(master, args, target_yaw_deg)


def _run_condition_yaw(
    master,
    args: argparse.Namespace,
    target_delta_deg: float,
    target_yaw_deg: float,
    start_yaw_rad: float,
    *,
    relative: bool,
) -> None:
    direction = 1 if target_delta_deg >= 0.0 else -1
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,
        0,
        abs(target_delta_deg) if relative else target_yaw_deg,
        float(args.yaw_speed_deg_s),
        direction,
        1 if relative else 0,
        0,
        0,
        0,
    )
    _wait_for_yaw_target(master, target_yaw_deg, math.degrees(start_yaw_rad), args.wait_timeout, args.tolerance_deg)


def _run_offboard_yaw_rate(master, args: argparse.Namespace, target_yaw_deg: float) -> None:
    target_system = master.target_system
    target_component = master.target_component
    setpoint_period = max(0.02, float(args.setpoint_period))

    deadline = time.time() + max(0.0, float(args.prime_seconds))
    while time.time() < deadline:
        _send_yaw_rate_setpoint(master, target_system, target_component, 0.0)
        time.sleep(setpoint_period)

    request_note = request_px4_mode(master, "OFFBOARD")
    offboard_deadline = time.time() + max(0.0, float(args.mode_timeout))
    latest_mode = ""
    while time.time() < offboard_deadline:
        _send_yaw_rate_setpoint(master, target_system, target_component, 0.0)
        heartbeat = wait_heartbeat(master, 0.2)
        latest_mode, heartbeat_note, px4_main_mode = describe_heartbeat(heartbeat)
        if latest_mode == "OFFBOARD" or px4_main_mode == 6:
            print(f"OFFBOARD accepted: {request_note}; {heartbeat_note}")
            break
        time.sleep(setpoint_period)
    else:
        raise RuntimeError(f"OFFBOARD was not accepted for yaw setup; last_mode={latest_mode}")

    deadline = time.time() + float(args.wait_timeout)
    last_yaw_deg = ""
    while time.time() < deadline:
        yaw_rad = wait_attitude_yaw(master, 0.2)
        if yaw_rad is None:
            _send_yaw_rate_setpoint(master, target_system, target_component, 0.0)
            continue
        last_yaw_deg = _normalize_degrees(math.degrees(yaw_rad))
        signed_error_deg = _signed_angle_error(target_yaw_deg, last_yaw_deg)
        error_deg = abs(signed_error_deg)
        yaw_rate_deg_s = _clamp(
            signed_error_deg * float(args.yaw_kp),
            -abs(float(args.yaw_speed_deg_s)),
            abs(float(args.yaw_speed_deg_s)),
        )
        if error_deg <= float(args.tolerance_deg):
            for _ in range(5):
                _send_yaw_rate_setpoint(master, target_system, target_component, 0.0)
                time.sleep(setpoint_period)
            recovery_note = request_px4_mode(master, args.recovery_mode)
            print(
                "Yaw setup accepted: "
                f"yaw={last_yaw_deg:.2f} deg target={target_yaw_deg:.2f} deg "
                f"error={error_deg:.2f} deg; {recovery_note}"
            )
            return
        print(
            f"yaw={last_yaw_deg:.2f} deg target={target_yaw_deg:.2f} deg "
            f"error={error_deg:.2f} deg yaw_rate={yaw_rate_deg_s:.2f} deg/s"
        )
        _send_yaw_rate_setpoint(
            master,
            target_system,
            target_component,
            math.radians(yaw_rate_deg_s),
        )
        time.sleep(setpoint_period)

    raise RuntimeError(
        "Yaw setup did not reach tolerance: "
        f"target={target_yaw_deg:.2f} deg, last={last_yaw_deg} deg, "
        f"tolerance={args.tolerance_deg:.2f} deg"
    )


def _wait_for_yaw_target(master, target_yaw_deg: float, start_yaw_deg: float, wait_timeout: float, tolerance_deg: float) -> None:
    deadline = time.time() + float(wait_timeout)
    last_yaw_deg = _normalize_degrees(start_yaw_deg)
    while time.time() < deadline:
        yaw_rad = wait_attitude_yaw(master, 0.5)
        if yaw_rad is None:
            continue
        last_yaw_deg = _normalize_degrees(math.degrees(yaw_rad))
        error_deg = abs(_signed_angle_error(target_yaw_deg, last_yaw_deg))
        print(f"yaw={last_yaw_deg:.2f} deg target={target_yaw_deg:.2f} deg error={error_deg:.2f} deg")
        if error_deg <= float(tolerance_deg):
            print("Yaw setup accepted.")
            return
    raise RuntimeError(
        "Yaw setup did not reach tolerance: "
        f"target={target_yaw_deg:.2f} deg, last={last_yaw_deg:.2f} deg, "
        f"tolerance={tolerance_deg:.2f} deg"
    )


def _send_yaw_rate_setpoint(master, target_system: int, target_component: int, yaw_rate_rad_s: float) -> None:
    master.mav.set_position_target_local_ned_send(
        int(time.time() * 1000) & 0xFFFFFFFF,
        target_system,
        target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        YAW_RATE_TYPE_MASK,
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
        yaw_rate_rad_s,
    )


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _normalize_degrees(value: float) -> float:
    value = value % 360.0
    return value if value >= 0.0 else value + 360.0


def _signed_angle_error(target_deg: float, current_deg: float) -> float:
    return (target_deg - current_deg + 180.0) % 360.0 - 180.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Set Phase 05 initial yaw by MAVLink command.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument("--connection", default=None)
    parser.add_argument(
        "--method",
        choices=["offboard-yaw-rate", "condition-yaw"],
        default="offboard-yaw-rate",
    )
    yaw_group = parser.add_mutually_exclusive_group(required=True)
    yaw_group.add_argument("--relative-yaw-deg", type=float)
    yaw_group.add_argument("--absolute-yaw-deg", type=float)
    parser.add_argument("--yaw-speed-deg-s", type=float, default=10.0)
    parser.add_argument("--yaw-kp", type=float, default=0.8)
    parser.add_argument("--tolerance-deg", type=float, default=3.0)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--wait-timeout", type=float, default=25.0)
    parser.add_argument("--prime-seconds", type=float, default=2.0)
    parser.add_argument("--mode-timeout", type=float, default=5.0)
    parser.add_argument("--setpoint-period", type=float, default=0.05)
    parser.add_argument("--min-altitude", type=float, default=0.8)
    parser.add_argument("--recovery-mode", choices=["LOITER", "LAND"], default="LOITER")
    return parser.parse_args()


def main() -> None:
    run_yaw_setup(parse_args())


if __name__ == "__main__":
    main()
