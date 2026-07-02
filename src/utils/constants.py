"""Shared constants for the UAV Landing AI reproducibility package.

The formal simulation workflow assumes AirSimNH vehicle `Drone1` and the
downward-facing camera `bottom_center`. These constants centralize names and
repository-relative output paths used by diagnostic and experimental scripts.
"""
from pathlib import Path

# Vehicle name defined in the local AirSim settings.
VEHICLE_NAME = "Drone1"

# Camera names defined in AirSim settings.
BOTTOM_CAMERA_NAME = "bottom_center"
FRONT_CAMERA_NAME = "front_center"

# Repository-relative paths used by reproducibility scripts.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = DATA_DIR / "logs"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
VIDEOS_DIR = OUTPUTS_DIR / "videos"
REPORTS_DIR = OUTPUTS_DIR / "reports"
PHASE03_PROCESSED_DIR = PROCESSED_DIR / "phase03_perception"
PHASE03_FIGURES_DIR = FIGURES_DIR / "phase03_perception"

# Diagnostic defaults. AirSim uses negative Z for altitude above ground.
DEFAULT_ALTITUDE_M = 5.0
DEFAULT_SPEED_MPS = 2.0
DEFAULT_HOVER_SECONDS = 2.0
