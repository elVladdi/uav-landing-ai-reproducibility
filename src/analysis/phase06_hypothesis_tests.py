"""Generate Phase 06 paired hypothesis-test outputs.

Inputs:
    - `outputs/tables/phase05_experiments/phase05_pairwise_differences.csv`
    - `outputs/tables/phase05_experiments/phase05_accepted_runs.csv`

Outputs:
    - `outputs/tables/phase06_analysis/phase06_hypothesis_tests.csv`
    - `outputs/tables/phase06_analysis/phase06_effect_sizes.csv`
    - `outputs/tables/phase06_analysis/phase06_categorical_tests.csv`
    - `outputs/tables/phase06_analysis/phase06_hypothesis_tests.md`

Reproducibility role:
    Recomputes the inferential statistics reported for the paired T0/T1
    comparison from versioned Phase 05 tables.

Scope:
    Analytical reproduction only. These tests do not validate real-flight
    performance, physical touchdown, operational deployment, or sim-to-real
    transfer. SciPy is used for the exact reported tests when available; the
    documented standard-library fallbacks are approximate inspection aids.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PAIRWISE_PATH = Path("outputs/tables/phase05_experiments/phase05_pairwise_differences.csv")
ACCEPTED_RUNS_PATH = Path("outputs/tables/phase05_experiments/phase05_accepted_runs.csv")
OUTPUT_DIR = Path("outputs/tables/phase06_analysis")
ALPHA = 0.05

try:
    from scipy import stats as scipy_stats  # type: ignore

    SCIPY_AVAILABLE = True
except ModuleNotFoundError:
    scipy_stats = None
    SCIPY_AVAILABLE = False


HYPOTHESES = [
    {
        "hypothesis": "HE1",
        "metric": "final_error_m_delta_t0_minus_t1",
        "label": "Error final",
        "alternative": "greater",
        "direction": "T1 reduce el error final frente a T0",
        "positive_interpretation": "T1 presenta menor error final que T0.",
    },
    {
        "hypothesis": "HE2",
        "metric": "landing_time_s_delta_t0_minus_t1",
        "label": "Tiempo de aterrizaje",
        "alternative": "two-sided",
        "direction": "T1 modifica el tiempo de aterrizaje frente a T0",
        "positive_interpretation": "T1 modifica el tiempo de aterrizaje respecto a T0.",
    },
    {
        "hypothesis": "HE3",
        "metric": "visual_dispersion_norm_delta_t0_minus_t1",
        "label": "Dinamica lateral - dispersion visual/lateral",
        "alternative": "two-sided",
        "direction": "T1 modifica la dinamica lateral frente a T0 mediante dispersion visual/lateral",
        "positive_interpretation": "T1 presenta diferencia significativa en dispersion visual/lateral frente a T0.",
    },
    {
        "hypothesis": "HE3",
        "metric": "command_count_delta_t1_minus_t0",
        "label": "Dinamica lateral - actividad correctiva",
        "alternative": "two-sided",
        "direction": "T1 modifica la actividad correctiva frente a T0 mediante conteo de comandos",
        "positive_interpretation": "T1 presenta diferencia significativa en actividad correctiva frente a T0.",
    },
    {
        "hypothesis": "HE3",
        "metric": "max_abs_horizontal_command_m_s_delta_t1_minus_t0",
        "label": "Dinamica lateral - intensidad correctiva",
        "alternative": "two-sided",
        "direction": "T1 modifica la intensidad correctiva lateral frente a T0",
        "positive_interpretation": "T1 presenta diferencia significativa en intensidad correctiva lateral frente a T0.",
    },
]

TEST_FIELDS = [
    "hypothesis",
    "metric",
    "n",
    "mean_difference",
    "median_difference",
    "sd_difference",
    "normality_test",
    "normality_statistic",
    "normality_p_value",
    "normality_decision",
    "selected_test",
    "test_statistic",
    "p_value",
    "alpha",
    "decision",
    "interpretation",
]

EFFECT_FIELDS = [
    "hypothesis",
    "metric",
    "n",
    "mean_difference",
    "median_difference",
    "sd_difference",
    "cohen_dz",
    "percent_change_mean",
    "practical_direction",
]

CATEGORICAL_FIELDS = [
    "hypothesis",
    "outcome",
    "n_pairs",
    "t0_success_t1_success",
    "t0_success_t1_failure",
    "t0_failure_t1_success",
    "t0_failure_t1_failure",
    "selected_test",
    "p_value",
    "alpha",
    "decision",
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


def numbers(rows: list[dict[str, str]], metric: str) -> list[float]:
    return [value for value in (float_or_none(row.get(metric)) for row in rows) if value is not None]


def describe(values: list[float]) -> dict[str, object]:
    if not values:
        return {"n": 0, "mean": "", "median": "", "sd": ""}
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def normal_sf(value: float) -> float:
    return 0.5 * math.erfc(value / math.sqrt(2.0))


def shapiro_or_fallback(values: list[float]) -> tuple[str, object, object, str]:
    """Run Shapiro-Wilk normality testing or a labeled fallback.

    The fallback is provided so the public workflow can still complete in a
    minimal Python environment. Article or thesis statistics should be produced
    with SciPy available.
    """
    if len(values) < 3:
        return "not_applicable", "", "", "insufficient_n"
    if SCIPY_AVAILABLE:
        result = scipy_stats.shapiro(values)
        p_value = float(result.pvalue)
        decision = "normal" if p_value >= ALPHA else "non_normal"
        return "Shapiro-Wilk", float(result.statistic), p_value, decision

    # Jarque-Bera is used only as a fallback when scipy is unavailable.
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    if sd == 0.0:
        return "Jarque-Bera approximate fallback", 0.0, 1.0, "normal"
    centered = [(value - mean) / sd for value in values]
    skew = sum(value**3 for value in centered) / len(centered)
    kurtosis = sum(value**4 for value in centered) / len(centered)
    jb = len(values) / 6.0 * (skew**2 + ((kurtosis - 3.0) ** 2) / 4.0)
    # Chi-square survival with 2 df is exp(-x/2).
    p_value = math.exp(-jb / 2.0)
    decision = "normal" if p_value >= ALPHA else "non_normal"
    return "Jarque-Bera approximate fallback", jb, p_value, decision


def paired_t_or_normal(values: list[float], alternative: str) -> tuple[str, object, object]:
    desc = describe(values)
    n = int(desc["n"])
    sd = float(desc["sd"])
    mean = float(desc["mean"])
    if n < 2 or sd == 0.0:
        return "paired t-test", "", 1.0 if mean == 0 else 0.0
    statistic = mean / (sd / math.sqrt(n))
    if SCIPY_AVAILABLE:
        result = scipy_stats.ttest_1samp(values, popmean=0.0, alternative=alternative)
        return "paired t-test", float(result.statistic), float(result.pvalue)
    if alternative == "greater":
        p_value = normal_sf(statistic)
    elif alternative == "less":
        p_value = normal_cdf(statistic)
    else:
        p_value = 2.0 * min(normal_cdf(statistic), normal_sf(statistic))
    return "paired t-test normal approximation fallback", statistic, min(1.0, max(0.0, p_value))


def wilcoxon_or_sign(values: list[float], alternative: str) -> tuple[str, object, object]:
    nonzero = [value for value in values if value != 0.0]
    if not nonzero:
        return "Wilcoxon signed-rank", "", 1.0
    if SCIPY_AVAILABLE:
        result = scipy_stats.wilcoxon(nonzero, alternative=alternative, zero_method="wilcox")
        return "Wilcoxon signed-rank", float(result.statistic), float(result.pvalue)

    positives = sum(1 for value in nonzero if value > 0)
    negatives = len(nonzero) - positives
    p_value = sign_test_p_value(positives, negatives, alternative)
    statistic = min(positives, negatives) if alternative == "two-sided" else positives
    return "sign test fallback for Wilcoxon", statistic, p_value


def sign_test_p_value(positives: int, negatives: int, alternative: str) -> float:
    n = positives + negatives
    if n == 0:
        return 1.0
    if alternative == "greater":
        return binomial_tail(n, positives, upper=True)
    if alternative == "less":
        return binomial_tail(n, positives, upper=False)
    tail = sum(math.comb(n, k) for k in range(0, min(positives, negatives) + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def binomial_tail(n: int, observed: int, upper: bool) -> float:
    if upper:
        return sum(math.comb(n, k) for k in range(observed, n + 1)) / (2**n)
    return sum(math.comb(n, k) for k in range(0, observed + 1)) / (2**n)


def select_and_run_test(values: list[float], alternative: str, normality_decision: str) -> tuple[str, object, object]:
    if normality_decision == "normal":
        return paired_t_or_normal(values, alternative)
    return wilcoxon_or_sign(values, alternative)


def hypothesis_tests(pairwise_rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Compute paired continuous-outcome tests and effect-size summaries."""
    test_rows: list[dict[str, object]] = []
    effect_rows: list[dict[str, object]] = []
    for item in HYPOTHESES:
        metric = item["metric"]
        values = numbers(pairwise_rows, metric)
        desc = describe(values)
        normality_name, normality_stat, normality_p, normality_decision = shapiro_or_fallback(values)
        selected_test, test_stat, p_value = select_and_run_test(
            values, item["alternative"], normality_decision
        )
        rejected = p_value != "" and float(p_value) < ALPHA
        decision = "reject_H0" if rejected else "fail_to_reject_H0"
        interpretation = item["positive_interpretation"] if rejected else "No se detecta diferencia estadistica suficiente."
        mean = float(desc["mean"]) if desc["mean"] != "" else 0.0
        sd = float(desc["sd"]) if desc["sd"] != "" else 0.0

        test_rows.append(
            {
                "hypothesis": item["hypothesis"],
                "metric": metric,
                "n": desc["n"],
                "mean_difference": desc["mean"],
                "median_difference": desc["median"],
                "sd_difference": desc["sd"],
                "normality_test": normality_name,
                "normality_statistic": normality_stat,
                "normality_p_value": normality_p,
                "normality_decision": normality_decision,
                "selected_test": selected_test,
                "test_statistic": test_stat,
                "p_value": p_value,
                "alpha": ALPHA,
                "decision": decision,
                "interpretation": interpretation,
            }
        )
        effect_rows.append(
            {
                "hypothesis": item["hypothesis"],
                "metric": metric,
                "n": desc["n"],
                "mean_difference": desc["mean"],
                "median_difference": desc["median"],
                "sd_difference": desc["sd"],
                "cohen_dz": mean / sd if sd else "",
                "percent_change_mean": percent_change(pairwise_rows, metric),
                "practical_direction": item["direction"],
            }
        )
    return test_rows, effect_rows


