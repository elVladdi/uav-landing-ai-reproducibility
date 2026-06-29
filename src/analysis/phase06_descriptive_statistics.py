"""Generate Phase 06 descriptive statistics from Phase 05 formal outputs."""
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

ACCEPTED_RUNS_PATH = Path("outputs/tables/phase05_experiments/phase05_accepted_runs.csv")
PAIRWISE_PATH = Path("outputs/tables/phase05_experiments/phase05_pairwise_differences.csv")
OUTPUT_DIR = Path("outputs/tables/phase06_analysis")

RUN_METRICS = [
    "final_error_m",
    "landing_time_s",
    "total_duration_s",
    "accepted_detection_rate",
    "lost_detection_count",
    "latency_ms_mean",
    "latency_ms_max",
    "mean_abs_error_x_norm",
    "std_error_x_norm",
    "mean_abs_error_y_norm",
    "std_error_y_norm",
    "max_abs_horizontal_command_m_s",
    "command_count",
    "descent_command_count",
]

PAIRWISE_METRICS = [
    "final_error_m_delta_t0_minus_t1",
    "landing_time_s_delta_t0_minus_t1",
    "accepted_detection_rate_delta_t1_minus_t0",
]

SUMMARY_FIELDS = [
    "scope",
    "scenario_short",
    "scenario_id",
    "treatment",
    "metric",
    "n",
    "mean",
    "median",
    "sd",
    "min",
    "q1",
    "q3",
    "max",
]

PAIRWISE_SUMMARY_FIELDS = [
    "scope",
    "scenario_short",
    "scenario_id",
    "metric",
    "n",
    "mean",
    "median",
    "sd",
    "min",
    "q1",
    "q3",
    "max",
    "direction",
]

SUCCESS_FIELDS = [
    "scope",
    "scenario_short",
    "scenario_id",
    "treatment",
    "n",
    "success_count",
    "success_rate",
    "abort_count",
    "abort_rate",
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


def canonical_scenario(value: str) -> str:
    match = re.search(r"S(\d{2})", value.upper())
    if match:
        return f"S{match.group(1)}"
    return value.upper()


def descriptive_stats(values: Iterable[float]) -> dict[str, object]:
    data = sorted(value for value in values if math.isfinite(value))
    if not data:
        return {
            "n": 0,
            "mean": "",
            "median": "",
            "sd": "",
            "min": "",
            "q1": "",
            "q3": "",
            "max": "",
        }
    return {
        "n": len(data),
        "mean": statistics.mean(data),
        "median": statistics.median(data),
        "sd": statistics.stdev(data) if len(data) > 1 else 0.0,
        "min": data[0],
        "q1": percentile(data, 0.25),
        "q3": percentile(data, 0.75),
        "max": data[-1],
    }


def percentile(sorted_data: list[float], probability: float) -> float:
    if not sorted_data:
        raise ValueError("percentile requires at least one value")
    if len(sorted_data) == 1:
        return sorted_data[0]
    position = (len(sorted_data) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_data[int(position)]
    fraction = position - lower
    return sorted_data[lower] + (sorted_data[upper] - sorted_data[lower]) * fraction


def float_or_none(value: object) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "si"}


def accepted_formal_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("curation_status") == "accepted"]


def run_metric_summary(rows: list[dict[str, str]], scope: str) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        scenario_id = row.get("scenario_id", "")
        scenario_short = canonical_scenario(scenario_id)
        treatment = row.get("treatment", "")
        if scope == "treatment":
            key = ("ALL", "", treatment)
        elif scope == "scenario_treatment":
            key = (scenario_short, scenario_id, treatment)
        else:
            raise ValueError(f"Unsupported scope: {scope}")
        groups[key].append(row)

    output: list[dict[str, object]] = []
    for (scenario_short, scenario_id, treatment), group_rows in sorted(groups.items()):
        for metric in RUN_METRICS:
            values = [
                value
                for value in (float_or_none(row.get(metric)) for row in group_rows)
                if value is not None
            ]
            output.append(
                {
                    "scope": scope,
                    "scenario_short": scenario_short,
                    "scenario_id": scenario_id,
                    "treatment": treatment,
                    "metric": metric,
                    **descriptive_stats(values),
                }
            )
    return output


def success_summary(rows: list[dict[str, str]], scope: str) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        scenario_id = row.get("scenario_id", "")
        scenario_short = canonical_scenario(scenario_id)
        treatment = row.get("treatment", "")
        if scope == "treatment":
            key = ("ALL", "", treatment)
        elif scope == "scenario_treatment":
            key = (scenario_short, scenario_id, treatment)
        else:
            raise ValueError(f"Unsupported scope: {scope}")
        groups[key].append(row)

    output: list[dict[str, object]] = []
    for (scenario_short, scenario_id, treatment), group_rows in sorted(groups.items()):
        n = len(group_rows)
        success_count = sum(1 for row in group_rows if truthy(row.get("landing_success")))
        abort_count = sum(1 for row in group_rows if truthy(row.get("aborted")))
        output.append(
            {
                "scope": scope,
                "scenario_short": scenario_short,
                "scenario_id": scenario_id,
                "treatment": treatment,
                "n": n,
                "success_count": success_count,
                "success_rate": success_count / n if n else "",
                "abort_count": abort_count,
                "abort_rate": abort_count / n if n else "",
            }
        )
    return output


