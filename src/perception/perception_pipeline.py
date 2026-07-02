"""Live Phase 03 perception pipeline using AirSim camera frames.

This diagnostic pipeline validates marker detection from the AirSim bottom
camera before closing the control loop. It records raw/annotated images and
detection JSON for inspection, but these perception diagnostics are not
statistical evidence for the formal T0/T1 comparison by themselves.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import airsim
import cv2
import numpy as np

from src.connection.airsim_client import connect_multirotor
from src.perception.detector_factory import build_marker_detector
from src.utils.constants import (
    BOTTOM_CAMERA_NAME,
    DEFAULT_SPEED_MPS,
    PHASE03_FIGURES_DIR,
    RAW_DIR,
    VEHICLE_NAME,
)


def _safe_label(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def position_vehicle_for_capture(
    client: airsim.MultirotorClient,
    altitude_m: float,
    pose_mode: str = "api",
    pose_x: float | None = None,
    pose_y: float | None = None,
    land_after_capture: bool = False,
) -> None:
    """Place the simulated vehicle for a perception-only capture."""
    if altitude_m <= 0:
        return

    print(f"Positioning vehicle at {altitude_m:.1f} m above marker using {pose_mode} mode...")
    if pose_mode == "sim_pose":
        current_pose = client.simGetVehiclePose(vehicle_name=VEHICLE_NAME)
        target_x = current_pose.position.x_val if pose_x is None else pose_x
        target_y = current_pose.position.y_val if pose_y is None else pose_y
        target_pose = airsim.Pose(
            airsim.Vector3r(
                target_x,
                target_y,
                -abs(altitude_m),
            ),
            current_pose.orientation,
        )
        print(f"sim_pose target NED: x={target_x:.3f}, y={target_y:.3f}, z={-abs(altitude_m):.3f}")
        client.simSetVehiclePose(target_pose, ignore_collision=True, vehicle_name=VEHICLE_NAME)
        return

    client.enableApiControl(True, vehicle_name=VEHICLE_NAME)
    client.armDisarm(True, vehicle_name=VEHICLE_NAME)
    client.takeoffAsync(vehicle_name=VEHICLE_NAME).join()
    client.moveToPositionAsync(
        0,
        0,
        -abs(altitude_m),
        DEFAULT_SPEED_MPS,
        vehicle_name=VEHICLE_NAME,
    ).join()

    if land_after_capture:
        print("Vehicle will land after image capture.")


def capture_frame_bgr(
    camera_name: str = BOTTOM_CAMERA_NAME,
    altitude_m: float = 0.0,
    pose_mode: str = "api",
    pose_x: float | None = None,
    pose_y: float | None = None,
    land_after_capture: bool = False,
) -> np.ndarray:
    """Capture one AirSim frame from the configured camera as BGR."""
    client = connect_multirotor(vehicle_name=VEHICLE_NAME)
    position_vehicle_for_capture(client, altitude_m, pose_mode, pose_x, pose_y, land_after_capture)
    responses = client.simGetImages(
        [airsim.ImageRequest(camera_name, airsim.ImageType.Scene, False, False)],
        vehicle_name=VEHICLE_NAME,
    )

    if not responses:
        raise RuntimeError("AirSim did not return an image response.")

    response = responses[0]
    if response.width == 0 or response.height == 0 or not response.image_data_uint8:
        raise RuntimeError(f"Invalid image from camera '{camera_name}'.")

    img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
    img_rgb = img1d.reshape(response.height, response.width, 3)
    image_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    if altitude_m > 0 and land_after_capture:
        client.landAsync(vehicle_name=VEHICLE_NAME).join()
        client.armDisarm(False, vehicle_name=VEHICLE_NAME)
        client.enableApiControl(False, vehicle_name=VEHICLE_NAME)

    return image_bgr


def run_live_perception(
    camera_name: str = BOTTOM_CAMERA_NAME,
    environment: str = "AirSimNH",
    scenario_id: str = "P03_live",
    altitude_m: float = 0.0,
    pose_mode: str = "api",
    pose_x: float | None = None,
    pose_y: float | None = None,
    land_after_capture: bool = False,
    detector_name: str | None = None,
) -> dict[str, object]:
    """Run one detector pass and persist traceable perception diagnostics."""
    run_id = f"phase03_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
    detector = build_marker_detector(environment, detector_name)
    image_bgr = capture_frame_bgr(camera_name, altitude_m, pose_mode, pose_x, pose_y, land_after_capture)
    result = detector.detect(image_bgr)
    annotated = detector.annotate(image_bgr, result)

    environment_label = _safe_label(environment)
    scenario_label = _safe_label(scenario_id)
    raw_dir = RAW_DIR / "phase03_perception" / environment_label / scenario_label
    figures_dir = PHASE03_FIGURES_DIR / environment_label / scenario_label
    raw_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    raw_path = raw_dir / f"{run_id}_{camera_name}.png"
    annotated_path = figures_dir / f"{run_id}_{camera_name}_annotated.png"
    json_path = figures_dir / f"{run_id}_{camera_name}_detection.json"

    cv2.imwrite(str(raw_path), image_bgr)
    cv2.imwrite(str(annotated_path), annotated)

    payload = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(timespec="milliseconds"),
        "phase": "fase03",
        "environment": environment,
        "scenario_id": scenario_id,
        "capture_altitude_m": altitude_m,
        "pose_mode": pose_mode,
        "pose_x": pose_x,
        "pose_y": pose_y,
        "detector_name": detector_name or "config-default",
        "camera_name": camera_name,
        "raw_image": str(raw_path),
        "annotated_image": str(annotated_path),
        "result": result.to_dict(),
    }
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    print(f"Run ID: {run_id}")
    print(f"Environment: {environment}")
    print(f"Scenario ID: {scenario_id}")
    print(f"Capture altitude: {altitude_m:.1f} m")
    print(f"Pose mode: {pose_mode}")
    print(f"Detector: {detector_name or 'config-default'}")
    if pose_x is not None or pose_y is not None:
        print(f"Requested pose XY: x={pose_x}, y={pose_y}")
    print(f"Raw image: {raw_path}")
    print(f"Annotated image: {annotated_path}")
    print(f"Detection JSON: {json_path}")
    print(f"Detected: {result.detected}")
    if result.detected:
        print(
            "Relative error: "
            f"dx={result.error_x_px:.2f}px ({result.error_x_norm:.3f}), "
            f"dy={result.error_y_px:.2f}px ({result.error_y_norm:.3f})"
        )

    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run live Phase 03 perception from AirSim.")
    parser.add_argument(
        "--environment",
        default="AirSimNH",
        choices=["Blocks", "AirSimNH"],
        help="AirSim environment used for this run.",
    )
    parser.add_argument(
        "--scenario-id",
        default="P03_live",
        help="Scenario identifier for traceability.",
    )
    parser.add_argument(
        "--camera-name",
        default=BOTTOM_CAMERA_NAME,
        help="AirSim camera name. Default: bottom_center.",
    )
    parser.add_argument(
        "--altitude-m",
        type=float,
        default=0.0,
        help="Optional altitude before capture. Use 0 to avoid moving the vehicle.",
    )
    parser.add_argument(
        "--pose-mode",
        choices=["api", "sim_pose"],
        default="api",
        help="Vehicle positioning mode. Use sim_pose for PX4/AirSimNH perception-only diagnostics.",
    )
    parser.add_argument("--pose-x", type=float, default=None, help="Optional NED X for sim_pose mode.")
    parser.add_argument("--pose-y", type=float, default=None, help="Optional NED Y for sim_pose mode.")
    parser.add_argument(
        "--land-after-capture",
        action="store_true",
        help="Land after capture when --altitude-m is used.",
    )
    parser.add_argument(
        "--detector",
        choices=["hsv", "hsv_color_contour", "aruco", "aruco_fiducial", "fiducial"],
        default="hsv",
        help=(
            "Perception backend. Defaults to hsv to preserve Phase 03 commands; "
            "use aruco for the Phase 04 fiducial marker."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_live_perception(
        camera_name=args.camera_name,
        environment=args.environment,
        scenario_id=args.scenario_id,
        altitude_m=args.altitude_m,
        pose_mode=args.pose_mode,
        pose_x=args.pose_x,
        pose_y=args.pose_y,
        land_after_capture=args.land_after_capture,
        detector_name=args.detector,
    )


if __name__ == "__main__":
    main()
