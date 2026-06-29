#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Results figures for the AirSimNH-PX4 SITL UAV landing manuscript.

Figures generated:
- Figure 5. Paired terminal landing error by treatment.
- Figure 6. Temporal and lateral-behavior outcomes.
- Figure 7. Scenario-level paired treatment differences.

Inputs are read directly from the Phase 05 and Phase 06 CSV outputs.
Outputs are exported as PNG (300 dpi) and SVG.

Author: generated for reproducible manuscript figure production.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# -----------------------------------------------------------------------------
# Default paths relative to the repository root.
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PHASE05_DIR = PROJECT_ROOT / "outputs" / "tables" / "phase05_experiments"
DEFAULT_PHASE06_DIR = PROJECT_ROOT / "outputs" / "tables" / "phase06_analysis"


# -----------------------------------------------------------------------------
# Plot style helpers.
# -----------------------------------------------------------------------------
SCENARIO_ORDER = [f"S{i:02d}" for i in range(1, 9)]
PANEL_LABEL_KW = dict(fontsize=10, fontweight="bold", va="top", ha="left")


def configure_matplotlib() -> None:
    """Configure a restrained manuscript-oriented matplotlib style."""
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.labelsize": 8.5,
            "axes.titlesize": 9.0,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "legend.fontsize": 8.0,
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "grid.color": "0.88",
            "grid.linewidth": 0.6,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def require_columns(df: pd.DataFrame, required: Sequence[str], name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def require_len(df: pd.DataFrame, n: int, name: str) -> None:
    if len(df) != n:
        raise ValueError(f"{name} should contain {n} rows, but contains {len(df)} rows.")


def scenario_short_from_id(scenario_id: str) -> str:
    """Extract S01-S08 from IDs such as P05_S01_H2_Y04_YAW0."""
    match = re.search(r"(S\d{2})", str(scenario_id))
    if not match:
        raise ValueError(f"Could not extract scenario_short from scenario_id={scenario_id!r}")
    return match.group(1)


def add_scenario_short(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "scenario_short" not in out.columns:
        out["scenario_short"] = out["scenario_id"].apply(scenario_short_from_id)
    out["scenario_short"] = pd.Categorical(out["scenario_short"], categories=SCENARIO_ORDER, ordered=True)
    return out


def p_text(p_value: float) -> str:
    """Journal-style p-value label for figure annotations."""
    if pd.isna(p_value):
        return "p = NA"
    if p_value < 0.001:
        return "p < 0.001"
    return f"p = {p_value:.3f}"


def test_label(hyp: pd.DataFrame, metric: str) -> str:
    row = hyp.loc[hyp["metric"].eq(metric)]
    if row.empty:
        return "statistical test unavailable"
    r = row.iloc[0]
    selected = str(r["selected_test"])
    selected = selected.replace("Paired t-test", "paired t-test")
    selected = selected.replace("Wilcoxon signed-rank", "Wilcoxon signed-rank")
    return f"{selected}, {p_text(float(r['p_value']))}"


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(0.0, 1.03, label, transform=ax.transAxes, **PANEL_LABEL_KW)


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{stem}.png"
    svg_path = output_dir / f"{stem}.svg"
    fig.savefig(png_path, bbox_inches="tight", dpi=300)
    fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {png_path}")
    print(f"Saved: {svg_path}")


def strip_by_scenario(
    ax: plt.Axes,
    df: pd.DataFrame,
    value_col: str,
    xlabel: str,
    jitter_seed: int = 123,
    point_size: float = 15,
    color: str = "0.20",
) -> None:
    """Horizontal strip plot grouped by scenario using matplotlib only."""
    rng = np.random.default_rng(jitter_seed)
    for idx, scenario in enumerate(SCENARIO_ORDER):
        vals = df.loc[df["scenario_short"].astype(str).eq(scenario), value_col].dropna().to_numpy()
        if len(vals) == 0:
            continue
        y = idx + rng.uniform(-0.18, 0.18, size=len(vals))
        ax.scatter(vals, y, s=point_size, alpha=0.72, color=color, edgecolors="none")
        # Add median marker for scenario-level visual reference.
        ax.plot(np.median(vals), idx, marker="|", color="black", markersize=11, markeredgewidth=1.5)
    ax.axvline(0, color="0.45", linewidth=0.9, linestyle="--")
    ax.set_yticks(range(len(SCENARIO_ORDER)))
    ax.set_yticklabels(SCENARIO_ORDER)
    ax.set_xlabel(xlabel)
    ax.grid(axis="x")
    ax.set_ylim(-0.6, len(SCENARIO_ORDER) - 0.4)
    ax.invert_yaxis()


# -----------------------------------------------------------------------------
# Data loading and validation.
# -----------------------------------------------------------------------------
def load_data(phase05_dir: Path, phase06_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pairwise_path = phase05_dir / "phase05_pairwise_differences.csv"
    accepted_path = phase05_dir / "phase05_accepted_runs.csv"
    scenario_path = phase06_dir / "phase06_scenario_analysis.csv"
    hypothesis_path = phase06_dir / "phase06_hypothesis_tests.csv"
    pairwise_summary_path = phase06_dir / "phase06_pairwise_difference_summary.csv"

    for path in [pairwise_path, accepted_path, scenario_path, hypothesis_path, pairwise_summary_path]:
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")

    pairwise = pd.read_csv(pairwise_path)
    accepted = pd.read_csv(accepted_path)
    scenario = pd.read_csv(scenario_path)
    hypothesis = pd.read_csv(hypothesis_path)
    pairwise_summary = pd.read_csv(pairwise_summary_path)

    require_columns(
        pairwise,
        [
            "scenario_id",
            "treatment_pair_id",
            "repetition",
            "final_error_m_t0",
            "final_error_m_t1",
            "final_error_m_delta_t0_minus_t1",
            "landing_time_s_t0",
            "landing_time_s_t1",
            "landing_time_s_delta_t0_minus_t1",
            "accepted_detection_rate_t0",
            "accepted_detection_rate_t1",
            "accepted_detection_rate_delta_t1_minus_t0",
        ],
        "phase05_pairwise_differences.csv",
    )
    require_columns(
        accepted,
        [
            "run_id",
            "treatment",
            "scenario_id",
            "treatment_pair_id",
            "repetition",
            "curation_status",
            "command_count",
            "max_abs_horizontal_command_m_s",
            "landing_time_s",
            "final_error_m",
        ],
        "phase05_accepted_runs.csv",
    )
    require_columns(
        scenario,
        [
            "scenario_short",
            "scenario_id",
            "height_m",
            "offset_y_m",
            "yaw_deg",
            "n_pairs",
            "final_error_delta_mean_t0_minus_t1",
            "landing_time_delta_mean_t0_minus_t1",
            "detection_rate_delta_mean_t1_minus_t0",
        ],
        "phase06_scenario_analysis.csv",
    )
    require_columns(
        hypothesis,
        [
            "hypothesis",
            "metric",
            "n",
            "selected_test",
            "test_statistic",
            "p_value",
            "alpha",
            "decision",
        ],
        "phase06_hypothesis_tests.csv",
    )

    require_len(pairwise, 80, "phase05_pairwise_differences.csv")
    require_len(accepted, 160, "phase05_accepted_runs.csv")
    require_len(scenario, 8, "phase06_scenario_analysis.csv")

    if accepted["treatment"].value_counts().to_dict() != {"T0": 80, "T1": 80}:
        raise ValueError(
            "phase05_accepted_runs.csv must contain exactly 80 T0 runs and 80 T1 runs. "
            f"Found: {accepted['treatment'].value_counts().to_dict()}"
        )
    if not scenario["n_pairs"].eq(10).all():
        raise ValueError("Each scenario in phase06_scenario_analysis.csv must have n_pairs = 10.")
    if set(scenario["scenario_short"].astype(str)) != set(SCENARIO_ORDER):
        raise ValueError(
            "Scenario labels in phase06_scenario_analysis.csv must be exactly S01-S08. "
            f"Found: {sorted(scenario['scenario_short'].astype(str).unique())}"
        )

    pairwise = add_scenario_short(pairwise)
    accepted = add_scenario_short(accepted)
    scenario = scenario.copy()
    scenario["scenario_short"] = pd.Categorical(scenario["scenario_short"], categories=SCENARIO_ORDER, ordered=True)
    scenario = scenario.sort_values("scenario_short")

    print("Validation summary")
    print("------------------")
    print(f"Pairwise rows: {len(pairwise)}")
    print(f"Accepted runs: {len(accepted)}")
    print(f"Treatment counts: {accepted['treatment'].value_counts().to_dict()}")
    print(f"Scenario rows: {len(scenario)}")
    print(f"Scenario n_pairs: {scenario['n_pairs'].tolist()}")
    print()

    return pairwise, accepted, scenario, hypothesis, pairwise_summary


def accepted_wide(accepted: pd.DataFrame) -> pd.DataFrame:
    """Create one row per pair with T0/T1 command and max-command values."""
    value_cols = ["command_count", "max_abs_horizontal_command_m_s", "landing_time_s"]
    idx_cols = ["treatment_pair_id", "scenario_id", "scenario_short", "repetition"]

    wide = accepted.pivot_table(
        index=idx_cols,
        columns="treatment",
        values=value_cols,
        aggfunc="first",
        observed=False,
    )
    wide.columns = [f"{metric}_{treatment}" for metric, treatment in wide.columns]
    wide = wide.reset_index()

    needed = [
        "command_count_T0",
        "command_count_T1",
        "max_abs_horizontal_command_m_s_T0",
        "max_abs_horizontal_command_m_s_T1",
    ]
    require_columns(wide, needed, "accepted_wide")

    wide["command_count_delta_t1_minus_t0"] = wide["command_count_T1"] - wide["command_count_T0"]
    wide["max_abs_horizontal_command_m_s_delta_t1_minus_t0"] = (
        wide["max_abs_horizontal_command_m_s_T1"] - wide["max_abs_horizontal_command_m_s_T0"]
    )
    wide["scenario_short"] = pd.Categorical(wide["scenario_short"].astype(str), categories=SCENARIO_ORDER, ordered=True)
    return wide.sort_values(["scenario_short", "repetition"])


# -----------------------------------------------------------------------------
# Figure generation.
# -----------------------------------------------------------------------------
def make_figure5(pairwise: pd.DataFrame, hypothesis: pd.DataFrame, output_dir: Path) -> None:
    """Figure 5. Paired terminal landing error by treatment."""
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.35), gridspec_kw={"width_ratios": [0.95, 1.25]})
    ax = axes[0]

    # Panel (a): paired plot T0 vs T1.
    for _, r in pairwise.iterrows():
        ax.plot([0, 1], [r["final_error_m_t0"], r["final_error_m_t1"]], color="0.55", alpha=0.36, linewidth=0.65)
    ax.scatter(np.zeros(len(pairwise)), pairwise["final_error_m_t0"], s=12, color="0.20", alpha=0.62, label="Pair values")
    ax.scatter(np.ones(len(pairwise)), pairwise["final_error_m_t1"], s=12, color="0.20", alpha=0.62)

    means = [pairwise["final_error_m_t0"].mean(), pairwise["final_error_m_t1"].mean()]
    sds = [pairwise["final_error_m_t0"].std(ddof=1), pairwise["final_error_m_t1"].std(ddof=1)]
    ax.errorbar([0, 1], means, yerr=sds, fmt="o", color="black", ecolor="black", capsize=3, markersize=4, linewidth=1.1, label="Mean ± SD")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["T0", "T1"])
    ax.set_ylabel("Terminal landing error (m)")
    ax.set_xlabel("Treatment")
    ax.grid(axis="y")
    ax.set_xlim(-0.35, 1.35)
    ax.text(0.03, 0.96, f"n = {len(pairwise)} pairs\n{test_label(hypothesis, 'final_error_m_delta_t0_minus_t1')}", transform=ax.transAxes, va="top", ha="left", fontsize=7.6)
    panel_label(ax, "(a)")

    # Panel (b): paired differences by scenario.
    ax = axes[1]
    strip_by_scenario(
        ax,
        pairwise,
        "final_error_m_delta_t0_minus_t1",
        "Terminal landing error reduction, T0 − T1 (m)",
        jitter_seed=501,
    )
    panel_label(ax, "(b)")

    fig.tight_layout(w_pad=2.0)
    save_figure(fig, output_dir, "figure5_paired_terminal_landing_error")


