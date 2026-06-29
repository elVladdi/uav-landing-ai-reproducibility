"""AirSim camera helpers used by Phase 04 control scripts."""
from __future__ import annotations

import airsim
import cv2
import numpy as np

from src.connection.airsim_client import connect_multirotor


def connect_airsim_vehicle(vehicle_name: str) -> airsim.MultirotorClient:
    return connect_multirotor(vehicle_name=vehicle_name)


def capture_scene_bgr(
    client: airsim.MultirotorClient,
    vehicle_name: str,
    camera_name: str,
) -> np.ndarray:
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
