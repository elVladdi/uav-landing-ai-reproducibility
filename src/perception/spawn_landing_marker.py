"""Spawn a simple visual landing marker in AirSim.

This utility is intended for Phase 03 controlled validation in Blocks. It tries
to spawn a flat red object below the UAV so the bottom camera can validate the
perception pipeline before moving the same test to AirSimNH.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import airsim
import cv2
import numpy as np

from src.connection.airsim_client import connect_multirotor
from src.utils.constants import PHASE03_FIGURES_DIR, VEHICLE_NAME


DEFAULT_ASSET_CANDIDATES = [
    "Cube",
    "Cylinder",
    "Shape_Cube",
    "SM_Cube",
    "StaticMesh'/Engine/BasicShapes/Cube.Cube'",
    "StaticMesh'/Engine/BasicShapes/Cylinder.Cylinder'",
]


def create_marker_texture() -> Path:
    texture_dir = PHASE03_FIGURES_DIR / "assets"
    texture_dir.mkdir(parents=True, exist_ok=True)
    texture_path = texture_dir / "landing_marker_red.png"

    image = np.zeros((512, 512, 3), dtype=np.uint8)
    image[:, :] = (0, 0, 255)
    cv2.circle(image, (256, 256), 170, (0, 255, 255), 20)
    cv2.line(image, (256, 60), (256, 452), (255, 255, 255), 16)
    cv2.line(image, (60, 256), (452, 256), (255, 255, 255), 16)
    cv2.imwrite(str(texture_path), image)
    return texture_path


def spawn_marker(
    object_name: str,
    x: float,
    y: float,
    z: float,
    scale_x: float,
    scale_y: float,
    scale_z: float,
    asset_name: str | None = None,
    under_vehicle: bool = False,
    offset_x: float = 0.0,
    offset_y: float = 0.0,
) -> str:
    client = connect_multirotor(vehicle_name=VEHICLE_NAME)
    if under_vehicle:
        vehicle_pose = client.simGetVehiclePose(vehicle_name=VEHICLE_NAME)
        x = vehicle_pose.position.x_val + offset_x
        y = vehicle_pose.position.y_val + offset_y
        print(
            "Using current vehicle XY for marker: "
            f"x={x:.3f}, y={y:.3f}, marker_z={z:.3f}, "
            f"offset_x={offset_x:.3f}, offset_y={offset_y:.3f}"
        )

    pose = airsim.Pose(
        airsim.Vector3r(x, y, z),
        airsim.to_quaternion(0.0, 0.0, 0.0),
    )
    scale = airsim.Vector3r(scale_x, scale_y, scale_z)
    candidates = [asset_name] if asset_name else DEFAULT_ASSET_CANDIDATES

    spawned_name = ""
    errors: list[str] = []
    for candidate in candidates:
        try:
            result = client.simSpawnObject(
                object_name,
                candidate,
                pose,
                scale,
                physics_enabled=False,
                is_blueprint=False,
            )
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")
            continue

        if result:
            spawned_name = str(result)
            break
        errors.append(f"{candidate}: AirSim returned empty object name")

    if not spawned_name:
        error_text = "\n".join(errors)
        raise RuntimeError(
            "Could not spawn landing marker with the available asset names.\n"
            "Try passing a known Unreal/AirSim asset with --asset-name.\n"
            f"Attempts:\n{error_text}"
        )

    texture_path = create_marker_texture()
    material_ok = False
    try:
        material_ok = bool(client.simSetObjectMaterialFromTexture(spawned_name, str(texture_path)))
    except Exception as exc:
        print(f"Warning: texture assignment failed: {exc}")

    final_pose = client.simGetObjectPose(spawned_name)
    print(f"Spawned marker: {spawned_name}")
    print(f"Texture: {texture_path}")
    print(f"Texture assigned: {material_ok}")
    print(
        "Marker pose NED: "
        f"x={final_pose.position.x_val:.3f}, "
        f"y={final_pose.position.y_val:.3f}, "
        f"z={final_pose.position.z_val:.3f}"
    )
    print(f"Marker scale: x={scale_x:.3f}, y={scale_y:.3f}, z={scale_z:.3f}")
    return spawned_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Spawn a red landing marker in AirSim.")
    parser.add_argument("--object-name", default="phase03_landing_marker")
    parser.add_argument("--asset-name", default=None)
    parser.add_argument("--x", type=float, default=0.0)
    parser.add_argument("--y", type=float, default=0.0)
    parser.add_argument("--z", type=float, default=0.0)
    parser.add_argument("--scale-x", type=float, default=2.0)
    parser.add_argument("--scale-y", type=float, default=2.0)
    parser.add_argument("--scale-z", type=float, default=0.03)
    parser.add_argument(
        "--offset-x",
        type=float,
        default=0.0,
        help="NED X offset from the current vehicle position when --under-vehicle is used.",
    )
    parser.add_argument(
        "--offset-y",
        type=float,
        default=0.0,
        help="NED Y offset from the current vehicle position when --under-vehicle is used.",
    )
    parser.add_argument(
        "--under-vehicle",
        action="store_true",
        help="Use the current vehicle X/Y position and the provided marker Z.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spawn_marker(
        object_name=args.object_name,
        x=args.x,
        y=args.y,
        z=args.z,
        scale_x=args.scale_x,
        scale_y=args.scale_y,
        scale_z=args.scale_z,
        asset_name=args.asset_name,
        under_vehicle=args.under_vehicle,
        offset_x=args.offset_x,
        offset_y=args.offset_y,
    )


if __name__ == "__main__":
    main()
