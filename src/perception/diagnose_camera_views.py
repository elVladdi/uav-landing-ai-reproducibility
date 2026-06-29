"""Capture diagnostic images from multiple AirSim cameras.

Use this when the external AirSim view shows the marker but the perception
pipeline does not see it from the configured camera.
"""
from __future__ import annotations

import argparse
import csv
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
from src.utils.constants import PHASE03_FIGURES_DIR, VEHICLE_NAME


DEFAULT_CAMERAS = ["bottom_center", "front_center", "0", "1", "2", "3", "4"]


def _safe_label(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def _response_to_bgr(response: airsim.ImageResponse) -> np.ndarray:
    img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
    img_rgb = img1d.reshape(response.height, response.width, 3)
    return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)


def _pose_row(label: str, pose: airsim.Pose) -> dict[str, object]:
    return {
        "position_x": pose.position.x_val,
        "position_y": pose.position.y_val,
        "position_z": pose.position.z_val,
        "orientation_w": pose.orientation.w_val,
        "orientation_x": pose.orientation.x_val,
        "orientation_y": pose.orientation.y_val,
        "orientation_z": pose.orientation.z_val,
    }


def diagnose_camera_views(
    environment: str,
    scenario_id: str,
    marker_name: str,
    camera_names: list[str],
    object_regex: str,
) -> Path:
    client = connect_multirotor(vehicle_name=VEHICLE_NAME)
    run_id = f"phase03_diag_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
    output_dir = (
        PHASE03_FIGURES_DIR
        / _safe_label(environment)
        / _safe_label(scenario_id)
        / run_id
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = output_dir / "camera_diagnostics.csv"
    fieldnames = [
        "run_id",
        "timestamp",
        "environment",
        "scenario_id",
        "kind",
        "name",
        "image_path",
        "width",
        "height",
        "status",
        "message",
        "position_x",
        "position_y",
        "position_z",
        "orientation_w",
        "orientation_x",
        "orientation_y",
        "orientation_z",
    ]

    rows: list[dict[str, object]] = []

    try:
        matching_objects = client.simListSceneObjects(object_regex)
        print(f"Objects matching '{object_regex}':")
        for object_name in matching_objects:
            print(f"  - {object_name}")
    except Exception as exc:
        matching_objects = []
        print(f"Object listing failed for '{object_regex}': {exc}")

    vehicle_state = client.getMultirotorState(vehicle_name=VEHICLE_NAME)
    kin = vehicle_state.kinematics_estimated
    vehicle_pose = airsim.Pose(kin.position, kin.orientation)
    rows.append(
        {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "environment": environment,
            "scenario_id": scenario_id,
            "kind": "pose",
            "name": VEHICLE_NAME,
            "image_path": "",
            "width": "",
            "height": "",
            "status": "ok",
            "message": "vehicle_pose",
            **_pose_row("vehicle", vehicle_pose),
        }
    )

    marker_names = [marker_name]
    marker_names.extend(name for name in matching_objects if name not in marker_names)

    for current_marker_name in marker_names:
        try:
            marker_pose = client.simGetObjectPose(current_marker_name)
            status = "ok"
            message = "marker_pose"
            pose_values = _pose_row("marker", marker_pose)
        except Exception as exc:
            status = "error"
            message = str(exc)
            pose_values = {
                "position_x": "",
                "position_y": "",
                "position_z": "",
                "orientation_w": "",
                "orientation_x": "",
                "orientation_y": "",
                "orientation_z": "",
            }

        rows.append(
            {
                "run_id": run_id,
                "timestamp": datetime.now().isoformat(timespec="milliseconds"),
                "environment": environment,
                "scenario_id": scenario_id,
                "kind": "pose",
                "name": current_marker_name,
                "image_path": "",
                "width": "",
                "height": "",
                "status": status,
                "message": message,
                **pose_values,
            }
        )

    for camera_name in camera_names:
        try:
            responses = client.simGetImages(
                [airsim.ImageRequest(camera_name, airsim.ImageType.Scene, False, False)],
                vehicle_name=VEHICLE_NAME,
            )
            response = responses[0] if responses else None
            if (
                response is None
                or response.width == 0
                or response.height == 0
                or not response.image_data_uint8
            ):
                raise RuntimeError("empty image response")

            image_bgr = _response_to_bgr(response)
            image_path = output_dir / f"{camera_name}_scene.png"
            cv2.imwrite(str(image_path), image_bgr)
            rows.append(
                {
                    "run_id": run_id,
                    "timestamp": datetime.now().isoformat(timespec="milliseconds"),
                    "environment": environment,
                    "scenario_id": scenario_id,
                    "kind": "camera",
                    "name": camera_name,
                    "image_path": str(image_path),
                    "width": response.width,
                    "height": response.height,
                    "status": "ok",
                    "message": "captured",
                    "position_x": "",
                    "position_y": "",
                    "position_z": "",
                    "orientation_w": "",
                    "orientation_x": "",
                    "orientation_y": "",
                    "orientation_z": "",
                }
            )
            print(f"{camera_name}: captured -> {image_path}")
        except Exception as exc:
            rows.append(
                {
                    "run_id": run_id,
                    "timestamp": datetime.now().isoformat(timespec="milliseconds"),
                    "environment": environment,
                    "scenario_id": scenario_id,
                    "kind": "camera",
                    "name": camera_name,
                    "image_path": "",
                    "width": "",
                    "height": "",
                    "status": "error",
                    "message": str(exc),
                    "position_x": "",
                    "position_y": "",
                    "position_z": "",
                    "orientation_w": "",
                    "orientation_x": "",
                    "orientation_y": "",
                    "orientation_z": "",
                }
            )
            print(f"{camera_name}: error -> {exc}")

    with metadata_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Diagnostics directory: {output_dir}")
    print(f"Diagnostics CSV: {metadata_path}")
    return output_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture diagnostic AirSim camera views.")
    parser.add_argument("--environment", default="AirSimNH")
    parser.add_argument("--scenario-id", default="P03_AIRSIMNH_MARKER")
    parser.add_argument("--marker-name", default="phase03_landing_marker")
    parser.add_argument("--object-regex", default=".*phase03.*marker.*")
    parser.add_argument("--cameras", nargs="+", default=DEFAULT_CAMERAS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    diagnose_camera_views(
        environment=args.environment,
        scenario_id=args.scenario_id,
        marker_name=args.marker_name,
        camera_names=args.cameras,
        object_regex=args.object_regex,
    )


if __name__ == "__main__":
    main()
