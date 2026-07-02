"""AirSim bottom-camera helpers used by visual-control scripts.

The formal workflow uses the AirSimNH vehicle `Drone1` and the downward-facing
camera `bottom_center`. Images are simulator RGB frames converted to OpenCV BGR
arrays before marker detection. These helpers do not provide real-camera
validation.
"""
from __future__ import annotations

import airsim
import cv2
import numpy as np

from src.connection.airsim_client import connect_multirotor


def connect_airsim_vehicle(vehicle_name: str) -> airsim.MultirotorClient:
    """Connect to the AirSim multirotor used by the current SITL run."""
    return connect_multirotor(vehicle_name=vehicle_name)


def capture_scene_bgr(
    client: airsim.MultirotorClient,
    vehicle_name: str,
    camera_name: str,
) -> np.ndarray:
    """Capture one simulator scene image and return it as an OpenCV BGR array."""
    responses = client.simGetImages(
        [airsim.ImageRequest(camera_name, airsim.ImageType.Scene, False, False)],
        vehicle_name=vehicle_name,
    )
    if not responses:
        raise RuntimeError("AirSim did not return an image response.")

    response = responses[0]
    if response.width == 0 or response.height == 0 or not response.image_data_uint8:
        raise RuntimeError(f"Invalid image from camera '{camera_name}'.")

    img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
    img_rgb = img1d.reshape(response.height, response.width, 3)
    return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