def make_figure6(pairwise: pd.DataFrame, accepted: pd.DataFrame, hypothesis: pd.DataFrame, output_dir: Path) -> None:
    """Figure 6. Temporal and lateral-behavior outcomes."""
    wide = accepted_wide(accepted)

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.6))
    ax = axes[0, 0]

    # Panel (a): paired landing-loop time by treatment.
    for _, r in pairwise.iterrows():
        ax.plot([0, 1], [r["landing_time_s_t0"], r["landing_time_s_t1"]], color="0.55", alpha=0.36, linewidth=0.65)
    ax.scatter(np.zeros(len(pairwise)), pairwise["landing_time_s_t0"], s=12, color="0.20", alpha=0.62)
    ax.scatter(np.ones(len(pairwise)), pairwise["landing_time_s_t1"], s=12, color="0.20", alpha=0.62)
    means = [pairwise["landing_time_s_t0"].mean(), pairwise["landing_time_s_t1"].mean()]
    sds = [pairwise["landing_time_s_t0"].std(ddof=1), pairwise["landing_time_s_t1"].std(ddof=1)]
    ax.errorbar([0, 1], means, yerr=sds, fmt="o", color="black", ecolor="black", capsize=3, markersize=4, linewidth=1.1)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["T0", "T1"])
    ax.set_ylabel("Landing-loop time (s)")
    ax.set_xlabel("Treatment")
    ax.grid(axis="y")
    ax.set_xlim(-0.35, 1.35)
    ax.text(0.03, 0.96, test_label(hypothesis, "landing_time_s_delta_t0_minus_t1"), transform=ax.transAxes, va="top", ha="left", fontsize=7.6)
    panel_label(ax, "(a)")

    # Panel (b): landing-loop time difference by scenario.
    ax = axes[0, 1]
    strip_by_scenario(
        ax,
        pairwise,
        "landing_time_s_delta_t0_minus_t1",
        "Landing-loop time difference, T0 − T1 (s)",
        jitter_seed=602,
    )
    panel_label(ax, "(b)")

    # Panel (c): command-count difference by scenario.
    ax = axes[1, 0]
    strip_by_scenario(
        ax,
        wide,
        "command_count_delta_t1_minus_t0",
        "Command-count difference, T1 − T0",
        jitter_seed=603,
    )
    ax.text(0.03, 0.96, test_label(hypothesis, "command_count_delta_t1_minus_t0"), transform=ax.transAxes, va="top", ha="left", fontsize=7.6)
    panel_label(ax, "(c)")

    # Panel (d): maximum absolute horizontal command by treatment.
    ax = axes[1, 1]
    for _, r in wide.iterrows():
        ax.plot(
            [0, 1],
            [r["max_abs_horizontal_command_m_s_T0"], r["max_abs_horizontal_command_m_s_T1"]],
            color="0.55",
            alpha=0.36,
            linewidth=0.65,
        )
    ax.scatter(np.zeros(len(wide)), wide["max_abs_horizontal_command_m_s_T0"], s=12, color="0.20", alpha=0.62)
    ax.scatter(np.ones(len(wide)), wide["max_abs_horizontal_command_m_s_T1"], s=12, color="0.20", alpha=0.62)
    means = [
        wide["max_abs_horizontal_command_m_s_T0"].mean(),
        wide["max_abs_horizontal_command_m_s_T1"].mean(),
    ]
    sds = [
        wide["max_abs_horizontal_command_m_s_T0"].std(ddof=1),
        wide["max_abs_horizontal_command_m_s_T1"].std(ddof=1),
    ]
    ax.errorbar([0, 1], means, yerr=sds, fmt="o", color="black", ecolor="black", capsize=3, markersize=4, linewidth=1.1)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["T0", "T1"])
    ax.set_ylabel("Maximum absolute horizontal command (m/s)")
    ax.set_xlabel("Treatment")
    ax.grid(axis="y")
    ax.set_xlim(-0.35, 1.35)
    ax.text(0.03, 0.96, test_label(hypothesis, "max_abs_horizontal_command_m_s_delta_t1_minus_t0"), transform=ax.transAxes, va="top", ha="left", fontsize=7.6)
    panel_label(ax, "(d)")

    fig.tight_layout(h_pad=2.0, w_pad=2.0)
    save_figure(fig, output_dir, "figure6_temporal_lateral_behavior_outcomes")