def percent_change(rows: list[dict[str, str]], metric: str) -> object:
    def paired_percent_change(t0_metric: str, delta_metric: str) -> object:
        t0 = [value for value in (float_or_none(row.get(t0_metric)) for row in rows) if value is not None]
        delta = numbers(rows, delta_metric)
        return statistics.mean(delta) / statistics.mean(t0) if t0 and delta and statistics.mean(t0) else ""

    if metric == "final_error_m_delta_t0_minus_t1":
        return paired_percent_change("final_error_m_t0", metric)
    if metric == "landing_time_s_delta_t0_minus_t1":
        return paired_percent_change("landing_time_s_t0", metric)
    if metric == "accepted_detection_rate_delta_t1_minus_t0":
        return paired_percent_change("accepted_detection_rate_t0", metric)
    if metric == "visual_dispersion_norm_delta_t0_minus_t1":
        return paired_percent_change("visual_dispersion_norm_t0", metric)
    if metric == "command_count_delta_t1_minus_t0":
        return paired_percent_change("command_count_t0", metric)
    if metric == "max_abs_horizontal_command_m_s_delta_t1_minus_t0":
        return paired_percent_change("max_abs_horizontal_command_m_s_t0", metric)
    return ""


def add_lateral_dynamics_metrics(pairwise_rows: list[dict[str, str]], accepted_rows: list[dict[str, str]]) -> None:
    """Attach lateral-dynamics metrics from accepted runs to paired rows.

    The added columns support HE3 by comparing visual dispersion, command count,
    and maximum horizontal command intensity between matched T0/T1 runs. These
    metrics describe simulated approach dynamics and should not be interpreted
    as a universal controller-validity measure.
    """
    metrics_by_run: dict[str, dict[str, float]] = {}
    for row in accepted_rows:
        run_id = row.get("run_id", "")
        std_x = float_or_none(row.get("std_error_x_norm"))
        std_y = float_or_none(row.get("std_error_y_norm"))
        command_count = float_or_none(row.get("command_count"))
        max_horizontal_command = float_or_none(row.get("max_abs_horizontal_command_m_s"))
        if run_id and std_x is not None and std_y is not None:
            metrics_by_run.setdefault(run_id, {})["visual_dispersion_norm"] = math.sqrt(std_x**2 + std_y**2)
        if run_id and command_count is not None:
            metrics_by_run.setdefault(run_id, {})["command_count"] = command_count
        if run_id and max_horizontal_command is not None:
            metrics_by_run.setdefault(run_id, {})["max_abs_horizontal_command_m_s"] = max_horizontal_command

    for row in pairwise_rows:
        t0_metrics = metrics_by_run.get(row.get("t0_run_id", ""), {})
        t1_metrics = metrics_by_run.get(row.get("t1_run_id", ""), {})

        visual_t0 = t0_metrics.get("visual_dispersion_norm")
        visual_t1 = t1_metrics.get("visual_dispersion_norm")
        row["visual_dispersion_norm_t0"] = "" if visual_t0 is None else str(visual_t0)
        row["visual_dispersion_norm_t1"] = "" if visual_t1 is None else str(visual_t1)
        row["visual_dispersion_norm_delta_t0_minus_t1"] = (
            "" if visual_t0 is None or visual_t1 is None else str(visual_t0 - visual_t1)
        )

        command_t0 = t0_metrics.get("command_count")
        command_t1 = t1_metrics.get("command_count")
        row["command_count_t0"] = "" if command_t0 is None else str(command_t0)
        row["command_count_t1"] = "" if command_t1 is None else str(command_t1)
        row["command_count_delta_t1_minus_t0"] = (
            "" if command_t0 is None or command_t1 is None else str(command_t1 - command_t0)
        )

        max_command_t0 = t0_metrics.get("max_abs_horizontal_command_m_s")
        max_command_t1 = t1_metrics.get("max_abs_horizontal_command_m_s")
        row["max_abs_horizontal_command_m_s_t0"] = "" if max_command_t0 is None else str(max_command_t0)
        row["max_abs_horizontal_command_m_s_t1"] = "" if max_command_t1 is None else str(max_command_t1)
        row["max_abs_horizontal_command_m_s_delta_t1_minus_t0"] = (
            ""
            if max_command_t0 is None or max_command_t1 is None
            else str(max_command_t1 - max_command_t0)
        )


