"""CSV logging helpers for Phase 05 experimental trials."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from src.logging.experiment_logger import PHASE04_FIELDNAMES


PHASE05_EXTRA_FIELDNAMES = [
    "experiment_id",
    "treatment_pair_id",
    "repetition",
    "planned_initial_height_m",
    "planned_offset_x_m",
    "planned_offset_y_m",
    "planned_yaw_deg",
    "marker_object_name",
    "marker_x_m",
    "marker_y_m",
    "marker_z_m",
    "final_error_x_m",
    "final_error_y_m",
    "final_error_m",
    "landing_success",
    "abort_reason",
    "config_snapshot",
]

PHASE05_FIELDNAMES = PHASE04_FIELDNAMES + [
    field for field in PHASE05_EXTRA_FIELDNAMES if field not in PHASE04_FIELDNAMES
]


class Phase05CsvLogger:
    """CSV writer with Phase 04 loop fields plus Phase 05 design metadata."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.output_path.open("w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(
            self._file,
            fieldnames=PHASE05_FIELDNAMES,
            extrasaction="ignore",
        )
        self._writer.writeheader()

    def write(self, row: dict[str, Any]) -> None:
        normalized = {field: "" for field in PHASE05_FIELDNAMES}
        normalized.update(row)
        self._writer.writerow(normalized)
        self._file.flush()

    def close(self) -> None:
        self._file.close()

    def __enter__(self) -> "Phase05CsvLogger":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()