def pairwise_summary(rows: list[dict[str, str]], scope: str) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        scenario_id = row.get("scenario_id", "")
        scenario_short = canonical_scenario(scenario_id)
        if scope == "global":
            key = ("ALL", "")
        elif scope == "scenario":
            key = (scenario_short, scenario_id)
        else:
            raise ValueError(f"Unsupported scope: {scope}")
        groups[key].append(row)

    output: list[dict[str, object]] = []
    for (scenario_short, scenario_id), group_rows in sorted(groups.items()):
        for metric in PAIRWISE_METRICS:
            values = [
                value
                for value in (float_or_none(row.get(metric)) for row in group_rows)
                if value is not None
            ]
            stats = descriptive_stats(values)
            output.append(
                {
                    "scope": scope,
                    "scenario_short": scenario_short,
                    "scenario_id": scenario_id,
                    "metric": metric,
                    **stats,
                    "direction": pairwise_direction(metric, stats.get("mean")),
                }
            )
    return output


def pairwise_direction(metric: str, mean_value: object) -> str:
    if mean_value in ("", None):
        return ""
    mean = float(mean_value)
    if metric == "final_error_m_delta_t0_minus_t1":
        return "T1 lower final error" if mean > 0 else "T0 lower final error"
    if metric == "landing_time_s_delta_t0_minus_t1":
        return "T1 longer landing time" if mean < 0 else "T1 shorter landing time"
    if metric == "accepted_detection_rate_delta_t1_minus_t0":
        return "T1 higher detection rate" if mean > 0 else "T0 higher detection rate"
    return ""


def format_number(value: object, digits: int = 4) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.{digits}f}"


def metric_label(metric: str) -> str:
    labels = {
        "final_error_m": "Error final (m)",
        "landing_time_s": "Tiempo de aterrizaje (s)",
        "total_duration_s": "Duracion total (s)",
        "accepted_detection_rate": "Tasa de deteccion aceptada",
        "lost_detection_count": "Perdidas de deteccion",
        "latency_ms_mean": "Latencia media (ms)",
        "latency_ms_max": "Latencia maxima (ms)",
        "mean_abs_error_x_norm": "Error visual X medio absoluto",
        "std_error_x_norm": "Dispersion error visual X",
        "mean_abs_error_y_norm": "Error visual Y medio absoluto",
        "std_error_y_norm": "Dispersion error visual Y",
        "max_abs_horizontal_command_m_s": "Comando horizontal maximo (m/s)",
        "command_count": "Comandos enviados",
        "descent_command_count": "Comandos de descenso",
        "final_error_m_delta_t0_minus_t1": "Diferencia error final T0-T1 (m)",
        "landing_time_s_delta_t0_minus_t1": "Diferencia tiempo T0-T1 (s)",
        "accepted_detection_rate_delta_t1_minus_t0": "Diferencia deteccion T1-T0",
    }
    return labels.get(metric, metric)


