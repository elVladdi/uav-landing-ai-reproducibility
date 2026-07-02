"""Build perception backends used by control and validation scripts.

The HSV detector supports early color-marker validation, while the ArUco
fiducial detector is the relevant backend for the formal T1 workflow. Both
return the same `DetectionResult` schema so logging and visual control can
consume center-error fields consistently.
"""
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
    """Protocol shared by HSV and ArUco marker detectors."""
    def detect(self, image_bgr: np.ndarray) -> DetectionResult:
        ...

    def annotate(self, image_bgr: np.ndarray, result: DetectionResult) -> np.ndarray:
        ...


HSV_DETECTOR_NAMES = {"hsv", "hsv_color_contour", "color"}
ARUCO_DETECTOR_NAMES = {"aruco", "aruco_fiducial", "fiducial"}


def active_detector_name(config_path: Path = DEFAULT_CONFIG_PATH) -> str:
    """Read the configured active detector name from the perception snapshot."""
    with config_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return str(payload.get("active_detector", "hsv_color_contour"))


def build_marker_detector(
    environment: str,
    detector_name: str | None = None,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> MarkerDetector:
    """Construct the requested detector for the AirSimNH environment."""
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
