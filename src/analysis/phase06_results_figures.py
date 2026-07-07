#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate manuscript figures from the reproduced Phase 05 and Phase 06 tables.

Figures generated:
- Figure 5. Paired terminal landing error by treatment.
- Figure 6. Temporal and lateral-behavior outcomes.
- Figure 7. Scenario-level paired treatment differences.

Inputs are read directly from the Phase 05 and Phase 06 CSV outputs. Outputs
are exported as PNG (300 dpi) and SVG for article or thesis preparation.

Reproducibility role:
    Produces visual summaries from versioned analytical tables; it does not
    rerun AirSimNH, PX4 SITL, MAVLink/Offboard control, or perception modules.

Scope:
    Figures describe the controlled simulation dataset only. They should not be
    used as evidence of physical touchdown behavior, real-flight deployment, or
    sim-to-real transfer.

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
PANEL_LABEL_KW = dict(fontsize=10.8, fontweight="bold", va="top", ha="left")
ANNOTATION_KW = dict(fontsize=9.5, va="top", ha="left")
ANNOTATION_BOX_KW = dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none", alpha=0.82)

# Color-blind-friendly publication palette with restrained accents.
T0_COLOR = "#4C78A8"  # muted blue
T1_COLOR = "#ECA06A"  # muted orange
PAIR_LINE_COLOR = "0.62"
MEAN_COLOR = "0.05"
DIFFERENCE_COLOR = "#2A9D8F"  # teal accent for paired differences
BAR_COLORS = ["#6A9FB5", "#8FA37A", "#C08A5A"]
BAR_EDGES = ["#2F5968", "#536445", "#744B2A"]
ZERO_LINE_COLOR = "0.35"


