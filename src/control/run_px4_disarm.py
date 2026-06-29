"""Guarded PX4 disarm helper.

Use this only after confirming that the simulated vehicle is already on the
ground. The script exists to leave PX4 in a clean state between Phase 05 runs.
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


async def run_disarm(
    confirm_send: bool,
    landed_altitude_m: float,
    timeout_seconds: float,
) -> None:
    if not confirm_send:
        print("Safety stop: this script sends a PX4 disarm command.")
        print("Re-run with --confirm-send only when the vehicle is landed.")
        return

    config = ControlConfig.from_json()
    client = await Px4OffboardClient.connect(config)
    snapshot = await client.telemetry_snapshot()
    print(
        "Current PX4 state before disarm: "
        f"mode={snapshot.flight_mode}, armed={snapshot.armed}, alt={snapshot.altitude_m}"
    )

    if snapshot.altitude_m is None:
        raise RuntimeError("Cannot disarm safely: altitude telemetry is unavailable.")
    if snapshot.altitude_m > landed_altitude_m:
        raise RuntimeError(
            "Safety stop: vehicle altitude is above landed threshold "
            f"({snapshot.altitude_m:.3f} m > {landed_altitude_m:.3f} m). "
            "Land first before disarming."
        )

    if snapshot.armed is False:
        print("Vehicle already appears disarmed.")
    else:
        print("Sending PX4 disarm command...")
        await client.disarm()

    start = asyncio.get_event_loop().time()
    last_snapshot = snapshot
    while asyncio.get_event_loop().time() - start <= timeout_seconds:
        last_snapshot = await client.telemetry_snapshot()
        print(
            "Disarm state: "
            f"mode={last_snapshot.flight_mode}, "
            f"armed={last_snapshot.armed}, "
            f"alt={last_snapshot.altitude_m}"
        )
        if last_snapshot.armed is False:
            if last_snapshot.flight_mode in {"LAND", "OFFBOARD"}:
                print(
                    f"PX4 is disarmed but still in {last_snapshot.flight_mode}; "
                    "requesting HOLD recovery..."
                )
                try:
                    await client.hold()
                except Exception as exc:
                    print(f"Warning: HOLD recovery failed: {exc}")
            print("Disarm accepted.")
            return
        await asyncio.sleep(0.5)

    raise RuntimeError(
        "Disarm timeout: PX4 did not report armed=False within "
        f"{timeout_seconds:.1f} s. Last armed={last_snapshot.armed}, "
        f"mode={last_snapshot.flight_mode}."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a guarded PX4 disarm command.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument("--landed-altitude", type=float, default=0.30)
    parser.add_argument("--timeout", type=float, default=10.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(run_disarm(args.confirm_send, args.landed_altitude, args.timeout))


if __name__ == "__main__":
    main()
