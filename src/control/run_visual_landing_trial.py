"""Phase 04 pilot visual landing trial.

This is a guarded integration script. It captures AirSim images, computes
visual-servo commands, sends PX4 Offboard body-velocity setpoints, and logs the
full loop. It requires --confirm-send.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.control.airsim_vision import capture_scene_bgr, connect_airsim_vehicle
from src.control.control_config import ControlConfig
from src.control.landing_state_machine import VisionLandingStateMachine
from src.control.px4_offboard_control import Px4OffboardClient
from src.control.visual_servo_controller import VisualServoController
from src.logging.experiment_logger import Phase04CsvLogger, build_run_id
from src.perception.detector_factory import active_detector_name, build_marker_detector


async def run_visual_landing_trial(args: argparse.Namespace) -> Path | None:
    if not args.confirm_send:
        print("Safety stop: this script sends PX4 Offboard commands.")
        print("Run visual-servo dry-run first, then re-run with --confirm-send.")
        return None

    config = ControlConfig.from_json()
    environment = args.environment or config.airsim.environment
    camera_name = args.camera_name or config.airsim.camera_name
    run_id = build_run_id(config.logging.run_id_prefix)
    output_path = config.logging.logs_dir / f"{run_id}_visual_landing_trial.csv"

    airsim_client = connect_airsim_vehicle(config.airsim.vehicle_name)
    px4_client = await Px4OffboardClient.connect(config)
    await px4_client.wait_until_ready()
    selected_detector = (args.detector or active_detector_name()).strip().lower()
    detector = build_marker_detector(environment, selected_detector)
    controller = VisualServoController(config.visual_servo, config.offboard)
    state_machine = VisionLandingStateMachine(config)

    print("Visual landing trial will send PX4 Offboard commands.")
    print(f"Environment: {environment}")
    print(f"Detector: {selected_detector}")
    print(f"Log: {output_path}")

    took_off = False
    should_land_after = False
    with Phase04CsvLogger(output_path) as logger:
        try:
            if not args.skip_takeoff:
                print(f"Arming and taking off to {args.takeoff_altitude:.2f} m...")
                await px4_client.arm_and_takeoff(args.takeoff_altitude)
                took_off = True

            print("Starting Offboard...")
            await px4_client.start_offboard()

            start = time.perf_counter()
            sample_idx = 0
            while True:
                cycle_start = time.perf_counter()
                elapsed = cycle_start - start
                image_bgr = capture_scene_bgr(
                    airsim_client,
                    config.airsim.vehicle_name,
                    camera_name,
                )
                detection = detector.detect(image_bgr)
                visual_command = controller.command_from_detection(detection)
                snapshot = await px4_client.telemetry_snapshot()
                decision = state_machine.update(snapshot, visual_command, elapsed)
                await px4_client.set_body_velocity(decision.command)
                latency_ms = (time.perf_counter() - cycle_start) * 1000.0

                logger.write(
                    {
                        "run_id": run_id,
                        "timestamp": snapshot.timestamp,
                        "phase": "fase04",
                        "treatment": "T1_pilot",
                        "scenario_id": args.scenario_id,
                        "sample_idx": sample_idx,
                        "elapsed_seconds": f"{elapsed:.3f}",
                        "controller_phase": decision.phase.value,
                        "controller_reason": decision.reason,
                        "event": "visual_landing_loop",
                        "detector_method": detection.method,
                        "detected": detection.detected,
                        "accepted_detection": decision.command.accepted_detection,
                        "centered": decision.command.centered,
                        "confidence": detection.confidence,
                        "error_x_norm": detection.error_x_norm,
                        "error_y_norm": detection.error_y_norm,
                        "error_x_px": detection.error_x_px,
                        "error_y_px": detection.error_y_px,
                        "command_forward_m_s": decision.command.forward_m_s,
                        "command_right_m_s": decision.command.right_m_s,
                        "command_down_m_s": decision.command.down_m_s,
                        "command_yawspeed_deg_s": decision.command.yawspeed_deg_s,
                        "command_sent": True,
                        "latency_ms": f"{latency_ms:.2f}",
                        "status": "abort" if decision.should_abort else "ok",
                        "detection_notes": detection.notes,
                        **snapshot.to_dict(),
                    }
                )
                print(
                    f"[{sample_idx}] phase={decision.phase.value} "
                    f"detected={detection.detected} centered={decision.command.centered} "
                    f"cmd(fwd={decision.command.forward_m_s:.3f}, "
                    f"right={decision.command.right_m_s:.3f}, "
                    f"down={decision.command.down_m_s:.3f}) "
                    f"alt={snapshot.altitude_m}"
                )

                if decision.should_land or decision.should_abort:
                    should_land_after = decision.should_land
                    break
                sample_idx += 1
                await asyncio.sleep(config.offboard.control_period_seconds)

        finally:
            print("Stopping Offboard...")
            await px4_client.stop_offboard()
            if (took_off and not args.no_land_after) or should_land_after:
                print("Landing...")
                await px4_client.land()

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a guarded pilot visual landing trial.")
    parser.add_argument("--confirm-send", action="store_true")
    parser.add_argument("--environment", default=None, choices=["Blocks", "AirSimNH"])
    parser.add_argument("--camera-name", default=None)
    parser.add_argument("--scenario-id", default="P04_V09_VISUAL_DESCENT_PILOT")
    parser.add_argument("--skip-takeoff", action="store_true")
    parser.add_argument("--no-land-after", action="store_true")
    parser.add_argument("--takeoff-altitude", type=float, default=3.0)
    parser.add_argument(
        "--detector",
        choices=["hsv", "hsv_color_contour", "aruco", "aruco_fiducial", "fiducial"],
        default=None,
        help="Perception backend. Use aruco for the Phase 04 fiducial marker.",
    )
    return parser.parse_args()


def main() -> None:
    asyncio.run(run_visual_landing_trial(parse_args()))


if __name__ == "__main__":
    main()