def categorical_test(accepted_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Evaluate binary landing success as a paired categorical outcome.

    In the formal dataset, landing success is saturated in both treatments.
    This output is retained for traceability but should be interpreted together
    with terminal error, time, detection availability, and corrective activity.
    """
    groups: dict[str, dict[str, bool]] = {}
    for row in accepted_rows:
        if row.get("curation_status") != "accepted":
            continue
        pair_id = row.get("treatment_pair_id", "")
        treatment = row.get("treatment", "")
        if not pair_id or treatment not in {"T0", "T1"}:
            continue
        groups.setdefault(pair_id, {})[treatment] = truthy(row.get("landing_success"))

    counts = Counter()
    for pair in groups.values():
        if "T0" not in pair or "T1" not in pair:
            continue
        counts[(pair["T0"], pair["T1"])] += 1

    b = counts[(True, False)]
    c = counts[(False, True)]
    discordant = b + c
    if discordant == 0:
        p_value = 1.0
        selected_test = "McNemar exact binomial"
    else:
        selected_test = "McNemar exact binomial"
        p_value = min(1.0, 2.0 * sum(math.comb(discordant, k) for k in range(0, min(b, c) + 1)) / (2**discordant))

    decision = "reject_H0" if p_value < ALPHA else "fail_to_reject_H0"
    interpretation = (
        "Se detecta diferencia en proporcion de exito."
        if decision == "reject_H0"
        else "No se detecta diferencia en proporcion de exito; ambos tratamientos presentan exito completo."
    )
    return [
        {
            "hypothesis": "HE4",
            "outcome": "landing_success",
            "n_pairs": sum(counts.values()),
            "t0_success_t1_success": counts[(True, True)],
            "t0_success_t1_failure": b,
            "t0_failure_t1_success": c,
            "t0_failure_t1_failure": counts[(False, False)],
            "selected_test": selected_test,
            "p_value": p_value,
            "alpha": ALPHA,
            "decision": decision,
            "interpretation": interpretation,
        }
    ]


def fmt(value: object, digits: int = 6) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.{digits}g}"


def write_markdown_report(
    path: Path,
    tests: list[dict[str, object]],
    effects: list[dict[str, object]],
    categorical: list[dict[str, object]],
) -> Path:
    lines = [
        "# Phase 06 hypothesis tests",
        "",
        f"- scipy available: `{SCIPY_AVAILABLE}`",
        f"- alpha: `{ALPHA}`",
        "",
        "## Continuous paired outcomes",
        "",
        "| Hypothesis | Metric | n | Normality | Selected test | Statistic | p-value | Decision |",
        "|---|---|---:|---|---|---:|---:|---|",
    ]
    for row in tests:
        lines.append(
            "| {hypothesis} | {metric} | {n} | {normality} (p={normality_p}) | {test} | {stat} | {p} | {decision} |".format(
                hypothesis=row["hypothesis"],
                metric=row["metric"],
                n=row["n"],
                normality=row["normality_test"],
                normality_p=fmt(row["normality_p_value"]),
                test=row["selected_test"],
                stat=fmt(row["test_statistic"]),
                p=fmt(row["p_value"]),
                decision=row["decision"],
            )
        )

    lines.extend(
        [
            "",
            "## Effect size summary",
            "",
            "| Hypothesis | Metric | Mean difference | Median difference | Cohen dz | Percent change mean | Direction |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in effects:
        lines.append(
            "| {hypothesis} | {metric} | {mean} | {median} | {dz} | {pct} | {direction} |".format(
                hypothesis=row["hypothesis"],
                metric=row["metric"],
                mean=fmt(row["mean_difference"]),
                median=fmt(row["median_difference"]),
                dz=fmt(row["cohen_dz"]),
                pct=fmt(row["percent_change_mean"]),
                direction=row["practical_direction"],
            )
        )

    lines.extend(
        [
            "",
            "## Categorical outcome",
            "",
            "| Hypothesis | Outcome | n pairs | T0 success/T1 success | T0 success/T1 failure | T0 failure/T1 success | T0 failure/T1 failure | Test | p-value | Decision |",
            "|---|---|---:|---:|---:|---:|---:|---|---:|---|",
        ]
    )
    for row in categorical:
        lines.append(
            "| {hypothesis} | {outcome} | {n} | {ss} | {sf} | {fs} | {ff} | {test} | {p} | {decision} |".format(
                hypothesis=row["hypothesis"],
                outcome=row["outcome"],
                n=row["n_pairs"],
                ss=row["t0_success_t1_success"],
                sf=row["t0_success_t1_failure"],
                fs=row["t0_failure_t1_success"],
                ff=row["t0_failure_t1_failure"],
                test=row["selected_test"],
                p=fmt(row["p_value"]),
                decision=row["decision"],
            )
        )

    if not SCIPY_AVAILABLE:
        lines.extend(
            [
                "",
                "## Method note",
                "",
                "SciPy is not installed in the active environment. Normality and paired tests were generated with documented standard-library fallbacks. For final thesis reporting, install SciPy and rerun this script to obtain Shapiro-Wilk, paired t-test and Wilcoxon signed-rank results from the standard scientific implementation.",
            ]
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Phase 06 hypothesis tests.")
    parser.add_argument("--pairwise-differences", type=Path, default=PAIRWISE_PATH)
    parser.add_argument("--accepted-runs", type=Path, default=ACCEPTED_RUNS_PATH)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pairwise = read_csv(resolve_project_path(args.pairwise_differences))
    accepted = read_csv(resolve_project_path(args.accepted_runs))
    output_dir = resolve_project_path(args.output_dir)
    add_lateral_dynamics_metrics(pairwise, accepted)

    tests, effects = hypothesis_tests(pairwise)
    categorical = categorical_test(accepted)

    tests_path = write_csv(output_dir / "phase06_hypothesis_tests.csv", tests, TEST_FIELDS)
    effects_path = write_csv(output_dir / "phase06_effect_sizes.csv", effects, EFFECT_FIELDS)
    categorical_path = write_csv(
        output_dir / "phase06_categorical_tests.csv", categorical, CATEGORICAL_FIELDS
    )
    report_path = write_markdown_report(
        output_dir / "phase06_hypothesis_tests.md", tests, effects, categorical
    )

    print(f"Hypothesis tests: {tests_path}")
    print(f"Effect sizes: {effects_path}")
    print(f"Categorical tests: {categorical_path}")
    print(f"Markdown report: {report_path}")
    print(f"SciPy available: {SCIPY_AVAILABLE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
