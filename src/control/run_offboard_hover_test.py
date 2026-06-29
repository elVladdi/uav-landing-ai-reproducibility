"""Phase 04 Offboard hover smoke test.

This script can arm, take off, start Offboard, send neutral body-velocity
setpoints, then land. It requires --confirm-send.
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
from src.control.visual_servo_controller import BodyVelocityCommand
from src.logging.experiment_logger import Phase04CsvLogger, build_run_id


async def run_hover_test(args: argparse.Namespace) -> Path | None:
    if not args.confirm_send:
        print("Safety stop: this script sends PX4 Offboard commands.")
        print("Re-run with --confirm-send only when AirSimNH + PX4 SITL are ready.")
        return None

    config = ControlConfig.from_json()
    duration = args.duration or config.offboard.hover_test_duration_seconds
    takeoff_altitude = args.takeoff_altitude or config.offboard.takeoff_altitude_m
    run_id = build_run_id(config.logging.run_id_prefix)
    output_path = config.logging.logs_dir / f"{run_id}_offboard_hover.csv"
    command = BodyVelocityCommand.hover(reason="offboard_hover")

    client = await Px4OffboardClient.connect(config)
    await client.wait_until_ready()
    print("PX4 ready for Offboard hover smoke test.")
    print(f"Log: {output_path}")

    took_off = False
    takeoff_attempted = False
    offboard_started = False
    error_occurred = False
    sample_idx = 0
    with Phase04CsvLogger(output_path) as logger:
        try:
            if not args.skip_takeoff:
                print(f"Arming and taking off to {takeoff_altitude:.2f} m...")
                takeoff_attempted = True
                await client.arm_and_takeoff(takeoff_altitude)
                took_off = True

            print("Starting Offboard with local NED priming...")
            await client.start_offboard()
            offboard_started = True

            start = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start <= duration:
                elapsed = asyncio.get_event_loop().time() - start
                await client.set_body_velocity(command)
                snapshot = await client.telemetry_snapshot()
                logger.write(
                    {
                        "run_id": run_id,
                        "timestamp": snapshot.timestamp,
                        "phase": "fase04",
                        "treatment": "pilot",
                        "scenario_id": "P04_V03_OFFBOARD_HOVER",
                        "sample_idx": sample_idx,
                        "elapsed_seconds": f"{elapsed:.3f}",
                        "controller_phase": "hover",
                        "controller_reason": command.reason,
                        "event": "offboard_hover",
                        "command_forward_m_s": command.forward_m_s,
                        "command_right_m_s": command.right_m_s,
                        "command_down_m_s": command.down_m_s,
                        "command_yawspeed_deg_s": command.yawspeed_deg_s,
                        "command_sent": True,
                        "status": "ok",
                        **snapshot.to_dict(),
                    }
                )
                print(f"[{sample_idx}] hover alt={snapshot.altitude_m}")
                sample_idx += 1
                await asyncio.sleep(config.offboard.control_period_seconds)

        except Exception as exc:
            error_occurred = True
            snapshot = await client.telemetry_snapshot()
            print(f"Offboard hover failed: {exc}")
            print(f"Error logged in: {output_path}")
            logger.write(
                {
                    "run_id": run_id,
                    "timestamp": snapshot.timestamp,
                    "phase": "fase04",
                    "treatment": "pilot",
                    "scenario_id": "P04_V03_OFFBOARD_HOVER",
                    "sample_idx": sample_idx,
                    "controller_phase": "hover",
                    "event": "offboard_hover_error",
                    "command_sent": False,
                    "status": "error",
                    "notes": str(exc),
                    **snapshot.to_dict(),
                }
            )
            if args.raise_on_error:
                raise

        finally:
            if offboard_started:
                print("Stopping Offboard...")
                await client.stop_offboard()
            if (took_off and not args.no_land_after) or (takeoff_attempted and error_occurred):
                print("Landing...")
                try:
                    await client.land()
                    await wait_after_land(
                        client,
                        timeout_seconds=args.land_timeout,
                        landed_altitude_m=args.landed_altitude,
                    )
                except Exception as land_exc:
                    print(f"Warning: landing command/monitor failed: {land_exc}")
                    print("Run run_px4_telemetry_check.py before the next test.")

    return output_path


async def wait_after_land(
    client: Px4OffboardClient,
    timeout_seconds: float,
    landed_altitude_m: float,
) -> None:
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start <= timeout_seconds:
        snapshot = await client.telemetry_snapshot()
        print(
            "Landing monitor: "
            f"mode={snapshot.flight_mode}, armed={snapshot.armed}, alt={snapshot.altitude_m}"
        )
        if snapshot.altitude_m is not None and snapshot.altitude_m <= landed_altitude_m:
            return
        if snapshot.armed is False:
            return
        await asyncio.sleep(1.0)
    print(
        "Warning: landing monitor timeout. "
        "Run run_px4_telemetry_check.py before the next test."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a safe Offboard hover smoke test.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument("--skip-takeoff", action="store_true")
    parser.add_argument("--no-land-after", action="store_true")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--takeoff-altitude", type=float, default=None)
    parser.add_argument("--land-timeout", type=float, default=45.0)
    parser.add_argument("--landed-altitude", type=float, default=0.30)
    parser.add_argument("--raise-on-error", action="store_true")
    return parser.parse_args()


def main() -> None:
    asyncio.run(run_hover_test(parse_args()))


if __name__ == "__main__":
    main()
