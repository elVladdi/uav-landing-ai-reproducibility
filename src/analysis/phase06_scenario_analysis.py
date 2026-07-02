"""Generate Phase 06 scenario-level analysis from paired Phase 05 outputs.

Inputs:
    - `outputs/tables/phase05_experiments/phase05_pairwise_differences.csv`
    - `outputs/tables/phase05_experiments/phase05_accepted_runs.csv`

Outputs:
    - `phase06_scenario_analysis.csv`
    - `phase06_scenario_factor_summary.csv`
    - `phase06_scenario_rankings.csv`
    - `phase06_scenario_analysis.md`

Reproducibility role:
    Recomputes scenario-level and factor-level summaries for the eight formal
    AirSimNH-PX4 SITL scenarios.

Scope:
    Scenario and factor summaries are descriptive. They support interpretation
    of the controlled experiment but do not imply universal performance across
    other vehicles, cameras, markers, weather, lighting, or real-flight setups.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PAIRWISE_PATH = Path("outputs/tables/phase05_experiments/phase05_pairwise_differences.csv")
ACCEPTED_RUNS_PATH = Path("outputs/tables/phase05_experiments/phase05_accepted_runs.csv")
OUTPUT_DIR = Path("outputs/tables/phase06_analysis")

SCENARIO_FIELDS = [
    "scenario_short",
    "scenario_id",
    "height_m",
    "offset_y_m",
    "yaw_deg",
    "n_pairs",
    "final_error_t0_mean",
    "final_error_t1_mean",
    "final_error_delta_mean_t0_minus_t1",
    "final_error_reduction_ratio",
    "landing_time_t0_mean",
    "landing_time_t1_mean",
    "landing_time_delta_mean_t0_minus_t1",
    "landing_time_increase_ratio",
    "detection_rate_t0_mean",
    "detection_rate_t1_mean",
    "detection_rate_delta_mean_t1_minus_t0",
]

FACTOR_FIELDS = [
    "factor",
    "level",
    "n_pairs",
    "final_error_delta_mean_t0_minus_t1",
    "landing_time_delta_mean_t0_minus_t1",
    "detection_rate_delta_mean_t1_minus_t0",
]

RANKING_FIELDS = [
    "rank_type",
    "rank",
    "scenario_short",
    "scenario_id",
    "value",
    "interpretation",
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


def scenario_metadata(scenario_id: str, accepted_rows: list[dict[str, str]]) -> dict[str, object]:
    rows = [row for row in accepted_rows if row.get("scenario_id") == scenario_id]
    row = rows[0] if rows else {}
    return {
        "height_m": float_or_blank(row.get("planned_initial_height_m")),
        "offset_y_m": float_or_blank(row.get("planned_offset_y_m")),
        "yaw_deg": float_or_blank(row.get("planned_yaw_deg")),
    }


def float_or_none(value: object) -> float | None:
    try:
        if value in (None, ""):
            return None
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None
    except (TypeError, ValueError):
        return None


def float_or_blank(value: object) -> object:
    parsed = float_or_none(value)
    return "" if parsed is None else parsed


def mean(values: Iterable[float]) -> object:
    data = [value for value in values if math.isfinite(value)]
    return statistics.mean(data) if data else ""


def scenario_summary(
    pairwise_rows: list[dict[str, str]], accepted_rows: list[dict[str, str]]
) -> list[dict[str, object]]:
    """Aggregate paired outcomes for each formal scenario."""
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in pairwise_rows:
        groups[row.get("scenario_id", "")].append(row)

    output: list[dict[str, object]] = []
    for scenario_id, rows in sorted(groups.items(), key=lambda item: canonical_scenario(item[0])):
        error_t0 = mean_values(rows, "final_error_m_t0")
        error_t1 = mean_values(rows, "final_error_m_t1")
        error_delta = mean_values(rows, "final_error_m_delta_t0_minus_t1")
        time_t0 = mean_values(rows, "landing_time_s_t0")
        time_t1 = mean_values(rows, "landing_time_s_t1")
        time_delta = mean_values(rows, "landing_time_s_delta_t0_minus_t1")
        detection_t0 = mean_values(rows, "accepted_detection_rate_t0")
        detection_t1 = mean_values(rows, "accepted_detection_rate_t1")
        detection_delta = mean_values(rows, "accepted_detection_rate_delta_t1_minus_t0")
        metadata = scenario_metadata(scenario_id, accepted_rows)

        output.append(
            {
                "scenario_short": canonical_scenario(scenario_id),
                "scenario_id": scenario_id,
                **metadata,
                "n_pairs": len(rows),
                "final_error_t0_mean": error_t0,
                "final_error_t1_mean": error_t1,
                "final_error_delta_mean_t0_minus_t1": error_delta,
                "final_error_reduction_ratio": error_delta / error_t0 if error_t0 else "",
                "landing_time_t0_mean": time_t0,
                "landing_time_t1_mean": time_t1,
                "landing_time_delta_mean_t0_minus_t1": time_delta,
                "landing_time_increase_ratio": abs(time_delta) / time_t0 if time_t0 else "",
                "detection_rate_t0_mean": detection_t0,
                "detection_rate_t1_mean": detection_t1,
                "detection_rate_delta_mean_t1_minus_t0": detection_delta,
            }
        )
    return output


def mean_values(rows: list[dict[str, str]], field: str) -> float:
    values = [value for value in (float_or_none(row.get(field)) for row in rows) if value is not None]
    return statistics.mean(values) if values else 0.0


def factor_summary(summary_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Summarize scenario differences by design factors descriptively."""
    output: list[dict[str, object]] = []
    for factor, field in [
        ("height_m", "height_m"),
        ("offset_y_m", "offset_y_m"),
        ("yaw_deg", "yaw_deg"),
    ]:
        groups: dict[object, list[dict[str, object]]] = defaultdict(list)
        for row in summary_rows:
            groups[row.get(field, "")].append(row)
        for level, rows in sorted(groups.items(), key=lambda item: str(item[0])):
            n_pairs = sum(int(row.get("n_pairs", 0)) for row in rows)
            output.append(
                {
                    "factor": factor,
                    "level": level,
                    "n_pairs": n_pairs,
                    "final_error_delta_mean_t0_minus_t1": weighted_mean(
                        rows, "final_error_delta_mean_t0_minus_t1", "n_pairs"
                    ),
                    "landing_time_delta_mean_t0_minus_t1": weighted_mean(
                        rows, "landing_time_delta_mean_t0_minus_t1", "n_pairs"
                    ),
                    "detection_rate_delta_mean_t1_minus_t0": weighted_mean(
                        rows, "detection_rate_delta_mean_t1_minus_t0", "n_pairs"
                    ),
                }
            )
    return output


