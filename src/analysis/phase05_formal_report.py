"""Generate Phase 05 formal tables from the curated run summary."""
from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.experiments.phase05_config import load_phase05_config, phase05_logging_paths, resolve_project_path


METRICS = [
    "final_error_m",
    "landing_time_s",
    "total_duration_s",
    "accepted_detection_rate",
    "lost_detection_count",
    "latency_ms_mean",
    "command_count",
    "descent_command_count",
    "mean_abs_error_x_norm",
    "std_error_x_norm",
]

SUMMARY_FIELDS = [
    "scenario_id",
    "treatment",
    "n",
    "landing_success_rate",
    *[field for metric in METRICS for field in (f"{metric}_mean", f"{metric}_sd", f"{metric}_min", f"{metric}_max")],
]

PAIRWISE_FIELDS = [
    "scenario_id",
    "treatment_pair_id",
    "repetition",
    "t0_run_id",
    "t1_run_id",
    "final_error_m_t0",
    "final_error_m_t1",
    "final_error_m_delta_t0_minus_t1",
    "landing_time_s_t0",
    "landing_time_s_t1",
    "landing_time_s_delta_t0_minus_t1",
    "accepted_detection_rate_t0",
    "accepted_detection_rate_t1",
    "accepted_detection_rate_delta_t1_minus_t0",
]


def read_summary(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Summary not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def accepted_rows(rows: list[dict[str, str]], scenario_ids: set[str] | None = None) -> list[dict[str, str]]:
    accepted = [row for row in rows if row.get("curation_status") == "accepted"]
    if scenario_ids is None:
        return accepted
    return [row for row in accepted if row.get("scenario_id", "") in scenario_ids]


def scenario_treatment_summary(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row.get("scenario_id", ""), row.get("treatment", ""))].append(row)

    output: list[dict[str, object]] = []
    for (scenario_id, treatment), group_rows in sorted(groups.items()):
        item: dict[str, object] = {
            "scenario_id": scenario_id,
            "treatment": treatment,
            "n": len(group_rows),
            "landing_success_rate": _mean(1.0 if _truthy(row.get("landing_success")) else 0.0 for row in group_rows),
        }
        for metric in METRICS:
            values = _numbers(row.get(metric) for row in group_rows)
            item[f"{metric}_mean"] = _mean(values)
            item[f"{metric}_sd"] = _stdev(values)
            item[f"{metric}_min"] = min(values) if values else ""
            item[f"{metric}_max"] = max(values) if values else ""
        output.append(item)
    return output


