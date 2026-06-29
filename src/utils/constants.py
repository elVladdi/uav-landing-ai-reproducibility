"""Constantes del proyecto UAV Landing AI.

Ajusta estos valores si cambias el nombre del vehículo, cámara o rutas.
"""
from pathlib import Path

# Nombre definido en Documents/AirSim/settings.json
VEHICLE_NAME = "Drone1"

# Cámara inferior definida en settings.json
BOTTOM_CAMERA_NAME = "bottom_center"
FRONT_CAMERA_NAME = "front_center"

# Rutas base del proyecto
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

# Parámetros de prueba
DEFAULT_ALTITUDE_M = 5.0  # AirSim usa Z negativo para altura
DEFAULT_SPEED_MPS = 2.0
DEFAULT_HOVER_SECONDS = 2.0
