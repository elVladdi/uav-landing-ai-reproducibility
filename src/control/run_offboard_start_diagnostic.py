"""Diagnose MAVSDK Offboard start setpoint registration.

This script does not arm or take off. It sends one Offboard setpoint type and
then calls offboard.start() to distinguish two cases:

- NO_SETPOINT_SET: MAVSDK did not register the setpoint before start.
- COMMAND_DENIED or similar: the setpoint was registered, but PX4 rejected
  switching to Offboard in the current ground/disarmed state.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mavsdk.offboard import (
    OffboardError,
    PositionNedYaw,
    VelocityBodyYawspeed,
    VelocityNedYaw,
)

from src.control.control_config import ControlConfig
from src.control.px4_offboard_control import Px4OffboardClient
from src.logging.experiment_logger import Phase04CsvLogger, build_run_id


SETPOINT_STRATEGIES = [
    "position_ned",
    "velocity_ned",
    "position_velocity_ned",
    "velocity_body",
]


async def run_diagnostic(args: argparse.Namespace) -> Path | None:
    if not args.confirm_send:
        print("Safety stop: this script sends an Offboard start/stop diagnostic command.")
        print("Re-run with --confirm-send only when PX4 SITL is ready.")
        return None

    config = ControlConfig.from_json()
    run_id = build_run_id(config.logging.run_id_prefix)
    output_path = config.logging.logs_dir / f"{run_id}_offboard_start_diagnostic.csv"

    client = await Px4OffboardClient.connect(config)
    snapshot = await client.telemetry_snapshot()
    print(
        "PX4 diagnostic state: "
        f"mode={snapshot.flight_mode}, armed={snapshot.armed}, alt={snapshot.altitude_m}"
    )
    strategies = SETPOINT_STRATEGIES if args.strategy == "all" else [args.strategy]
    print(f"Strategy: {args.strategy}")
    print(f"Log: {output_path}")

    if snapshot.north_m is None or snapshot.east_m is None or snapshot.down_m is None:
        raise RuntimeError("Cannot diagnose Offboard: missing local NED position.")

    with Phase04CsvLogger(output_path) as logger:
        for sample_idx, strategy in enumerate(strategies):
            snapshot = await client.telemetry_snapshot()
            if snapshot.north_m is None or snapshot.east_m is None or snapshot.down_m is None:
                raise RuntimeError("Cannot diagnose Offboard: missing local NED position.")

            try:
                await send_repeated_setpoints(client, config, snapshot, strategy, args.repeats)
                await client.drone.offboard.start()
                result_status = "ok"
                notes = "offboard.start() accepted; stopping Offboard immediately"
                print(f"[{strategy}] {notes}")
                await client.stop_offboard()
            except OffboardError as exc:
                result_status = "error"
                notes = str(exc)
                print(f"[{strategy}] Offboard diagnostic result: {notes}")
            except Exception as exc:
                result_status = "error"
                notes = str(exc)
                print(f"[{strategy}] Offboard diagnostic unexpected error: {notes}")

            final_snapshot = await client.telemetry_snapshot()
            logger.write(
                {
                    "run_id": run_id,
                    "timestamp": final_snapshot.timestamp,
                    "phase": "fase04",
                    "treatment": "pilot",
                    "scenario_id": "P04_V02B_OFFBOARD_START_DIAGNOSTIC",
                    "sample_idx": sample_idx,
                    "controller_phase": "offboard_start_diagnostic",
                    "controller_reason": strategy,
                    "event": "offboard_start_diagnostic",
                    "command_sent": True,
                    "status": result_status,
                    "notes": notes,
                    **final_snapshot.to_dict(),
                }
            )

    return output_path


async def send_repeated_setpoints(
    client: Px4OffboardClient,
    config: ControlConfig,
    snapshot,
    strategy: str,
    repeats: int,
) -> None:
    position = PositionNedYaw(
        float(snapshot.north_m),
        float(snapshot.east_m),
        float(snapshot.down_m),
        0.0,
    )
    velocity_ned = VelocityNedYaw(0.0, 0.0, 0.0, 0.0)
    velocity_body = VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)

    for _ in range(max(1, repeats)):
        if strategy == "position_ned":
            await client.drone.offboard.set_position_ned(position)
        elif strategy == "velocity_ned":
            await client.drone.offboard.set_velocity_ned(velocity_ned)
        elif strategy == "position_velocity_ned":
            await client.drone.offboard.set_position_velocity_ned(
                position,
                velocity_ned,
            )
        elif strategy == "velocity_body":
            await client.drone.offboard.set_velocity_body(velocity_body)
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")
        await asyncio.sleep(config.offboard.control_period_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose Offboard start setpoint registration.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument(
        "--strategy",
        choices=[
            "all",
            "position_ned",
            "velocity_ned",
            "position_velocity_ned",
            "velocity_body",
        ],
        default="position_velocity_ned",
    )
    parser.add_argument("--repeats", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    asyncio.run(run_diagnostic(parse_args()))


if __name__ == "__main__":
    main()