def pairwise_differences(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        key = (
            row.get("scenario_id", ""),
            row.get("treatment_pair_id", ""),
            row.get("repetition", ""),
        )
        groups[key][row.get("treatment", "")] = row

    output: list[dict[str, object]] = []
    for (scenario_id, pair_id, repetition), group in sorted(groups.items()):
        t0 = group.get("T0")
        t1 = group.get("T1")
        if not t0 or not t1:
            continue
        t0_error = _float_or_none(t0.get("final_error_m"))
        t1_error = _float_or_none(t1.get("final_error_m"))
        t0_time = _float_or_none(t0.get("landing_time_s"))
        t1_time = _float_or_none(t1.get("landing_time_s"))
        t0_detection = _float_or_none(t0.get("accepted_detection_rate"))
        t1_detection = _float_or_none(t1.get("accepted_detection_rate"))
        output.append(
            {
                "scenario_id": scenario_id,
                "treatment_pair_id": pair_id,
                "repetition": repetition,
                "t0_run_id": t0.get("run_id", ""),
                "t1_run_id": t1.get("run_id", ""),
                "final_error_m_t0": _blank_if_none(t0_error),
                "final_error_m_t1": _blank_if_none(t1_error),
                "final_error_m_delta_t0_minus_t1": _delta(t0_error, t1_error),
                "landing_time_s_t0": _blank_if_none(t0_time),
                "landing_time_s_t1": _blank_if_none(t1_time),
                "landing_time_s_delta_t0_minus_t1": _delta(t0_time, t1_time),
                "accepted_detection_rate_t0": _blank_if_none(t0_detection),
                "accepted_detection_rate_t1": _blank_if_none(t1_detection),
                "accepted_detection_rate_delta_t1_minus_t0": _delta(t1_detection, t0_detection),
            }
        )
    return output


def completion_rows(rows: list[dict[str, str]], config: dict[str, object]) -> list[dict[str, object]]:
    repetitions = int(config.get("formal_design", {}).get("repetitions_per_treatment", 10))
    accepted = accepted_rows(rows, _formal_scenario_ids(config))
    counts = Counter((row.get("scenario_id", ""), row.get("treatment", "")) for row in accepted)
    output: list[dict[str, object]] = []
    for scenario in config.get("scenarios", []):
        scenario_id = str(scenario.get("scenario_id", ""))
        for treatment in ("T0", "T1"):
            count = counts[(scenario_id, treatment)]
            output.append(
                {
                    "scenario_id": scenario_id,
                    "treatment": treatment,
                    "accepted_runs": count,
                    "expected_runs": repetitions,
                    "missing_runs": max(0, repetitions - count),
                    "complete": count >= repetitions,
                }
            )
    return output


def write_markdown_report(
    path: Path,
    rows: list[dict[str, str]],
    accepted: list[dict[str, str]],
    completion: list[dict[str, object]],
    pairwise: list[dict[str, object]],
    config: dict[str, object],
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    curation_counts = Counter(row.get("curation_status", "") for row in rows)
    expected_total = int(config.get("formal_design", {}).get("minimum_total_runs", 160))
    all_accepted = accepted_rows(rows)
    formal_ids = _formal_scenario_ids(config)
    non_formal_accepted = [row for row in all_accepted if row.get("scenario_id", "") not in formal_ids]
    complete_cells = sum(1 for row in completion if row["complete"])
    total_cells = len(completion)
    deltas = _numbers(row.get("final_error_m_delta_t0_minus_t1") for row in pairwise)
    times = _numbers(row.get("landing_time_s_delta_t0_minus_t1") for row in pairwise)

    with path.open("w", encoding="utf-8", newline="") as file:
        file.write("# Phase 05 Formal Analysis Report\n\n")
        file.write("Generated from curated Phase 05 logs.\n\n")
        file.write("## Completion\n\n")
        file.write(f"- Expected formal runs: {expected_total}\n")
        file.write(f"- Accepted formal runs: {len(accepted)}\n")
        file.write(f"- Accepted non-formal runs excluded from this report: {len(non_formal_accepted)}\n")
        file.write(f"- Completed scenario/treatment cells: {complete_cells}/{total_cells}\n")
        for status, count in sorted(curation_counts.items()):
            file.write(f"- `{status or 'blank'}`: {count}\n")

        file.write("\n## Pairwise Practical Effect\n\n")
        file.write(f"- Accepted T0/T1 pairs: {len(pairwise)}\n")
        file.write(f"- Mean final-error delta T0-T1: {_format_number(_mean(deltas))} m\n")
        file.write(f"- SD final-error delta T0-T1: {_format_number(_stdev(deltas))} m\n")
        file.write(f"- Cohen dz final-error delta: {_format_number(_cohen_dz(deltas))}\n")
        file.write(f"- Mean landing-time delta T0-T1: {_format_number(_mean(times))} s\n")

        file.write("\n## Missing Cells\n\n")
        missing = [row for row in completion if row["missing_runs"]]
        if not missing:
            file.write("No missing scenario/treatment cells.\n")
        else:
            file.write("| Scenario | Treatment | Accepted | Expected | Missing |\n")
            file.write("|---|---:|---:|---:|---:|\n")
            for row in missing:
                file.write(
                    f"| {row['scenario_id']} | {row['treatment']} | "
                    f"{row['accepted_runs']} | {row['expected_runs']} | {row['missing_runs']} |\n"
                )
    return path


def generate_report(args: argparse.Namespace) -> dict[str, Path]:
    config = load_phase05_config()
    rows = read_summary(args.summary)
    accepted = accepted_rows(rows, _formal_scenario_ids(config))
    summary_rows = scenario_treatment_summary(accepted)
    pairwise_rows = pairwise_differences(accepted)
    completion = completion_rows(rows, config)

    paths = {
        "accepted": write_csv(args.output_dir / "phase05_accepted_runs.csv", accepted, list(rows[0].keys()) if rows else []),
        "scenario_summary": write_csv(args.output_dir / "phase05_scenario_treatment_summary.csv", summary_rows, SUMMARY_FIELDS),
        "pairwise": write_csv(args.output_dir / "phase05_pairwise_differences.csv", pairwise_rows, PAIRWISE_FIELDS),
        "completion": write_csv(
            args.output_dir / "phase05_completion_check.csv",
            completion,
            ["scenario_id", "treatment", "accepted_runs", "expected_runs", "missing_runs", "complete"],
        ),
        "report": write_markdown_report(
            args.output_dir / "phase05_formal_report.md",
            rows,
            accepted,
            completion,
            pairwise_rows,
            config,
        ),
    }
    return paths


def _formal_scenario_ids(config: dict[str, object]) -> set[str]:
    return {str(scenario.get("scenario_id", "")) for scenario in config.get("scenarios", [])}


def _numbers(values: Iterable[object]) -> list[float]:
    numbers = []
    for value in values:
        number = _float_or_none(value)
        if number is not None:
            numbers.append(number)
    return numbers


def _float_or_none(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def _blank_if_none(value: float | None) -> float | str:
    return "" if value is None else value


def _delta(left: float | None, right: float | None) -> float | str:
    return "" if left is None or right is None else left - right


def _mean(values: Iterable[float]) -> float | str:
    values = list(values)
    return statistics.fmean(values) if values else ""


def _stdev(values: list[float]) -> float | str:
    return statistics.stdev(values) if len(values) >= 2 else ""


def _cohen_dz(values: list[float]) -> float | str:
    sd = _stdev(values)
    mean = _mean(values)
    if sd in ("", 0.0) or mean == "":
        return ""
    return float(mean) / float(sd)


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "ok"}


def _format_number(value: object) -> str:
    number = _float_or_none(value)
    return "NA" if number is None else f"{number:.4f}"


def parse_args() -> argparse.Namespace:
    config = load_phase05_config()
    paths = phase05_logging_paths(config)
    parser = argparse.ArgumentParser(description="Generate Phase 05 formal analysis tables.")
    parser.add_argument("--summary", type=Path, default=paths["summary_dir"] / "phase05_run_summary.csv")
    parser.add_argument("--output-dir", type=Path, default=resolve_project_path("outputs/tables/phase05_experiments"))
    return parser.parse_args()


def main() -> None:
    paths = generate_report(parse_args())
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