def make_figure7(scenario: pd.DataFrame, output_dir: Path, show_factor_labels: bool = True) -> None:
    """Figure 7. Scenario-level paired treatment differences."""
    scenario = scenario.sort_values("scenario_short").copy()
    if show_factor_labels:
        ylabels = [
            f"{r.scenario_short} | H={r.height_m:.1f}, Y={r.offset_y_m:.1f}, yaw={int(r.yaw_deg)}°"
            for r in scenario.itertuples(index=False)
        ]
    else:
        ylabels = scenario["scenario_short"].astype(str).tolist()

    y = np.arange(len(scenario))
    fig, axes = plt.subplots(1, 3, figsize=(8.4, 3.65), sharey=True)

    panels = [
        (
            axes[0],
            "final_error_delta_mean_t0_minus_t1",
            "Terminal landing error reduction,\nT0 − T1 (m)",
            "(a)",
        ),
        (
            axes[1],
            "landing_time_delta_mean_t0_minus_t1",
            "Landing-loop time delta,\nT0 − T1 (s)",
            "(b)",
        ),
        (
            axes[2],
            "detection_rate_delta_mean_t1_minus_t0",
            "Accepted-detection-rate gain,\nT1 − T0",
            "(c)",
        ),
    ]

    for ax, col, xlabel, label in panels:
        ax.barh(y, scenario[col], color="0.55", edgecolor="0.25", linewidth=0.6, height=0.66)
        ax.axvline(0, color="0.35", linewidth=0.9, linestyle="--")
        ax.set_xlabel(xlabel)
        ax.grid(axis="x")
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        panel_label(ax, label)

    axes[0].set_yticks(y)
    axes[0].set_yticklabels(ylabels)
    axes[0].invert_yaxis()
    axes[0].set_ylabel("Scenario")

    fig.tight_layout(w_pad=2.0)
    save_figure(fig, output_dir, "figure7_scenario_level_treatment_differences")


