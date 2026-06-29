"""CSV logging helpers for Phase 04 control experiments."""
from __future__ import annotations

import csv
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


PHASE04_FIELDNAMES = [
    "run_id",
    "timestamp",
    "phase",
    "treatment",
    "scenario_id",
    "sample_idx",
    "elapsed_seconds",
    "controller_phase",
    "controller_reason",
    "event",
    "detector_method",
    "detected",
    "accepted_detection",
    "centered",
    "confidence",
    "error_x_norm",
    "error_y_norm",
    "error_x_px",
    "error_y_px",
    "command_forward_m_s",
    "command_right_m_s",
    "command_down_m_s",
    "command_yawspeed_deg_s",
    "command_sent",
    "armed",
    "flight_mode",
    "health_local_position_ok",
    "north_m",
    "east_m",
    "down_m",
    "altitude_m",
    "velocity_north_m_s",
    "velocity_east_m_s",
    "velocity_down_m_s",
    "airsim_position_x",
    "airsim_position_y",
    "airsim_position_z",
    "airsim_velocity_x",
    "airsim_velocity_y",
    "airsim_velocity_z",
    "airsim_landed_state",
    "latency_ms",
    "status",
    "detection_notes",
    "notes",
]


def build_run_id(prefix: str) -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"


class Phase04CsvLogger:
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.output_path.open("w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(
            self._file,
            fieldnames=PHASE04_FIELDNAMES,
            extrasaction="ignore",
        )
        self._writer.writeheader()

    def write(self, row: dict[str, Any]) -> None:
        normalized = {field: "" for field in PHASE04_FIELDNAMES}
        normalized.update(row)
        self._writer.writerow(normalized)
        self._file.flush()

    def close(self) -> None:
        self._file.close()

    def __enter__(self) -> "Phase04CsvLogger":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def dataclass_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return {}
