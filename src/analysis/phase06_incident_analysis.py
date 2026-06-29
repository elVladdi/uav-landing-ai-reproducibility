"""Generate Phase 06 incident and error-source analysis."""
from __future__ import annotations

import argparse
import csv
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ACCEPTED_RUNS_PATH = Path("outputs/tables/phase05_experiments/phase05_accepted_runs.csv")
OUTPUT_DIR = Path("outputs/tables/phase06_analysis")

SUMMARY_FIELDS = [
    "scope",
    "scenario_short",
    "scenario_id",
    "treatment",
    "n",
    "landing_success_rate",
    "abort_rate",
    "lost_detection_mean",
    "lost_detection_max",
    "accepted_detection_rate_mean",
    "latency_ms_mean_mean",
    "latency_ms_mean_max",
    "latency_ms_max_mean",
    "latency_ms_max_max",
    "final_error_m_mean",
    "final_error_m_max",
    "landing_time_s_mean",
    "landing_time_s_max",
    "max_abs_horizontal_command_m_s_mean",
    "max_abs_horizontal_command_m_s_max",
    "std_error_x_norm_mean",
    "std_error_y_norm_mean",
]

EXTREME_FIELDS = [
    "category",
    "rank",
    "run_id",
    "scenario_short",
    "scenario_id",
    "treatment",
    "treatment_pair_id",
    "repetition",
    "value",
    "threshold",
    "final_error_m",
    "landing_time_s",
    "accepted_detection_rate",
    "lost_detection_count",
    "latency_ms_mean",
    "latency_ms_max",
    "max_abs_horizontal_command_m_s",
    "terminal_event",
    "terminal_status",
    "aborted",
    "notes",
]

COUNTS_FIELDS = [
    "scope",
    "scenario_short",
    "scenario_id",
    "treatment",
    "terminal_event",
    "terminal_status",
    "aborted",
    "count",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Input not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def resolve_project_path(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def canonical_scenario(value: str) -> str:
    match = re.search(r"S(\d{2})", value.upper())
    if match:
        return f"S{match.group(1)}"
    return value.upper()


def float_or_none(value: object) -> float | None:
    try:
        if value in (None, ""):
            return None
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None
    except (TypeError, ValueError):
        return None


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "si"}


def values(rows: list[dict[str, str]], field: str) -> list[float]:
    return [value for value in (float_or_none(row.get(field)) for row in rows) if value is not None]


def mean(rows: list[dict[str, str]], field: str) -> object:
    data = values(rows, field)
    return statistics.mean(data) if data else ""


def maximum(rows: list[dict[str, str]], field: str) -> object:
    data = values(rows, field)
    return max(data) if data else ""


def accepted_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("curation_status") == "accepted"]


