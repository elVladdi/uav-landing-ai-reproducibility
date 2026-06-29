"""Detector factory for perception backends used by control scripts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

import numpy as np

from src.perception.fiducial_marker_detector import (
    ArucoFiducialDetector,
    FiducialDetectorConfig,
)
from src.perception.landing_marker_detector import (
    DEFAULT_CONFIG_PATH,
    DetectionResult,
    DetectorConfig,
    LandingMarkerDetector,
)


class MarkerDetector(Protocol):
    def detect(self, image_bgr: np.ndarray) -> DetectionResult:
        ...

    def annotate(self, image_bgr: np.ndarray, result: DetectionResult) -> np.ndarray:
        ...


HSV_DETECTOR_NAMES = {"hsv", "hsv_color_contour", "color"}
ARUCO_DETECTOR_NAMES = {"aruco", "aruco_fiducial", "fiducial"}


def active_detector_name(config_path: Path = DEFAULT_CONFIG_PATH) -> str:
    with config_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return str(payload.get("active_detector", "hsv_color_contour"))


def build_marker_detector(
    environment: str,
    detector_name: str | None = None,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> MarkerDetector:
    name = (detector_name or active_detector_name(config_path)).strip().lower()
    if name in HSV_DETECTOR_NAMES:
        return LandingMarkerDetector(
            DetectorConfig.from_json_for_environment(environment, config_path)
        )
    if name in ARUCO_DETECTOR_NAMES:
        return ArucoFiducialDetector(
            FiducialDetectorConfig.from_json_for_environment(environment, config_path)
        )

    valid = sorted(HSV_DETECTOR_NAMES | ARUCO_DETECTOR_NAMES)
    raise ValueError(f"Unknown detector '{detector_name}'. Valid options: {', '.join(valid)}")
