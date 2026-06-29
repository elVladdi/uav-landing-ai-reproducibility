"""Configuration helpers for Phase 05 T0/T1 experiments."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.utils.constants import PROJECT_ROOT


DEFAULT_PHASE05_CONFIG_PATH = PROJECT_ROOT / "configs" / "phase05_experiment_config.json"


def load_phase05_config(config_path: Path = DEFAULT_PHASE05_CONFIG_PATH) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def resolve_project_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def phase05_logging_paths(config: dict[str, Any]) -> dict[str, Path]:
    logging = config.get("logging", {})
    return {
        "raw_logs_dir": resolve_project_path(
            logging.get("raw_logs_dir", "data/logs/phase05_experiments/raw")
        ),
        "summary_dir": resolve_project_path(
            logging.get("summary_dir", "data/logs/phase05_experiments/summary")
        ),
        "figures_dir": resolve_project_path(
            logging.get("figures_dir", "outputs/figures/phase05_experiments")
        ),
    }


def get_scenario(config: dict[str, Any], scenario_id: str) -> dict[str, Any] | None:
    for scenario in config.get("scenarios", []):
        if scenario.get("scenario_id") == scenario_id:
            return scenario
    return None


def trial_metadata_from_args(args, config: dict[str, Any]) -> dict[str, object]:
    scenario = get_scenario(config, getattr(args, "scenario_id", "") or "") or {}
    return {
        "experiment_id": config.get("metadata", {}).get("experiment_id", ""),
        "treatment_pair_id": getattr(args, "treatment_pair_id", "") or "",
        "repetition": getattr(args, "repetition", "") or "",
        "planned_initial_height_m": _first_present(
            getattr(args, "planned_initial_height_m", None),
            scenario.get("initial_height_m"),
        ),
        "planned_offset_x_m": _first_present(
            getattr(args, "planned_offset_x_m", None),
            scenario.get("offset_x_m"),
        ),
        "planned_offset_y_m": _first_present(
            getattr(args, "planned_offset_y_m", None),
            scenario.get("offset_y_m"),
        ),
        "planned_yaw_deg": _first_present(
            getattr(args, "planned_yaw_deg", None),
            scenario.get("yaw_deg"),
        ),
        "marker_object_name": getattr(args, "marker_object_name", "") or "",
        "config_snapshot": "configs/phase05_experiment_config.json",
    }


def _first_present(*values):
    for value in values:
        if value is not None and value != "":
            return value
    return ""