# -----------------------------------------------------------------------------
# Main CLI.
# -----------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Figures 5-7 for the AirSimNH-PX4 SITL UAV landing manuscript."
    )
    parser.add_argument(
        "--phase05-dir",
        type=Path,
        default=DEFAULT_PHASE05_DIR,
        help="Directory containing Phase 05 CSV outputs.",
    )
    parser.add_argument(
        "--phase06-dir",
        type=Path,
        default=DEFAULT_PHASE06_DIR,
        help="Directory containing Phase 06 CSV outputs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Directory where figures will be exported. "
            "Default: <repo>/outputs/figures/phase06_results inferred from phase05-dir."
        ),
    )
    parser.add_argument(
        "--short-scenario-labels",
        action="store_true",
        help="Use only S01-S08 labels in Figure 7 instead of compact factor labels.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    phase05_dir = args.phase05_dir
    phase06_dir = args.phase06_dir

    if args.output_dir is None:
        # phase05_dir = <repo>/outputs/tables/phase05_experiments
        # phase05_dir.parents[1] = <repo>/outputs
        output_dir = phase05_dir.parents[1] / "figures" / "phase06_results"
    else:
        output_dir = args.output_dir

    configure_matplotlib()
    pairwise, accepted, scenario, hypothesis, pairwise_summary = load_data(phase05_dir, phase06_dir)

    make_figure5(pairwise, hypothesis, output_dir)
    make_figure6(pairwise, accepted, hypothesis, output_dir)
    make_figure7(scenario, output_dir, show_factor_labels=not args.short_scenario_labels)

    print()
    print("Figure generation completed.")
    print(f"Output directory: {output_dir}")
    print("Generated files:")
    for stem in [
        "figure5_paired_terminal_landing_error",
        "figure6_temporal_lateral_behavior_outcomes",
        "figure7_scenario_level_treatment_differences",
    ]:
        print(f"- {stem}.png")
        print(f"- {stem}.svg")


if __name__ == "__main__":
    main()
