"""Configuration loader for Phase 04 control experiments."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.utils.constants import PROJECT_ROOT


DEFAULT_CONTROL_CONFIG_PATH = PROJECT_ROOT / "configs" / "control_config.json"


@dataclass(frozen=True)
class Px4RuntimeConfig:
    connection_timeout_seconds: float = 5.0
    telemetry_timeout_seconds: float = 2.0
    require_local_position: bool = True


@dataclass(frozen=True)
class AirSimRuntimeConfig:
    environment: str = "AirSimNH"
    vehicle_name: str = "Drone1"
    camera_name: str = "bottom_center"
    image_type: str = "Scene"


@dataclass(frozen=True)
class OffboardConfig:
    control_frequency_hz: float = 5.0
    preflight_setpoint_seconds: float = 1.0
    takeoff_altitude_m: float = 2.0
    takeoff_acceptance_ratio: float = 0.55
    takeoff_min_acceptance_altitude_m: float = 1.0
    takeoff_timeout_seconds: float = 45.0
    hover_seconds_after_takeoff: float = 3.0
    hover_test_duration_seconds: float = 10.0
    max_forward_m_s: float = 0.35
    max_right_m_s: float = 0.35
    max_down_m_s: float = 0.20
    max_yawspeed_deg_s: float = 0.0

    @property
    def control_period_seconds(self) -> float:
        return 1.0 / max(0.1, self.control_frequency_hz)


@dataclass(frozen=True)
class VisualServoConfig:
    gain_forward_mps_per_norm_error: float = 0.25
    gain_right_mps_per_norm_error: float = 0.25
    forward_error_sign: float = -1.0
    right_error_sign: float = 1.0
    center_tolerance_norm: float = 0.08
    command_deadband_norm: float = 0.03
    min_confidence: float = 0.30
    max_missing_detections: int = 5


@dataclass(frozen=True)
class LandingConfig:
    centered_cycles_required: int = 5
    align_timeout_seconds: float = 20.0
    max_trial_seconds: float = 45.0
    descent_rate_m_s: float = 0.12
    landing_complete_altitude_m: float = 0.35
    abort_action: str = "land"


@dataclass(frozen=True)
class LoggingConfig:
    run_id_prefix: str = "phase04"
    logs_dir: Path = PROJECT_ROOT / "data" / "logs" / "phase04_control"
    figures_dir: Path = PROJECT_ROOT / "outputs" / "figures" / "phase04_control"
    save_periodic_images: bool = False


@dataclass(frozen=True)
class ControlConfig:
    px4: Px4RuntimeConfig
    airsim: AirSimRuntimeConfig
    offboard: OffboardConfig
    visual_servo: VisualServoConfig
    landing: LandingConfig
    logging: LoggingConfig
    raw: dict[str, Any]

    @classmethod
    def from_json(cls, config_path: Path = DEFAULT_CONTROL_CONFIG_PATH) -> "ControlConfig":
        with config_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        return cls(
            px4=_dataclass_from_mapping(Px4RuntimeConfig, payload.get("px4", {})),
            airsim=_dataclass_from_mapping(AirSimRuntimeConfig, payload.get("airsim", {})),
            offboard=_dataclass_from_mapping(OffboardConfig, payload.get("offboard", {})),
            visual_servo=_dataclass_from_mapping(
                VisualServoConfig,
                payload.get("visual_servo", {}),
            ),
            landing=_dataclass_from_mapping(LandingConfig, payload.get("landing", {})),
            logging=_logging_from_mapping(payload.get("logging", {})),
            raw=payload,
        )


def _dataclass_from_mapping(class_type: type, mapping: dict[str, Any]):
    allowed = class_type.__dataclass_fields__.keys()
    filtered = {key: value for key, value in mapping.items() if key in allowed}
    return class_type(**filtered)


def _logging_from_mapping(mapping: dict[str, Any]) -> LoggingConfig:
    logs_dir = Path(mapping.get("logs_dir", "data/logs/phase04_control"))
    figures_dir = Path(mapping.get("figures_dir", "outputs/figures/phase04_control"))
    if not logs_dir.is_absolute():
        logs_dir = PROJECT_ROOT / logs_dir
    if not figures_dir.is_absolute():
        figures_dir = PROJECT_ROOT / figures_dir

    return LoggingConfig(
        run_id_prefix=str(mapping.get("run_id_prefix", "phase04")),
        logs_dir=logs_dir,
        figures_dir=figures_dir,
        save_periodic_images=bool(mapping.get("save_periodic_images", False)),
    )