def weighted_mean(rows: list[dict[str, object]], value_field: str, weight_field: str) -> object:
    numerator = 0.0
    denominator = 0.0
    for row in rows:
        value = float_or_none(row.get(value_field))
        weight = float_or_none(row.get(weight_field))
        if value is None or weight is None:
            continue
        numerator += value * weight
        denominator += weight
    return numerator / denominator if denominator else ""


def rankings(summary_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    specs = [
        (
            "largest_error_reduction",
            "final_error_delta_mean_t0_minus_t1",
            True,
            "Mayor reduccion media de error final con T1.",
        ),
        (
            "smallest_error_reduction",
            "final_error_delta_mean_t0_minus_t1",
            False,
            "Menor reduccion media de error final con T1.",
        ),
        (
            "largest_time_cost",
            "landing_time_delta_mean_t0_minus_t1",
            False,
            "Mayor incremento temporal de T1 respecto a T0.",
        ),
        (
            "smallest_time_cost",
            "landing_time_delta_mean_t0_minus_t1",
            True,
            "Menor incremento temporal de T1 respecto a T0.",
        ),
        (
            "largest_detection_gain",
            "detection_rate_delta_mean_t1_minus_t0",
            True,
            "Mayor mejora media en tasa de deteccion aceptada.",
        ),
    ]
    output: list[dict[str, object]] = []
    for rank_type, field, descending, interpretation in specs:
        ordered = sorted(
            summary_rows,
            key=lambda row: float_or_none(row.get(field)) or 0.0,
            reverse=descending,
        )
        for index, row in enumerate(ordered, start=1):
            output.append(
                {
                    "rank_type": rank_type,
                    "rank": index,
                    "scenario_short": row.get("scenario_short", ""),
                    "scenario_id": row.get("scenario_id", ""),
                    "value": row.get(field, ""),
                    "interpretation": interpretation,
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
    factor_rows: list[dict[str, object]],
    ranking_rows: list[dict[str, object]],
) -> Path:
    lines = [
        "# Phase 06 scenario analysis",
        "",
        "## Scenario summary",
        "",
        "| Scenario | Height | Offset Y | Yaw | Error T0 | Error T1 | Error reduction | Time T0 | Time T1 | Time delta T0-T1 | Detection gain |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| {scenario} | {height} | {offset} | {yaw} | {err_t0} | {err_t1} | {err_delta} | {time_t0} | {time_t1} | {time_delta} | {det_delta} |".format(
                scenario=row["scenario_short"],
                height=fmt(row["height_m"], 1),
                offset=fmt(row["offset_y_m"], 1),
                yaw=fmt(row["yaw_deg"], 0),
                err_t0=fmt(row["final_error_t0_mean"]),
                err_t1=fmt(row["final_error_t1_mean"]),
                err_delta=fmt(row["final_error_delta_mean_t0_minus_t1"]),
                time_t0=fmt(row["landing_time_t0_mean"]),
                time_t1=fmt(row["landing_time_t1_mean"]),
                time_delta=fmt(row["landing_time_delta_mean_t0_minus_t1"]),
                det_delta=fmt(row["detection_rate_delta_mean_t1_minus_t0"]),
            )
        )

    lines.extend(
        [
            "",
            "## Factor summary",
            "",
            "| Factor | Level | n pairs | Error reduction | Time delta T0-T1 | Detection gain |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in factor_rows:
        lines.append(
            "| {factor} | {level} | {n} | {err} | {time} | {det} |".format(
                factor=row["factor"],
                level=fmt(row["level"], 1),
                n=row["n_pairs"],
                err=fmt(row["final_error_delta_mean_t0_minus_t1"]),
                time=fmt(row["landing_time_delta_mean_t0_minus_t1"]),
                det=fmt(row["detection_rate_delta_mean_t1_minus_t0"]),
            )
        )

    lines.extend(
        [
            "",
            "## Rankings",
            "",
            "| Rank type | Rank | Scenario | Value | Interpretation |",
            "|---|---:|---|---:|---|",
        ]
    )
    for row in ranking_rows:
        if int(row["rank"]) <= 3:
            lines.append(
                "| {rank_type} | {rank} | {scenario} | {value} | {interpretation} |".format(
                    rank_type=row["rank_type"],
                    rank=row["rank"],
                    scenario=row["scenario_short"],
                    value=fmt(row["value"]),
                    interpretation=row["interpretation"],
                )
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Phase 06 scenario analysis.")
    parser.add_argument("--pairwise-differences", type=Path, default=PAIRWISE_PATH)
    parser.add_argument("--accepted-runs", type=Path, default=ACCEPTED_RUNS_PATH)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pairwise = read_csv(resolve_project_path(args.pairwise_differences))
    accepted = read_csv(resolve_project_path(args.accepted_runs))
    output_dir = resolve_project_path(args.output_dir)

    summary_rows = scenario_summary(pairwise, accepted)
    factor_rows = factor_summary(summary_rows)
    ranking_rows = rankings(summary_rows)

    scenario_path = write_csv(output_dir / "phase06_scenario_analysis.csv", summary_rows, SCENARIO_FIELDS)
    factor_path = write_csv(output_dir / "phase06_scenario_factor_summary.csv", factor_rows, FACTOR_FIELDS)
    ranking_path = write_csv(output_dir / "phase06_scenario_rankings.csv", ranking_rows, RANKING_FIELDS)
    report_path = write_markdown_report(
        output_dir / "phase06_scenario_analysis.md",
        summary_rows,
        factor_rows,
        ranking_rows,
    )

    print(f"Scenario analysis: {scenario_path}")
    print(f"Factor summary: {factor_path}")
    print(f"Rankings: {ranking_path}")
    print(f"Markdown report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