def configure_matplotlib() -> None:
    """Configure a restrained manuscript-oriented matplotlib style."""
    plt.rcParams.update(
        {
            "figure.dpi": 220,
            "savefig.dpi": 600,
            "font.family": "DejaVu Sans",
            "font.size": 10.5,
            "axes.labelsize": 10.5,
            "axes.titlesize": 11.0,
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 9.5,
            "legend.fontsize": 9.5,
            "axes.linewidth": 0.8,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "grid.color": "0.86",
            "grid.linewidth": 0.65,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def require_columns(df: pd.DataFrame, required: Sequence[str], name: str) -> None:
    """Fail fast when a reproduced table does not match the expected schema."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def require_len(df: pd.DataFrame, n: int, name: str) -> None:
    """Assert the expected row count for manuscript figure inputs."""
    if len(df) != n:
        raise ValueError(f"{name} should contain {n} rows, but contains {len(df)} rows.")


def scenario_short_from_id(scenario_id: str) -> str:
    """Extract S01-S08 from IDs such as P05_S01_H2_Y04_YAW0."""
    match = re.search(r"(S\d{2})", str(scenario_id))
    if not match:
        raise ValueError(f"Could not extract scenario_short from scenario_id={scenario_id!r}")
    return match.group(1)


def add_scenario_short(df: pd.DataFrame) -> pd.DataFrame:
    """Add ordered S01-S08 scenario labels used for plotting."""
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
    """Format the reproduced statistical-test label for figure annotation."""
    row = hyp.loc[hyp["metric"].eq(metric)]
    if row.empty:
        return "statistical test unavailable"
    r = row.iloc[0]
    selected = str(r["selected_test"])
    selected = selected.replace("Paired t-test", "paired t-test")
    selected = selected.replace("Wilcoxon signed-rank", "Wilcoxon signed-rank")
    return f"{selected}, {p_text(float(r['p_value']))}"


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(-0.015, 1.035, label, transform=ax.transAxes, clip_on=False, **PANEL_LABEL_KW)


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{stem}.png"
    svg_path = output_dir / f"{stem}.svg"
    pdf_path = output_dir / f"{stem}.pdf"
    fig.savefig(png_path, bbox_inches="tight", dpi=600)
    fig.savefig(svg_path, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {png_path}")
    print(f"Saved: {svg_path}")
    print(f"Saved: {pdf_path}")


def strip_by_scenario(
    ax: plt.Axes,
    df: pd.DataFrame,
    value_col: str,
    xlabel: str,
    jitter_seed: int = 123,
    point_size: float = 22,
    color: str = DIFFERENCE_COLOR,
) -> None:
    """Horizontal strip plot grouped by scenario using matplotlib only."""
    rng = np.random.default_rng(jitter_seed)
    for idx, scenario in enumerate(SCENARIO_ORDER):
        vals = df.loc[df["scenario_short"].astype(str).eq(scenario), value_col].dropna().to_numpy()
        if len(vals) == 0:
            continue
        y = idx + rng.uniform(-0.18, 0.18, size=len(vals))
        ax.scatter(vals, y, s=point_size, alpha=0.78, color=color, edgecolors="white", linewidths=0.25)
        # Add median marker for scenario-level visual reference.
        ax.plot(np.median(vals), idx, marker="|", color=MEAN_COLOR, markersize=13, markeredgewidth=1.7)
    ax.axvline(0, color=ZERO_LINE_COLOR, linewidth=0.9, linestyle="--")
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
    """Load and validate all tabular inputs required for result figures."""
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
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(8.0, 4.0),
        gridspec_kw={"width_ratios": [0.95, 1.3]},
        constrained_layout=True,
    )
    ax = axes[0]

    # Panel (a): paired plot T0 vs T1.
    for _, r in pairwise.iterrows():
        ax.plot([0, 1], [r["final_error_m_t0"], r["final_error_m_t1"]], color=PAIR_LINE_COLOR, alpha=0.42, linewidth=0.8)
    ax.scatter(np.zeros(len(pairwise)), pairwise["final_error_m_t0"], s=22, color=T0_COLOR, alpha=0.78, edgecolors="white", linewidths=0.25)
    ax.scatter(np.ones(len(pairwise)), pairwise["final_error_m_t1"], s=22, color=T1_COLOR, alpha=0.78, edgecolors="white", linewidths=0.25)

    means = [pairwise["final_error_m_t0"].mean(), pairwise["final_error_m_t1"].mean()]
    sds = [pairwise["final_error_m_t0"].std(ddof=1), pairwise["final_error_m_t1"].std(ddof=1)]
    ax.errorbar([0, 1], means, yerr=sds, fmt="o", color=MEAN_COLOR, ecolor=MEAN_COLOR, capsize=3.5, markersize=4.8, linewidth=1.2, label="Mean ± SD")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["T0", "T1"])
    ax.set_ylabel("Terminal landing error (m)")
    ax.set_xlabel("Treatment")
    ax.grid(axis="y")
    ax.set_xlim(-0.35, 1.35)
    ax.text(
        0.06,
        0.93,
        f"n = {len(pairwise)} pairs\n{test_label(hypothesis, 'final_error_m_delta_t0_minus_t1')}",
        transform=ax.transAxes,
        bbox=ANNOTATION_BOX_KW,
        **ANNOTATION_KW,
    )
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

    save_figure(fig, output_dir, "figure5_paired_terminal_landing_error")


def make_figure6(pairwise: pd.DataFrame, accepted: pd.DataFrame, hypothesis: pd.DataFrame, output_dir: Path) -> None:
    """Figure 6. Temporal and lateral-behavior outcomes."""
    wide = accepted_wide(accepted)

    fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.0), constrained_layout=False)
    ax = axes[0, 0]

    # Panel (a): paired landing-loop time by treatment.
    for _, r in pairwise.iterrows():
        ax.plot([0, 1], [r["landing_time_s_t0"], r["landing_time_s_t1"]], color=PAIR_LINE_COLOR, alpha=0.42, linewidth=0.8)
    ax.scatter(np.zeros(len(pairwise)), pairwise["landing_time_s_t0"], s=22, color=T0_COLOR, alpha=0.78, edgecolors="white", linewidths=0.25)
    ax.scatter(np.ones(len(pairwise)), pairwise["landing_time_s_t1"], s=22, color=T1_COLOR, alpha=0.78, edgecolors="white", linewidths=0.25)
    means = [pairwise["landing_time_s_t0"].mean(), pairwise["landing_time_s_t1"].mean()]
    sds = [pairwise["landing_time_s_t0"].std(ddof=1), pairwise["landing_time_s_t1"].std(ddof=1)]
    ax.errorbar([0, 1], means, yerr=sds, fmt="o", color=MEAN_COLOR, ecolor=MEAN_COLOR, capsize=3.5, markersize=4.8, linewidth=1.2)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["T0", "T1"])
    ax.set_ylabel("Landing-loop time (s)")
    ax.set_xlabel("Treatment")
    ax.grid(axis="y")
    ax.set_xlim(-0.35, 1.35)
    ax.text(0.04, 0.96, test_label(hypothesis, "landing_time_s_delta_t0_minus_t1"), transform=ax.transAxes, **ANNOTATION_KW)
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
    ax.text(0.04, 0.96, test_label(hypothesis, "command_count_delta_t1_minus_t0"), transform=ax.transAxes, **ANNOTATION_KW)
    panel_label(ax, "(c)")

    # Panel (d): maximum absolute horizontal command by treatment.
    ax = axes[1, 1]
    for _, r in wide.iterrows():
        ax.plot(
            [0, 1],
            [r["max_abs_horizontal_command_m_s_T0"], r["max_abs_horizontal_command_m_s_T1"]],
            color=PAIR_LINE_COLOR,
            alpha=0.42,
            linewidth=0.8,
        )
    ax.scatter(np.zeros(len(wide)), wide["max_abs_horizontal_command_m_s_T0"], s=22, color=T0_COLOR, alpha=0.78, edgecolors="white", linewidths=0.25)
    ax.scatter(np.ones(len(wide)), wide["max_abs_horizontal_command_m_s_T1"], s=22, color=T1_COLOR, alpha=0.78, edgecolors="white", linewidths=0.25)
    means = [
        wide["max_abs_horizontal_command_m_s_T0"].mean(),
        wide["max_abs_horizontal_command_m_s_T1"].mean(),
    ]
    sds = [
        wide["max_abs_horizontal_command_m_s_T0"].std(ddof=1),
        wide["max_abs_horizontal_command_m_s_T1"].std(ddof=1),
    ]
    ax.errorbar([0, 1], means, yerr=sds, fmt="o", color=MEAN_COLOR, ecolor=MEAN_COLOR, capsize=3.5, markersize=4.8, linewidth=1.2)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["T0", "T1"])
    ax.set_ylabel("Maximum absolute horizontal command (m/s)", fontsize=10.0, labelpad=8)
    ax.set_xlabel("Treatment")
    ax.grid(axis="y")
    ax.set_xlim(-0.35, 1.35)
    ax.text(0.04, 0.96, test_label(hypothesis, "max_abs_horizontal_command_m_s_delta_t1_minus_t0"), transform=ax.transAxes, **ANNOTATION_KW)
    panel_label(ax, "(d)")

    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.09, top=0.94, wspace=0.32, hspace=0.34)
    save_figure(fig, output_dir, "figure6_temporal_lateral_behavior_outcomes")


def make_figure7(scenario: pd.DataFrame, output_dir: Path, show_factor_labels: bool = False) -> None:
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
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 4.5), sharey=True, constrained_layout=True)

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

    for idx, (ax, col, xlabel, label) in enumerate(panels):
        ax.barh(y, scenario[col], color=BAR_COLORS[idx], edgecolor=BAR_EDGES[idx], linewidth=0.7, height=0.72, alpha=0.88)
        ax.axvline(0, color=ZERO_LINE_COLOR, linewidth=0.9, linestyle="--")
        ax.set_xlabel(xlabel)
        ax.grid(axis="x")
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        panel_label(ax, label)

    axes[0].set_yticks(y)
    axes[0].set_yticklabels(ylabels)
    axes[0].invert_yaxis()
    axes[0].set_ylabel("Scenario")

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
        "--factor-scenario-labels",
        action="store_true",
        help="Use compact factor labels in Figure 7 instead of the default S01-S08 manuscript labels.",
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
    make_figure7(scenario, output_dir, show_factor_labels=args.factor_scenario_labels)

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
        print(f"- {stem}.pdf")


if __name__ == "__main__":
    main()
