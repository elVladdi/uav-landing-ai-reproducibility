"""Phase 04 PX4 land helper.

Use this after a guarded hover/dry-run sequence that leaves the vehicle airborne.
It requires --confirm-send because it sends a PX4 land command.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.control.control_config import ControlConfig
from src.control.px4_offboard_control import Px4OffboardClient


async def run_land(
    confirm_send: bool,
    timeout_seconds: float,
    landed_altitude_m: float,
) -> None:
    if not confirm_send:
        print("Safety stop: this script sends a PX4 land command.")
        print("Re-run with --confirm-send only when AirSimNH + PX4 SITL are ready.")
        return

    config = ControlConfig.from_json()
    client = await Px4OffboardClient.connect(config)
    snapshot = await client.telemetry_snapshot()
    print(
        "Current PX4 state before land: "
        f"mode={snapshot.flight_mode}, armed={snapshot.armed}, alt={snapshot.altitude_m}"
    )
    if snapshot.armed is False and (snapshot.altitude_m or 0.0) <= landed_altitude_m:
        print("Vehicle already appears landed and disarmed.")
        if snapshot.flight_mode in {"LAND", "OFFBOARD"}:
            print(f"PX4 is still in {snapshot.flight_mode} mode; requesting HOLD recovery...")
            try:
                await client.hold()
            except Exception as exc:
                print(f"Warning: HOLD recovery failed: {exc}")
                print(
                    "If arming is denied, run "
                    "src\\control\\run_mavlink_mode_recovery.py --confirm-send "
                    "or restart PX4/AirSimNH before the next attempt."
                )
        return

    print("Sending PX4 land command...")
    await client.land()
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start <= timeout_seconds:
        snapshot = await client.telemetry_snapshot()
        if snapshot.altitude_m is None:
            print("Landing state: telemetry incomplete; waiting...")
        else:
            print(
                "Landing state: "
                f"mode={snapshot.flight_mode}, armed={snapshot.armed}, alt={snapshot.altitude_m}"
            )
        if snapshot.altitude_m is not None and snapshot.altitude_m <= landed_altitude_m:
            print("Landing altitude threshold reached.")
            if snapshot.flight_mode in {"LAND", "OFFBOARD"}:
                print(f"Requesting HOLD recovery after landing from {snapshot.flight_mode}...")
                try:
                    await client.hold()
                except Exception as exc:
                    print(f"Warning: HOLD recovery failed: {exc}")
                    print(
                        "If arming is denied, run "
                        "src\\control\\run_mavlink_mode_recovery.py --confirm-send "
                        "or restart PX4/AirSimNH before the next attempt."
                    )
            return
        await asyncio.sleep(1.0)
    raise RuntimeError(
        "Landing timeout: "
        f"altitude did not fall below {landed_altitude_m:.2f} m within "
        f"{timeout_seconds:.1f} s."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a guarded PX4 land command.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--landed-altitude", type=float, default=0.25)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(run_land(args.confirm_send, args.timeout, args.landed_altitude))


if __name__ == "__main__":
    main()
