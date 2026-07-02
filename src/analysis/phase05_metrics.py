"""Build the Phase 05 run-level metrics table from execution logs.

Inputs:
    - Raw or summary CSV logs written by the Phase 05 control scripts.
    - `configs/phase05_experiment_config.json` for formal curation rules.

Outputs:
    - A one-row-per-run CSV summary used by Phase 05 and Phase 06 analyses.

Reproducibility role:
    Converts simulator/control/perception logs into a curated analytical table
    with stable identifiers, scenario metadata, terminal metrics, visual
    availability metrics, and curation labels.

Scope:
    Analytical reproduction only. Final error is derived from simulator-side
    AirSim vehicle-marker poses, and terminal state is a protocol transition,
    not physical touchdown validation or real-flight evidence.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.experiments.phase05_config import load_phase05_config, phase05_logging_paths


SUMMARY_FIELDS = [
    "run_id",
    "source_file",
    "phase",
    "treatment",
    "scenario_id",
    "experiment_id",
    "treatment_pair_id",
    "repetition",
    "curation_status",
    "curation_reason",
    "superseded_by",
    "planned_initial_height_m",
    "planned_offset_x_m",
    "planned_offset_y_m",
    "planned_yaw_deg",
    "visual_samples",
    "accepted_detections",
    "accepted_detection_rate",
    "lost_detection_count",
    "latency_ms_mean",
    "latency_ms_max",
    "mean_abs_error_x_norm",
    "std_error_x_norm",
    "mean_abs_error_y_norm",
    "std_error_y_norm",
    "command_count",
    "descent_command_count",
    "max_abs_horizontal_command_m_s",
    "landing_time_s",
    "total_duration_s",
    "start_altitude_m",
    "last_visual_altitude_m",
    "final_error_x_m",
    "final_error_y_m",
    "final_error_m",
    "landing_success",
    "landing_threshold_reached",
    "aborted",
    "abort_reason",
    "terminal_event",
    "terminal_mode",
    "terminal_armed",
    "terminal_status",
    "status",
    "notes",
]

def _relative_project_path(path: Path) -> str:
    """Return a stable project-relative path for traceable CSV provenance."""
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()

def summarize_file(csv_path: Path) -> dict[str, object]:
    """Summarize a single Phase 05 execution log into one analytical row.

    The summary preserves treatment, scenario, repetition, pair identifiers,
    visual-sample counts, command activity, terminal state, and final simulator
    landing error. T0 logs may include passive perception, but those detections
    do not imply visual lateral correction in the baseline treatment.
    """
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        return {"source_file": _relative_project_path(csv_path), "status": "empty"}

    visual_rows = [row for row in rows if row.get("event") in {"visual_servo", "baseline_descent"}]
    summary_rows = [row for row in rows if row.get("event") == "summary"]
    land_complete_rows = [row for row in rows if row.get("event") == "land_complete"]
    terminal = (land_complete_rows or summary_rows or rows)[-1]
    first = rows[0]
    last_visual = visual_rows[-1] if visual_rows else terminal

    accepted_count = sum(_truthy(row.get("accepted_detection")) for row in visual_rows)
    command_count = sum(_truthy(row.get("command_sent")) for row in visual_rows)
    descent_command_count = sum(
        1 for row in visual_rows if _float_or_none(row.get("command_down_m_s")) not in (None, 0.0)
    )
    lost_detection_count = sum(
        1 for row in visual_rows if row.get("detected") != "" and not _truthy(row.get("accepted_detection"))
    )
    latencies = _numbers(row.get("latency_ms") for row in visual_rows)
    err_x = _numbers(row.get("error_x_norm") for row in visual_rows)
    err_y = _numbers(row.get("error_y_norm") for row in visual_rows)
    landing_time = _float_or_none(last_visual.get("elapsed_seconds"))
    total_duration = _float_or_none(terminal.get("elapsed_seconds"))
    landing_success = _derive_landing_success(summary_rows, terminal)
    landing_threshold_reached = _derive_landing_threshold(summary_rows, terminal)
    aborted = any(row.get("status") == "abort" or "aborted=True" in row.get("notes", "") for row in rows)
    horizontal_commands = _numbers(
        value
        for row in visual_rows
        for value in (row.get("command_forward_m_s"), row.get("command_right_m_s"))
    )

    return {
        "run_id": first.get("run_id", ""),
        "source_file": _relative_project_path(csv_path),
        "phase": first.get("phase", ""),
        "treatment": first.get("treatment", ""),
        "scenario_id": first.get("scenario_id", ""),
        "experiment_id": first.get("experiment_id", ""),
        "treatment_pair_id": first.get("treatment_pair_id", ""),
        "repetition": first.get("repetition", ""),
        "curation_status": "",
        "curation_reason": "",
        "superseded_by": "",
        "planned_initial_height_m": first.get("planned_initial_height_m", ""),
        "planned_offset_x_m": first.get("planned_offset_x_m", ""),
        "planned_offset_y_m": first.get("planned_offset_y_m", ""),
        "planned_yaw_deg": first.get("planned_yaw_deg", ""),
        "visual_samples": len(visual_rows),
        "accepted_detections": accepted_count,
        "accepted_detection_rate": _ratio(accepted_count, len(visual_rows)),
        "lost_detection_count": lost_detection_count,
        "latency_ms_mean": _mean(latencies),
        "latency_ms_max": max(latencies) if latencies else "",
        "mean_abs_error_x_norm": _mean(abs(value) for value in err_x),
        "std_error_x_norm": _stdev(err_x),
        "mean_abs_error_y_norm": _mean(abs(value) for value in err_y),
        "std_error_y_norm": _stdev(err_y),
        "command_count": command_count,
        "descent_command_count": descent_command_count,
        "max_abs_horizontal_command_m_s": max((abs(value) for value in horizontal_commands), default=""),
        "landing_time_s": landing_time if landing_time is not None else "",
        "total_duration_s": total_duration if total_duration is not None else "",
        "start_altitude_m": _float_or_blank(first.get("altitude_m")),
        "last_visual_altitude_m": _float_or_blank(last_visual.get("altitude_m")),
        "final_error_x_m": terminal.get("final_error_x_m", ""),
        "final_error_y_m": terminal.get("final_error_y_m", ""),
        "final_error_m": terminal.get("final_error_m", ""),
        "landing_success": landing_success,
        "landing_threshold_reached": landing_threshold_reached,
        "aborted": aborted,
        "abort_reason": terminal.get("abort_reason", ""),
        "terminal_event": terminal.get("event", ""),
        "terminal_mode": terminal.get("flight_mode", ""),
        "terminal_armed": _bool_or_blank(terminal.get("armed")),
        "terminal_status": terminal.get("status", ""),
        "status": terminal.get("status", ""),
        "notes": terminal.get("notes", ""),
    }


def summarize_directory(raw_logs_dir: Path, output_path: Path, curation: dict[str, object] | None = None) -> Path:
    """Summarize all Phase 05 CSV logs and apply reproducibility curation."""
    files = sorted(raw_logs_dir.glob("phase05_*_*.csv"))
    summaries = [summarize_file(csv_path) for csv_path in files]
    apply_curation(summaries, curation or {})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SUMMARY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(summaries)
    return output_path


def apply_curation(rows: list[dict[str, object]], curation: dict[str, object]) -> None:
    """Assign reproducibility-oriented curation labels to run summaries.

    The curation rules exclude diagnostic, aborted, incomplete, superseded, or
    non-comparable runs before paired T0/T1 analysis. Changing these rules would
    change the public analytical dataset and therefore requires matching updates
    to the methodology documentation and article reproducibility statement.
    """
    rules = curation.get("rules", {}) if isinstance(curation.get("rules", {}), dict) else {}
    superseded = {
        entry.get("run_id"): entry
        for entry in curation.get("superseded_runs", [])
        if isinstance(entry, dict) and entry.get("run_id")
    }

    for row in rows:
        status, reason = _base_curation_status(row, rules)
        superseded_by = ""
        run_id = str(row.get("run_id", ""))
        if run_id in superseded:
            entry = superseded[run_id]
            status = "superseded"
            reason = str(entry.get("reason", "Run superseded by a corrective repetition."))
            superseded_by = str(entry.get("superseded_by", ""))
        row["curation_status"] = status
        row["curation_reason"] = reason
        row["superseded_by"] = superseded_by

    if curation.get("duplicate_policy") == "exclude_unresolved_duplicates":
        _exclude_unresolved_duplicates(rows)


def _base_curation_status(row: dict[str, object], rules: dict[str, object]) -> tuple[str, str]:
    """Evaluate one run against the Phase 05 inclusion/exclusion criteria."""
    required_phase = str(rules.get("required_phase", "fase05"))
    valid_treatments = set(rules.get("valid_treatments", ["T0", "T1"]))
    required_metadata = rules.get(
        "required_metadata",
        ["scenario_id", "experiment_id", "treatment_pair_id", "repetition"],
    )

    if row.get("status") == "empty":
        return "excluded", "Empty log file."
    if row.get("phase") != required_phase:
        return "excluded", f"Unexpected phase: {row.get('phase', '')}."
    if row.get("treatment") not in valid_treatments:
        return "excluded", f"Unexpected treatment: {row.get('treatment', '')}."

    for field in required_metadata:
        if row.get(str(field)) in (None, ""):
            return "excluded", f"Missing required metadata: {field}."

    scenario_id = str(row.get("scenario_id", ""))
    if scenario_id in _string_list(rules.get("excluded_scenario_ids", [])):
        return "excluded", f"Diagnostic or excluded scenario: {scenario_id}."
    for suffix in _string_list(rules.get("excluded_scenario_suffixes", [])):
        if suffix and scenario_id.endswith(suffix):
            return "excluded", f"Diagnostic or excluded scenario suffix: {suffix}."

    if rules.get("require_no_abort", True) and _truthy(row.get("aborted")):
        return "excluded", "Run marked as aborted."
    if rules.get("require_land_complete", True) and row.get("terminal_event") != "land_complete":
        return "excluded", f"Terminal event is not land_complete: {row.get('terminal_event', '')}."
    if rules.get("require_terminal_disarmed", True):
        terminal_armed = row.get("terminal_armed")
        if terminal_armed in (None, ""):
            return "excluded", "Terminal armed state is unavailable."
        if _truthy(terminal_armed):
            return "excluded", "Vehicle remained armed at terminal event."
    if rules.get("require_landing_success", True) and not _truthy(row.get("landing_success")):
        return "excluded", "landing_success is false."

    treatment = row.get("treatment")
    if treatment == "T1" and rules.get("require_t1_landing_threshold", True):
        if not _truthy(row.get("landing_threshold_reached")):
            return "excluded", "T1 did not reach the landing threshold in the visual loop."

    if treatment == "T0":
        max_horizontal_command = _float_or_none(str(row.get("max_abs_horizontal_command_m_s", "")))
        max_allowed = _float_or_none(
            str(rules.get("max_t0_horizontal_command_m_s", rules.get("max_t0_lateral_command_m_s", 0.001)))
        )
        if (
            max_horizontal_command is not None
            and max_allowed is not None
            and max_horizontal_command > max_allowed
        ):
            return "excluded", "T0 used horizontal correction commands above the allowed tolerance."

    return "accepted", "Meets Phase 05 inclusion criteria."


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


def _exclude_unresolved_duplicates(rows: list[dict[str, object]]) -> None:
    groups: dict[tuple[str, str, str, str, str], list[dict[str, object]]] = {}
    for row in rows:
        if row.get("curation_status") != "accepted":
            continue
        key = (
            str(row.get("experiment_id", "")),
            str(row.get("scenario_id", "")),
            str(row.get("treatment", "")),
            str(row.get("treatment_pair_id", "")),
            str(row.get("repetition", "")),
        )
        groups.setdefault(key, []).append(row)

    for duplicates in groups.values():
        if len(duplicates) < 2:
            continue
        for row in duplicates:
            row["curation_status"] = "excluded"
            row["curation_reason"] = (
                "Unresolved duplicate for experiment/scenario/treatment/pair/repetition; "
                "declare one run as superseded before comparative analysis."
            )


def _derive_landing_success(summary_rows: list[dict[str, str]], terminal: dict[str, str]) -> bool:
    for row in reversed(summary_rows):
        if row.get("landing_success") != "":
            return _truthy(row.get("landing_success"))
        notes = row.get("notes", "")
        if "landing_threshold_reached=True" in notes and "aborted=True" not in notes:
            return True
    if terminal.get("landing_success") != "":
        return _truthy(terminal.get("landing_success"))
    return terminal.get("event") == "land_complete" and not _truthy(terminal.get("armed"))


def _derive_landing_threshold(summary_rows: list[dict[str, str]], terminal: dict[str, str]) -> bool | str:
    for row in reversed(summary_rows):
        if row.get("landing_threshold_reached") not in (None, ""):
            return _truthy(row.get("landing_threshold_reached"))
        value = _note_value(row.get("notes", ""), "landing_threshold_reached")
        if value != "":
            return _truthy(value)
    if terminal.get("landing_threshold_reached") not in (None, ""):
        return _truthy(terminal.get("landing_threshold_reached"))
    value = _note_value(terminal.get("notes", ""), "landing_threshold_reached")
    return _truthy(value) if value != "" else ""


def _numbers(values: Iterable[str | None]) -> list[float]:
    result = []
    for value in values:
        number = _float_or_none(value)
        if number is not None:
            result.append(number)
    return result


def _float_or_none(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def _float_or_blank(value: str | None) -> float | str:
    number = _float_or_none(value)
    return "" if number is None else number


def _mean(values: Iterable[float]) -> float | str:
    values = list(values)
    return statistics.fmean(values) if values else ""


def _stdev(values: list[float]) -> float | str:
    return statistics.stdev(values) if len(values) >= 2 else ""


def _ratio(numerator: int, denominator: int) -> float | str:
    return numerator / denominator if denominator else ""


def _note_value(notes: str | None, key: str) -> str:
    for part in str(notes or "").split(";"):
        if "=" not in part:
            continue
        name, value = part.split("=", 1)
        if name.strip() == key:
            return value.strip()
    return ""


def _bool_or_blank(value: str | None) -> bool | str:
    return "" if value in (None, "") else _truthy(value)


def _truthy(value: str | None) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "ok"}


def parse_args() -> argparse.Namespace:
    config = load_phase05_config()
    paths = phase05_logging_paths(config)
    parser = argparse.ArgumentParser(description="Summarize Phase 05 raw CSV logs.")
    parser.add_argument("--raw-logs-dir", type=Path, default=paths["raw_logs_dir"])
    parser.add_argument(
        "--output",
        type=Path,
        default=paths["summary_dir"] / "phase05_run_summary.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_phase05_config()
    output_path = summarize_directory(args.raw_logs_dir, args.output, config.get("curation", {}))
    print(f"Summary written to: {output_path}")


if __name__ == "__main__":
    main()
