"""Phase 04 PX4 takeoff/land diagnostic without Offboard.

This script validates whether PX4 action commands move the AirSimNH vehicle.
It logs PX4 NED telemetry and AirSim multirotor state side by side.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.connection.airsim_client import connect_multirotor
from src.control.control_config import ControlConfig
from src.control.px4_offboard_control import Px4OffboardClient
from src.logging.experiment_logger import Phase04CsvLogger, build_run_id


def read_airsim_row(airsim_client, vehicle_name: str) -> dict[str, object]:
    state = airsim_client.getMultirotorState(vehicle_name=vehicle_name)
    kin = state.kinematics_estimated
    pos = kin.position
    vel = kin.linear_velocity
    return {
        "airsim_position_x": pos.x_val,
        "airsim_position_y": pos.y_val,
        "airsim_position_z": pos.z_val,
        "airsim_velocity_x": vel.x_val,
        "airsim_velocity_y": vel.y_val,
        "airsim_velocity_z": vel.z_val,
        "airsim_landed_state": str(state.landed_state),
    }


async def log_sample(
    logger: Phase04CsvLogger,
    run_id: str,
    sample_idx: int,
    event: str,
    px4_client: Px4OffboardClient,
    airsim_client,
    vehicle_name: str,
    start_time: float,
    status: str = "ok",
    notes: str = "",
) -> None:
    snapshot = await px4_client.telemetry_snapshot()
    elapsed = asyncio.get_event_loop().time() - start_time
    row = {
        "run_id": run_id,
        "timestamp": snapshot.timestamp,
        "phase": "fase04",
        "treatment": "pilot",
        "scenario_id": "P04_V02_PX4_TAKEOFF_LAND",
        "sample_idx": sample_idx,
        "elapsed_seconds": f"{elapsed:.3f}",
        "controller_phase": "px4_action",
        "event": event,
        "command_sent": event in {"arm", "takeoff", "land"},
        "status": status,
        "notes": notes,
        **snapshot.to_dict(),
        **read_airsim_row(airsim_client, vehicle_name),
    }
    logger.write(row)
    print(
        f"[{sample_idx}] {event} "
        f"px4_alt={snapshot.altitude_m} "
        f"mode={snapshot.flight_mode} "
        f"airsim_z={row['airsim_position_z']} "
        f"landed={row['airsim_landed_state']}"
    )


async def run_takeoff_land_test(args: argparse.Namespace) -> Path | None:
    if not args.confirm_send:
        print("Safety stop: this script sends PX4 arm/takeoff/land commands.")
        print("Re-run with --confirm-send only when AirSimNH + PX4 SITL are ready.")
        return None

    config = ControlConfig.from_json()
    run_id = build_run_id(config.logging.run_id_prefix)
    output_path = config.logging.logs_dir / f"{run_id}_px4_takeoff_land.csv"
    px4_client = await Px4OffboardClient.connect(config)
    airsim_client = connect_multirotor(vehicle_name=config.airsim.vehicle_name)
    start = asyncio.get_event_loop().time()

    print("PX4 takeoff/land diagnostic started. Offboard will not be used.")
    print(f"Log: {output_path}")

    sample_idx = 0
    with Phase04CsvLogger(output_path) as logger:
        try:
            await log_sample(
                logger,
                run_id,
                sample_idx,
                "precheck",
                px4_client,
                airsim_client,
                config.airsim.vehicle_name,
                start,
            )
            sample_idx += 1

            await px4_client.prepare_for_arm()
            await px4_client.drone.action.set_takeoff_altitude(float(args.takeoff_altitude))
            await px4_client.drone.action.arm()
            await log_sample(
                logger,
                run_id,
                sample_idx,
                "arm",
                px4_client,
                airsim_client,
                config.airsim.vehicle_name,
                start,
            )
            sample_idx += 1

            await px4_client.drone.action.takeoff()
            for _ in range(args.samples_after_takeoff):
                await asyncio.sleep(args.sample_interval)
                await log_sample(
                    logger,
                    run_id,
                    sample_idx,
                    "takeoff_monitor",
                    px4_client,
                    airsim_client,
                    config.airsim.vehicle_name,
                    start,
                )
                sample_idx += 1

            if not args.no_land_after:
                await px4_client.land()
                for _ in range(args.samples_after_land):
                    await asyncio.sleep(args.sample_interval)
                    await log_sample(
                        logger,
                        run_id,
                        sample_idx,
                        "land_monitor",
                        px4_client,
                        airsim_client,
                        config.airsim.vehicle_name,
                        start,
                    )
                    sample_idx += 1

        except Exception as exc:
            await log_sample(
                logger,
                run_id,
                sample_idx,
                "error",
                px4_client,
                airsim_client,
                config.airsim.vehicle_name,
                start,
                status="error",
                notes=str(exc),
            )
            raise

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate PX4 takeoff/land against AirSim state.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument("--takeoff-altitude", type=float, default=2.0)
    parser.add_argument("--sample-interval", type=float, default=1.0)
    parser.add_argument("--samples-after-takeoff", type=int, default=12)
    parser.add_argument("--samples-after-land", type=int, default=8)
    parser.add_argument("--no-land-after", action="store_true")
    return parser.parse_args()


def main() -> None:
    asyncio.run(run_takeoff_land_test(parse_args()))


if __name__ == "__main__":
    main()
