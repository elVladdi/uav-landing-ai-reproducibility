"""Phase 04 PX4 telemetry logging check.

This script does not arm the vehicle and does not send Offboard commands.
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
from src.logging.experiment_logger import Phase04CsvLogger, build_run_id


async def run_telemetry_check(duration_seconds: float, sample_interval_seconds: float) -> Path:
    config = ControlConfig.from_json()
    run_id = build_run_id(config.logging.run_id_prefix)
    output_path = config.logging.logs_dir / f"{run_id}_px4_telemetry.csv"

    client = await Px4OffboardClient.connect(config)
    print("PX4 connected. Reading telemetry only; no commands will be sent.")
    print(f"Log: {output_path}")

    sample_idx = 0
    start = asyncio.get_event_loop().time()
    with Phase04CsvLogger(output_path) as logger:
        while asyncio.get_event_loop().time() - start <= duration_seconds:
            elapsed = asyncio.get_event_loop().time() - start
            snapshot = await client.telemetry_snapshot()
            telemetry_complete = bool(snapshot.flight_mode) and snapshot.altitude_m is not None
            status = "ok" if telemetry_complete else "warning"
            notes = "" if telemetry_complete else "telemetry_incomplete_possible_simulator_link_loss"
            row = {
                "run_id": run_id,
                "timestamp": snapshot.timestamp,
                "phase": "fase04",
                "treatment": "pilot",
                "scenario_id": "P04_V01_TELEMETRY",
                "sample_idx": sample_idx,
                "elapsed_seconds": f"{elapsed:.3f}",
                "event": "telemetry",
                "command_sent": False,
                "status": status,
                "notes": notes,
                **snapshot.to_dict(),
            }
            logger.write(row)
            print(
                f"[{sample_idx}] mode={snapshot.flight_mode} "
                f"armed={snapshot.armed} alt={snapshot.altitude_m} "
                f"status={status}"
            )
            if not telemetry_complete:
                print(
                    "Warning: incomplete telemetry. If PX4 shows "
                    "'simulator_mavlink poll timeout', restart AirSimNH and PX4 SITL."
                )
            sample_idx += 1
            await asyncio.sleep(sample_interval_seconds)

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Log PX4 telemetry for Phase 04.")
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--sample-interval", type=float, default=0.5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(run_telemetry_check(args.duration, args.sample_interval))


if __name__ == "__main__":
    main()
