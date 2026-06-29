"""Prueba de captura de cámara inferior en AirSim.

Uso desde la raíz del proyecto:
    python src/perception/camera_test.py

Guarda una imagen RGB de la cámara bottom_center en data/raw/.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import airsim
import cv2
import numpy as np

from src.connection.airsim_client import connect_multirotor
from src.utils.constants import BOTTOM_CAMERA_NAME, RAW_DIR, VEHICLE_NAME


def capture_scene_image(camera_name: str = BOTTOM_CAMERA_NAME) -> Path:
    client = connect_multirotor(vehicle_name=VEHICLE_NAME)

    responses = client.simGetImages(
        [airsim.ImageRequest(camera_name, airsim.ImageType.Scene, False, False)],
        vehicle_name=VEHICLE_NAME,
    )

    if not responses:
        raise RuntimeError("AirSim no devolvió respuesta de imagen.")

    response = responses[0]
    if response.width == 0 or response.height == 0 or not response.image_data_uint8:
        raise RuntimeError(
            f"Imagen inválida desde la cámara '{camera_name}'. "
            "Verifica que esa cámara exista en settings.json."
        )

    img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
    img_rgb = img1d.reshape(response.height, response.width, 3)

    # OpenCV guarda en BGR; convertimos desde RGB para que los colores sean correctos.
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = RAW_DIR / f"capture_{camera_name}_{timestamp}.png"
    cv2.imwrite(str(output_path), img_bgr)

    print(f"Imagen guardada: {output_path}")
    print(f"Resolución: {response.width} x {response.height}")
    return output_path


def main() -> None:
    capture_scene_image()


if __name__ == "__main__":
    main()
