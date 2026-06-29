"""Phase 04 visual-servo dry run.

Captures AirSim images, runs the Phase 03 detector, computes the control
command, and logs it without sending anything to PX4.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from src.control.airsim_vision import capture_scene_bgr, connect_airsim_vehicle
from src.control.control_config import ControlConfig
from src.control.px4_offboard_control import Px4OffboardClient
from src.control.visual_servo_controller import VisualServoController
from src.logging.experiment_logger import Phase04CsvLogger, build_run_id
from src.perception.detector_factory import active_detector_name, build_marker_detector


async def run_dry_run(args: argparse.Namespace) -> Path:
    config = ControlConfig.from_json()
    environment = args.environment or config.airsim.environment
    camera_name = args.camera_name or config.airsim.camera_name
    run_id = build_run_id(config.logging.run_id_prefix)
    output_path = config.logging.logs_dir / f"{run_id}_visual_servo_dry_run.csv"
    figures_dir = config.logging.figures_dir / "dry_run" / run_id

    airsim_client = connect_airsim_vehicle(config.airsim.vehicle_name)
    px4_client = await Px4OffboardClient.connect(config) if args.with_px4 else None
    selected_detector = (args.detector or active_detector_name()).strip().lower()
    scenario_id = args.scenario_id or (
        "P04_V06C_ARUCO_FIDUCIAL_DRY_RUN"
        if "aruco" in selected_detector or "fiducial" in selected_detector
        else "P04_V06_VISUAL_SERVO_DRY_RUN"
    )
    detector = build_marker_detector(environment, selected_detector)
    controller = VisualServoController(config.visual_servo, config.offboard)

    print("Visual-servo dry-run started. No PX4 commands will be sent.")
    print(f"Environment: {environment}")
    print(f"Detector: {selected_detector}")
    print(f"Scenario ID: {scenario_id}")
    print(f"Log: {output_path}")

    with Phase04CsvLogger(output_path) as logger:
        for sample_idx in range(args.samples):
            cycle_start = time.perf_counter()
            image_bgr = capture_scene_bgr(
                airsim_client,
                config.airsim.vehicle_name,
                camera_name,
            )
            detection = detector.detect(image_bgr)
            command = controller.command_from_detection(detection)
            latency_ms = (time.perf_counter() - cycle_start) * 1000.0
            snapshot = await px4_client.telemetry_snapshot() if px4_client else None

            if args.save_annotated:
                figures_dir.mkdir(parents=True, exist_ok=True)
                annotated = detector.annotate(image_bgr, detection)
                cv2.imwrite(str(figures_dir / f"{sample_idx:04d}_annotated.png"), annotated)

            telemetry_row = snapshot.to_dict() if snapshot else {}
            timestamp = snapshot.timestamp if snapshot else datetime.now().isoformat(timespec="milliseconds")
            logger.write(
                {
                    "run_id": run_id,
                    "timestamp": timestamp,
                    "phase": "fase04",
                    "treatment": "pilot",
                    "scenario_id": scenario_id,
                    "sample_idx": sample_idx,
                    "elapsed_seconds": "",
                    "controller_phase": "dry_run",
                    "controller_reason": command.reason,
                    "event": "visual_servo_dry_run",
                    "detector_method": detection.method,
                    "detected": detection.detected,
                    "accepted_detection": command.accepted_detection,
                    "centered": command.centered,
                    "confidence": detection.confidence,
                    "error_x_norm": detection.error_x_norm,
                    "error_y_norm": detection.error_y_norm,
                    "error_x_px": detection.error_x_px,
                    "error_y_px": detection.error_y_px,
                    "command_forward_m_s": command.forward_m_s,
                    "command_right_m_s": command.right_m_s,
                    "command_down_m_s": command.down_m_s,
                    "command_yawspeed_deg_s": command.yawspeed_deg_s,
                    "command_sent": False,
                    "latency_ms": f"{latency_ms:.2f}",
                    "status": "ok",
                    "detection_notes": detection.notes,
                    **telemetry_row,
                }
            )
            print(
                f"[{sample_idx}] detected={detection.detected} "
                f"centered={command.centered} "
                f"cmd(fwd={command.forward_m_s:.3f}, right={command.right_m_s:.3f}) "
                f"latency={latency_ms:.1f} ms"
            )
            await asyncio.sleep(config.offboard.control_period_seconds)

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute visual-servo commands without sending them.")
    parser.add_argument("--environment", default=None, choices=["Blocks", "AirSimNH"])
    parser.add_argument("--camera-name", default=None)
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--with-px4", action="store_true")
    parser.add_argument("--save-annotated", action="store_true")
    parser.add_argument("--scenario-id", default=None)
    parser.add_argument(
        "--detector",
        choices=["hsv", "hsv_color_contour", "aruco", "aruco_fiducial", "fiducial"],
        default=None,
        help="Perception backend. Use aruco for the Phase 04 fiducial marker.",
    )
    return parser.parse_args()


def main() -> None:
    asyncio.run(run_dry_run(parse_args()))


if __name__ == "__main__":
    main()