def write_markdown_report(
    path: Path,
    treatment_rows: list[dict[str, object]],
    scenario_rows: list[dict[str, object]],
    pairwise_rows: list[dict[str, object]],
    success_rows: list[dict[str, object]],
) -> Path:
    treatment_lookup = {
        (row["treatment"], row["metric"]): row
        for row in treatment_rows
        if row["scope"] == "treatment"
    }
    pairwise_lookup = {
        row["metric"]: row
        for row in pairwise_rows
        if row["scope"] == "global" and row["scenario_short"] == "ALL"
    }
    success_lookup = {
        row["treatment"]: row
        for row in success_rows
        if row["scope"] == "treatment"
    }

    lines = [
        "# Phase 06 descriptive statistics",
        "",
        "## Global treatment summary",
        "",
        "| Metric | T0 mean | T0 median | T0 sd | T1 mean | T1 median | T1 sd |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for metric in [
        "final_error_m",
        "landing_time_s",
        "total_duration_s",
        "accepted_detection_rate",
        "lost_detection_count",
        "latency_ms_mean",
        "mean_abs_error_x_norm",
        "mean_abs_error_y_norm",
        "max_abs_horizontal_command_m_s",
    ]:
        t0 = treatment_lookup.get(("T0", metric), {})
        t1 = treatment_lookup.get(("T1", metric), {})
        lines.append(
            "| {metric} | {t0_mean} | {t0_median} | {t0_sd} | {t1_mean} | {t1_median} | {t1_sd} |".format(
                metric=metric_label(metric),
                t0_mean=format_number(t0.get("mean")),
                t0_median=format_number(t0.get("median")),
                t0_sd=format_number(t0.get("sd")),
                t1_mean=format_number(t1.get("mean")),
                t1_median=format_number(t1.get("median")),
                t1_sd=format_number(t1.get("sd")),
            )
        )

    lines.extend(
        [
            "",
            "## Success and abort summary",
            "",
            "| Treatment | n | Success count | Success rate | Abort count | Abort rate |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for treatment in ("T0", "T1"):
        row = success_lookup.get(treatment, {})
        lines.append(
            "| {treatment} | {n} | {success_count} | {success_rate} | {abort_count} | {abort_rate} |".format(
                treatment=treatment,
                n=row.get("n", ""),
                success_count=row.get("success_count", ""),
                success_rate=format_number(row.get("success_rate")),
                abort_count=row.get("abort_count", ""),
                abort_rate=format_number(row.get("abort_rate")),
            )
        )

    lines.extend(
        [
            "",
            "## Global paired differences",
            "",
            "| Metric | n | Mean | Median | SD | Min | Max | Direction |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for metric in PAIRWISE_METRICS:
        row = pairwise_lookup.get(metric, {})
        lines.append(
            "| {metric} | {n} | {mean} | {median} | {sd} | {minv} | {maxv} | {direction} |".format(
                metric=metric_label(metric),
                n=row.get("n", ""),
                mean=format_number(row.get("mean")),
                median=format_number(row.get("median")),
                sd=format_number(row.get("sd")),
                minv=format_number(row.get("min")),
                maxv=format_number(row.get("max")),
                direction=row.get("direction", ""),
            )
        )

    lines.extend(
        [
            "",
            "## Scenario coverage",
            "",
            "| Scenario | Metric | T0 mean | T1 mean |",
            "|---|---|---:|---:|",
        ]
    )
    scenario_lookup = {
        (row["scenario_short"], row["treatment"], row["metric"]): row
        for row in scenario_rows
        if row["scope"] == "scenario_treatment"
    }
    for scenario in [f"S{i:02d}" for i in range(1, 9)]:
        for metric in ("final_error_m", "landing_time_s", "accepted_detection_rate"):
            t0 = scenario_lookup.get((scenario, "T0", metric), {})
            t1 = scenario_lookup.get((scenario, "T1", metric), {})
            lines.append(
                f"| {scenario} | {metric_label(metric)} | {format_number(t0.get('mean'))} | {format_number(t1.get('mean'))} |"
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Phase 06 descriptive statistics.")
    parser.add_argument(
        "--accepted-runs",
        type=Path,
        default=ACCEPTED_RUNS_PATH,
        help="Path to phase05_accepted_runs.csv.",
    )
    parser.add_argument(
        "--pairwise-differences",
        type=Path,
        default=PAIRWISE_PATH,
        help="Path to phase05_pairwise_differences.csv.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for Phase 06 descriptive outputs.",
    )
    return parser.parse_args()


def resolve_project_path(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def main() -> int:
    args = parse_args()
    accepted_path = resolve_project_path(args.accepted_runs)
    pairwise_path = resolve_project_path(args.pairwise_differences)
    output_dir = resolve_project_path(args.output_dir)

    accepted = accepted_formal_rows(read_csv(accepted_path))
    pairwise = read_csv(pairwise_path)

    treatment_summary = run_metric_summary(accepted, "treatment")
    scenario_summary = run_metric_summary(accepted, "scenario_treatment")
    pairwise_rows = pairwise_summary(pairwise, "global") + pairwise_summary(pairwise, "scenario")
    success_rows = success_summary(accepted, "treatment") + success_summary(accepted, "scenario_treatment")

    treatment_path = write_csv(
        output_dir / "phase06_descriptive_by_treatment.csv",
        treatment_summary,
        SUMMARY_FIELDS,
    )
    scenario_path = write_csv(
        output_dir / "phase06_descriptive_by_scenario_treatment.csv",
        scenario_summary,
        SUMMARY_FIELDS,
    )
    pairwise_summary_path = write_csv(
        output_dir / "phase06_pairwise_difference_summary.csv",
        pairwise_rows,
        PAIRWISE_SUMMARY_FIELDS,
    )
    success_path = write_csv(
        output_dir / "phase06_success_abort_summary.csv",
        success_rows,
        SUCCESS_FIELDS,
    )
    report_path = write_markdown_report(
        output_dir / "phase06_descriptive_statistics.md",
        treatment_summary,
        scenario_summary,
        pairwise_rows,
        success_rows,
    )

    print(f"Treatment summary: {treatment_path}")
    print(f"Scenario summary: {scenario_path}")
    print(f"Pairwise summary: {pairwise_summary_path}")
    print(f"Success summary: {success_path}")
    print(f"Markdown report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
