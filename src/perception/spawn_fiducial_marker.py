"""Generate and spawn the ArUco fiducial landing marker in AirSim.

The formal T1 workflow uses an ArUco `DICT_4X4_50` marker with ID `23`. This
script creates the texture and optionally places it in the AirSimNH world so the
bottom camera can observe the marker center for image-space control.
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
from src.perception.fiducial_marker_detector import render_aruco_marker
from src.utils.constants import FIGURES_DIR, VEHICLE_NAME


DEFAULT_ASSET_CANDIDATES = [
    "Cube",
    "Shape_Cube",
    "SM_Cube",
    "StaticMesh'/Engine/BasicShapes/Cube.Cube'",
]


def create_fiducial_texture(
    dictionary_name: str,
    marker_id: int,
    texture_size_px: int = 2048,
    marker_size_ratio: float = 0.72,
) -> Path:
    """Create the marker texture image used by AirSim object material assignment."""
    texture_dir = FIGURES_DIR / "phase04_control" / "assets"
    texture_dir.mkdir(parents=True, exist_ok=True)
    texture_path = texture_dir / f"aruco_{dictionary_name.lower()}_id{marker_id}.png"

    texture_size_px = max(128, int(texture_size_px))
    marker_size_px = int(texture_size_px * float(marker_size_ratio))
    marker_size_px = max(64, min(texture_size_px, marker_size_px))
    margin = int((texture_size_px - marker_size_px) / 2)

    marker_gray = render_aruco_marker(dictionary_name, marker_id, marker_size_px)
    texture_gray = np.full((texture_size_px, texture_size_px), 255, dtype=np.uint8)
    texture_gray[
        margin : margin + marker_size_px,
        margin : margin + marker_size_px,
    ] = marker_gray

    texture_bgr = cv2.cvtColor(texture_gray, cv2.COLOR_GRAY2BGR)
    cv2.imwrite(str(texture_path), texture_bgr)
    return texture_path


def spawn_fiducial_marker(
    object_name: str,
    x: float,
    y: float,
    z: float,
    scale_x: float,
    scale_y: float,
    scale_z: float,
    dictionary_name: str,
    marker_id: int,
    asset_name: str | None = None,
    under_vehicle: bool = False,
    offset_x: float = 0.0,
    offset_y: float = 0.0,
    texture_size_px: int = 2048,
    marker_size_ratio: float = 0.72,
    generate_only: bool = False,
) -> str:
    """Spawn or generate the configured ArUco marker for a simulated run."""
    texture_path = create_fiducial_texture(
        dictionary_name=dictionary_name,
        marker_id=marker_id,
        texture_size_px=texture_size_px,
        marker_size_ratio=marker_size_ratio,
    )
    print(f"Fiducial texture: {texture_path}")
    if generate_only:
        return str(texture_path)

    client = connect_multirotor(vehicle_name=VEHICLE_NAME)
    if under_vehicle:
        vehicle_pose = client.simGetVehiclePose(vehicle_name=VEHICLE_NAME)
        x = vehicle_pose.position.x_val + offset_x
        y = vehicle_pose.position.y_val + offset_y
        print(
            "Using current vehicle XY for fiducial marker: "
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
            "Could not spawn fiducial marker with the available asset names.\n"
            "Try passing a known Unreal/AirSim asset with --asset-name.\n"
            f"Attempts:\n{error_text}"
        )

    material_ok = False
    try:
        material_ok = bool(client.simSetObjectMaterialFromTexture(spawned_name, str(texture_path)))
    except Exception as exc:
        print(f"Warning: texture assignment failed: {exc}")

    final_pose = client.simGetObjectPose(spawned_name)
    print(f"Spawned fiducial marker: {spawned_name}")
    print(f"Dictionary: {dictionary_name}")
    print(f"Marker ID: {marker_id}")
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
    parser = argparse.ArgumentParser(description="Spawn an ArUco fiducial marker in AirSim.")
    parser.add_argument("--object-name", default="phase04_aruco_marker")
    parser.add_argument("--asset-name", default=None)
    parser.add_argument("--x", type=float, default=0.0)
    parser.add_argument("--y", type=float, default=0.0)
    parser.add_argument("--z", type=float, default=0.0)
    parser.add_argument("--scale-x", type=float, default=2.5)
    parser.add_argument("--scale-y", type=float, default=2.5)
    parser.add_argument("--scale-z", type=float, default=0.01)
    parser.add_argument("--offset-x", type=float, default=0.0)
    parser.add_argument("--offset-y", type=float, default=0.0)
    parser.add_argument("--under-vehicle", action="store_true")
    parser.add_argument("--dictionary-name", default="DICT_4X4_50")
    parser.add_argument("--marker-id", type=int, default=23)
    parser.add_argument("--texture-size-px", type=int, default=2048)
    parser.add_argument("--marker-size-ratio", type=float, default=0.72)
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="Create the texture image without connecting to AirSim.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spawn_fiducial_marker(
        object_name=args.object_name,
        x=args.x,
        y=args.y,
        z=args.z,
        scale_x=args.scale_x,
        scale_y=args.scale_y,
        scale_z=args.scale_z,
        dictionary_name=args.dictionary_name,
        marker_id=args.marker_id,
        asset_name=args.asset_name,
        under_vehicle=args.under_vehicle,
        offset_x=args.offset_x,
        offset_y=args.offset_y,
        texture_size_px=args.texture_size_px,
        marker_size_ratio=args.marker_size_ratio,
        generate_only=args.generate_only,
    )


if __name__ == "__main__":
    main()
