"""Generate the Phase 05 formal execution plan and command blocks."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.experiments.phase05_config import load_phase05_config, resolve_project_path


PLAN_FIELDS = [
    "run_index",
    "scenario_id",
    "treatment",
    "treatment_pair_id",
    "repetition",
    "initial_height_m",
    "offset_x_m",
    "offset_y_m",
    "yaw_deg",
    "duration_s",
    "marker_object_name",
]


def build_run_plan(config: dict[str, Any]) -> list[dict[str, object]]:
    repetitions = int(config.get("formal_design", {}).get("repetitions_per_treatment", 10))
    rows: list[dict[str, object]] = []
    run_index = 1
    for scenario in config.get("scenarios", []):
        scenario_id = str(scenario["scenario_id"])
        scenario_short = scenario_id.lower().replace("p05_", "")
        for repetition in range(1, repetitions + 1):
            treatment_order = ["T0", "T1"] if repetition % 2 == 1 else ["T1", "T0"]
            pair_id = f"{scenario_id}_R{repetition:02d}"
            for treatment in treatment_order:
                marker_object_name = f"phase05_{scenario_short}_r{repetition:02d}_{treatment.lower()}"
                rows.append(
                    {
                        "run_index": run_index,
                        "scenario_id": scenario_id,
                        "treatment": treatment,
                        "treatment_pair_id": pair_id,
                        "repetition": repetition,
                        "initial_height_m": scenario.get("initial_height_m", ""),
                        "offset_x_m": scenario.get("offset_x_m", 0.0),
                        "offset_y_m": scenario.get("offset_y_m", 0.0),
                        "yaw_deg": scenario.get("yaw_deg", 0.0),
                        "duration_s": _duration_for_height(config, scenario.get("initial_height_m")),
                        "marker_object_name": marker_object_name,
                    }
                )
                run_index += 1
    return rows


def write_plan_csv(rows: list[dict[str, object]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=PLAN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def write_commands_markdown(
    rows: list[dict[str, object]],
    output_path: Path,
    config: dict[str, Any],
    start_index: int,
    limit: int | None,
) -> Path:
    selected = [
        row
        for row in rows
        if int(row["run_index"]) >= start_index and (limit is None or int(row["run_index"]) < start_index + limit)
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        file.write("# Phase 05 Formal Run Commands\n\n")
        file.write("Run these commands from the repository root with `.venv` active.\n\n")
        file.write("```powershell\n")
        file.write("cd <REPO_ROOT>\n")
        file.write(".\\.venv\\Scripts\\Activate.ps1\n")
        file.write("```\n\n")
        for row in selected:
            file.write(f"## Run {row['run_index']}: {row['scenario_id']} {row['treatment']} R{int(row['repetition']):02d}\n\n")
            file.write("```powershell\n")
            file.write("\n".join(_commands_for_row(row, config)))
            file.write("\n```\n\n")
            file.write("After this run, verify telemetry before continuing to the next command block.\n\n")
    return output_path


def _commands_for_row(row: dict[str, object], config: dict[str, Any]) -> list[str]:
    frozen = config.get("frozen_t1", {})
    execution = config.get("formal_execution", {})
    yaw_setup = execution.get("yaw_setup", {})
    takeoff_samples = int(execution.get("takeoff_samples_after", 8))
    telemetry_duration = int(execution.get("telemetry_check_duration_s", 5))
    marker_z = float(execution.get("marker_z", 0.0))
    yaw_deg = float(row["yaw_deg"])
    treatment = str(row["treatment"])
    treatment_script = (
        "src\\control\\run_phase05_t0_baseline_descent.py"
        if treatment == "T0"
        else "src\\control\\run_phase05_t1_visual_descent.py"
    )

    commands = [
        'python src\\perception\\clear_landing_markers.py --object-regex ".*phase05.*"',
        (
            "python src\\control\\run_px4_takeoff_land_test.py --confirm-send "
            f"--takeoff-altitude {float(row['initial_height_m']):.1f} "
            f"--samples-after-takeoff {takeoff_samples} --no-land-after"
        )
    ]
    commands.append(
        "python src\\control\\run_phase05_yaw_setup.py --confirm-send "
        f"--method {yaw_setup.get('method', 'offboard-yaw-rate')} "
        f"--absolute-yaw-deg {yaw_deg:.1f} "
        f"--yaw-speed-deg-s {float(yaw_setup.get('yaw_speed_deg_s', 10.0)):.1f} "
        f"--yaw-kp {float(yaw_setup.get('yaw_kp', 0.8)):.2f} "
        f"--tolerance-deg {float(yaw_setup.get('tolerance_deg', 3.0)):.1f} "
        f"--wait-timeout {float(yaw_setup.get('timeout_s', 25.0)):.1f}"
    )
    commands.append(
        "python src\\perception\\spawn_fiducial_marker.py "
        f"--object-name {row['marker_object_name']} --under-vehicle "
        f"--offset-x {float(row['offset_x_m']):.1f} --offset-y {float(row['offset_y_m']):.1f} --z {marker_z:.1f} "
        f"--scale-x {float(frozen.get('marker_scale_x', 1.2)):.1f} "
        f"--scale-y {float(frozen.get('marker_scale_y', 1.2)):.1f} "
        f"--scale-z {float(frozen.get('marker_scale_z', 0.01)):.2f} "
        f"--dictionary-name {frozen.get('dictionary_name', 'DICT_4X4_50')} "
        f"--marker-id {int(frozen.get('marker_id', 23))} "
        f"--texture-size-px {int(frozen.get('texture_size_px', 2048))} "
        f"--marker-size-ratio {float(frozen.get('marker_size_ratio', 0.72)):.2f}"
    )

    treatment_command = (
        f"python {treatment_script} --confirm-send "
        f"--duration {float(row['duration_s']):.0f} "
        "--detector aruco --save-annotated "
    )
    if treatment == "T1":
        treatment_command += (
            f"--max-horizontal-speed {float(frozen.get('max_horizontal_speed_m_s', 0.10)):.2f} "
            f"--max-missing-detections {int(frozen.get('max_missing_detections', 3))} "
            "--enable-descent "
            f"--descent-rate {float(frozen.get('descent_rate_m_s', 0.08)):.2f} "
            f"--centered-cycles-required {int(frozen.get('centered_cycles_required', 5))} "
            f"--landing-complete-altitude {float(frozen.get('landing_complete_altitude_m', 0.80)):.2f} "
        )
    else:
        treatment_command += (
            f"--descent-rate {float(frozen.get('descent_rate_m_s', 0.08)):.2f} "
            f"--landing-complete-altitude {float(frozen.get('landing_complete_altitude_m', 0.80)):.2f} "
        )

    treatment_command += (
        f"--scenario-id {row['scenario_id']} "
        f"--marker-object-name {row['marker_object_name']} "
        f"--treatment-pair-id {row['treatment_pair_id']} "
        f"--repetition {int(row['repetition'])} "
        f"--planned-initial-height-m {float(row['initial_height_m']):.1f} "
        f"--planned-offset-x-m {float(row['offset_x_m']):.1f} "
        f"--planned-offset-y-m {float(row['offset_y_m']):.1f} "
        f"--planned-yaw-deg {yaw_deg:.1f}"
    )
    commands.extend(
        [
            treatment_command,
            'python src\\perception\\clear_landing_markers.py --object-regex ".*phase05.*"',
            f"python src\\control\\run_px4_telemetry_check.py --duration {telemetry_duration}",
            "python src\\analysis\\phase05_metrics.py",
            "python src\\analysis\\phase05_formal_report.py",
        ]
    )
    return commands


def _duration_for_height(config: dict[str, Any], height: object) -> float:
    durations = config.get("formal_execution", {}).get("duration_by_initial_height_m", {})
    key = f"{float(height):.1f}"
    return float(durations.get(key, 55))


def parse_args() -> argparse.Namespace:
    config = load_phase05_config()
    execution = config.get("formal_execution", {})
    parser = argparse.ArgumentParser(description="Generate Phase 05 formal run plan and commands.")
    parser.add_argument("--plan-output", type=Path, default=resolve_project_path(execution["run_plan_output"]))
    parser.add_argument("--commands-output", type=Path, default=resolve_project_path(execution["commands_output"]))
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--limit", type=int, default=int(execution.get("recommended_block_size_runs", 8)))
    parser.add_argument("--all-commands", action="store_true")
    return parser.parse_args()


def main() -> None:
    config = load_phase05_config()
    args = parse_args()
    rows = build_run_plan(config)
    plan_path = write_plan_csv(rows, args.plan_output)
    commands_path = write_commands_markdown(
        rows,
        args.commands_output,
        config,
        start_index=max(1, args.start_index),
        limit=None if args.all_commands else max(1, args.limit),
    )
    print(f"Run plan written to: {plan_path}")
    print(f"Command blocks written to: {commands_path}")
    print(f"Total planned runs: {len(rows)}")


if __name__ == "__main__":
    main()