def grouped_summary(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    group_specs: list[tuple[str, dict[tuple[str, str, str], list[dict[str, str]]]]] = []

    by_treatment: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    by_scenario_treatment: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        scenario_id = row.get("scenario_id", "")
        scenario_short = canonical_scenario(scenario_id)
        treatment = row.get("treatment", "")
        by_treatment[("ALL", "", treatment)].append(row)
        by_scenario_treatment[(scenario_short, scenario_id, treatment)].append(row)

    group_specs.append(("treatment", by_treatment))
    group_specs.append(("scenario_treatment", by_scenario_treatment))

    for scope, groups in group_specs:
        for (scenario_short, scenario_id, treatment), group_rows in sorted(groups.items()):
            n = len(group_rows)
            output.append(
                {
                    "scope": scope,
                    "scenario_short": scenario_short,
                    "scenario_id": scenario_id,
                    "treatment": treatment,
                    "n": n,
                    "landing_success_rate": ratio(
                        sum(1 for row in group_rows if truthy(row.get("landing_success"))), n
                    ),
                    "abort_rate": ratio(sum(1 for row in group_rows if truthy(row.get("aborted"))), n),
                    "lost_detection_mean": mean(group_rows, "lost_detection_count"),
                    "lost_detection_max": maximum(group_rows, "lost_detection_count"),
                    "accepted_detection_rate_mean": mean(group_rows, "accepted_detection_rate"),
                    "latency_ms_mean_mean": mean(group_rows, "latency_ms_mean"),
                    "latency_ms_mean_max": maximum(group_rows, "latency_ms_mean"),
                    "latency_ms_max_mean": mean(group_rows, "latency_ms_max"),
                    "latency_ms_max_max": maximum(group_rows, "latency_ms_max"),
                    "final_error_m_mean": mean(group_rows, "final_error_m"),
                    "final_error_m_max": maximum(group_rows, "final_error_m"),
                    "landing_time_s_mean": mean(group_rows, "landing_time_s"),
                    "landing_time_s_max": maximum(group_rows, "landing_time_s"),
                    "max_abs_horizontal_command_m_s_mean": mean(
                        group_rows, "max_abs_horizontal_command_m_s"
                    ),
                    "max_abs_horizontal_command_m_s_max": maximum(
                        group_rows, "max_abs_horizontal_command_m_s"
                    ),
                    "std_error_x_norm_mean": mean(group_rows, "std_error_x_norm"),
                    "std_error_y_norm_mean": mean(group_rows, "std_error_y_norm"),
                }
            )
    return output


def ratio(numerator: int, denominator: int) -> object:
    return numerator / denominator if denominator else ""


def percentile(data: list[float], probability: float) -> float:
    data = sorted(data)
    if not data:
        return 0.0
    if len(data) == 1:
        return data[0]
    position = (len(data) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return data[int(position)]
    fraction = position - lower
    return data[lower] + (data[upper] - data[lower]) * fraction


def extreme_runs(rows: list[dict[str, str]], top_n: int = 10) -> list[dict[str, object]]:
    specs = [
        ("highest_final_error", "final_error_m", True),
        ("longest_landing_time", "landing_time_s", True),
        ("lowest_detection_rate", "accepted_detection_rate", False),
        ("highest_lost_detection_count", "lost_detection_count", True),
        ("highest_mean_latency", "latency_ms_mean", True),
        ("highest_max_latency", "latency_ms_max", True),
        ("highest_horizontal_command", "max_abs_horizontal_command_m_s", True),
        ("highest_visual_x_dispersion", "std_error_x_norm", True),
        ("highest_visual_y_dispersion", "std_error_y_norm", True),
    ]
    output: list[dict[str, object]] = []
    for category, field, descending in specs:
        numeric_rows = [(row, float_or_none(row.get(field))) for row in rows]
        numeric_rows = [(row, value) for row, value in numeric_rows if value is not None]
        threshold = percentile([value for _, value in numeric_rows], 0.9 if descending else 0.1)
        ordered = sorted(numeric_rows, key=lambda item: item[1], reverse=descending)
        for rank, (row, value) in enumerate(ordered[:top_n], start=1):
            output.append(extreme_row(category, rank, row, value, threshold))
    return output


def extreme_row(category: str, rank: int, row: dict[str, str], value: float, threshold: float) -> dict[str, object]:
    return {
        "category": category,
        "rank": rank,
        "run_id": row.get("run_id", ""),
        "scenario_short": canonical_scenario(row.get("scenario_id", "")),
        "scenario_id": row.get("scenario_id", ""),
        "treatment": row.get("treatment", ""),
        "treatment_pair_id": row.get("treatment_pair_id", ""),
        "repetition": row.get("repetition", ""),
        "value": value,
        "threshold": threshold,
        "final_error_m": row.get("final_error_m", ""),
        "landing_time_s": row.get("landing_time_s", ""),
        "accepted_detection_rate": row.get("accepted_detection_rate", ""),
        "lost_detection_count": row.get("lost_detection_count", ""),
        "latency_ms_mean": row.get("latency_ms_mean", ""),
        "latency_ms_max": row.get("latency_ms_max", ""),
        "max_abs_horizontal_command_m_s": row.get("max_abs_horizontal_command_m_s", ""),
        "terminal_event": row.get("terminal_event", ""),
        "terminal_status": row.get("terminal_status", ""),
        "aborted": row.get("aborted", ""),
        "notes": row.get("notes", ""),
    }


def terminal_counts(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    counters: dict[tuple[str, str, str, str, str, str, str], int] = Counter()
    for row in rows:
        scenario_id = row.get("scenario_id", "")
        scenario_short = canonical_scenario(scenario_id)
        treatment = row.get("treatment", "")
        terminal_event = row.get("terminal_event", "")
        terminal_status = row.get("terminal_status", "")
        aborted = row.get("aborted", "")
        counters[("scenario_treatment", scenario_short, scenario_id, treatment, terminal_event, terminal_status, aborted)] += 1
        counters[("treatment", "ALL", "", treatment, terminal_event, terminal_status, aborted)] += 1

    for key, count in sorted(counters.items()):
        scope, scenario_short, scenario_id, treatment, terminal_event, terminal_status, aborted = key
        output.append(
            {
                "scope": scope,
                "scenario_short": scenario_short,
                "scenario_id": scenario_id,
                "treatment": treatment,
                "terminal_event": terminal_event,
                "terminal_status": terminal_status,
                "aborted": aborted,
                "count": count,
            }
        )
    return output


def fmt(value: object, digits: int = 4) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.{digits}f}"


def write_markdown_report(
    path: Path,
    summary_rows: list[dict[str, object]],
    extreme_rows_: list[dict[str, object]],
    terminal_rows: list[dict[str, object]],
) -> Path:
    treatment_rows = [row for row in summary_rows if row["scope"] == "treatment"]
    scenario_rows = [row for row in summary_rows if row["scope"] == "scenario_treatment"]
    lines = [
        "# Phase 06 incident and error-source analysis",
        "",
        "## Treatment-level incident summary",
        "",
        "| Treatment | n | Success rate | Abort rate | Lost detections mean | Detection rate mean | Mean latency | Max latency observed | Final error max | Landing time max | Horizontal command max |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in treatment_rows:
        lines.append(
            "| {treatment} | {n} | {success} | {abort} | {lost} | {detect} | {lat} | {latmax} | {errmax} | {timemax} | {cmdmax} |".format(
                treatment=row["treatment"],
                n=row["n"],
                success=fmt(row["landing_success_rate"]),
                abort=fmt(row["abort_rate"]),
                lost=fmt(row["lost_detection_mean"]),
                detect=fmt(row["accepted_detection_rate_mean"]),
                lat=fmt(row["latency_ms_mean_mean"]),
                latmax=fmt(row["latency_ms_max_max"]),
                errmax=fmt(row["final_error_m_max"]),
                timemax=fmt(row["landing_time_s_max"]),
                cmdmax=fmt(row["max_abs_horizontal_command_m_s_max"]),
            )
        )

    lines.extend(
        [
            "",
            "## Scenario-treatment summary",
            "",
            "| Scenario | Treatment | Lost detections mean | Detection rate mean | Mean latency | Final error max | Landing time max | Visual X sd mean | Visual Y sd mean |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in scenario_rows:
        lines.append(
            "| {scenario} | {treatment} | {lost} | {detect} | {lat} | {errmax} | {timemax} | {sdx} | {sdy} |".format(
                scenario=row["scenario_short"],
                treatment=row["treatment"],
                lost=fmt(row["lost_detection_mean"]),
                detect=fmt(row["accepted_detection_rate_mean"]),
                lat=fmt(row["latency_ms_mean_mean"]),
                errmax=fmt(row["final_error_m_max"]),
                timemax=fmt(row["landing_time_s_max"]),
                sdx=fmt(row["std_error_x_norm_mean"]),
                sdy=fmt(row["std_error_y_norm_mean"]),
            )
        )

    lines.extend(
        [
            "",
            "## Extreme runs",
            "",
            "| Category | Rank | Scenario | Treatment | Value | Run ID |",
            "|---|---:|---|---|---:|---|",
        ]
    )
    for row in extreme_rows_:
        if int(row["rank"]) <= 5:
            lines.append(
                "| {category} | {rank} | {scenario} | {treatment} | {value} | {run_id} |".format(
                    category=row["category"],
                    rank=row["rank"],
                    scenario=row["scenario_short"],
                    treatment=row["treatment"],
                    value=fmt(row["value"]),
                    run_id=row["run_id"],
                )
            )

    terminal_treatment = [row for row in terminal_rows if row["scope"] == "treatment"]
    lines.extend(
        [
            "",
            "## Terminal states",
            "",
            "| Treatment | Terminal event | Terminal status | Aborted | Count |",
            "|---|---|---|---|---:|",
        ]
    )
    for row in terminal_treatment:
        lines.append(
            "| {treatment} | {event} | {status} | {aborted} | {count} |".format(
                treatment=row["treatment"],
                event=row["terminal_event"],
                status=row["terminal_status"],
                aborted=row["aborted"],
                count=row["count"],
            )
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Phase 06 incident analysis.")
    parser.add_argument("--accepted-runs", type=Path, default=ACCEPTED_RUNS_PATH)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--top-n", type=int, default=10)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = accepted_rows(read_csv(resolve_project_path(args.accepted_runs)))
    output_dir = resolve_project_path(args.output_dir)

    summary = grouped_summary(rows)
    extremes = extreme_runs(rows, args.top_n)
    terminals = terminal_counts(rows)

    summary_path = write_csv(output_dir / "phase06_incident_summary.csv", summary, SUMMARY_FIELDS)
    extremes_path = write_csv(output_dir / "phase06_incident_extreme_runs.csv", extremes, EXTREME_FIELDS)
    terminal_path = write_csv(output_dir / "phase06_terminal_state_counts.csv", terminals, COUNTS_FIELDS)
    report_path = write_markdown_report(
        output_dir / "phase06_incident_analysis.md",
        summary,
        extremes,
        terminals,
    )

    print(f"Incident summary: {summary_path}")
    print(f"Extreme runs: {extremes_path}")
    print(f"Terminal counts: {terminal_path}")
    print(f"Markdown report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
