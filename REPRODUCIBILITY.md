# Reproducibility Guide

This public branch reproduces the analytical evidence for the UAV Landing AI experiment without requiring access to the private thesis workspace.

## Reproducibility levels

| Level | Scope | Public branch support |
|---|---|---|
| Analytical reproduction | Rebuild Phase 05 curated tables and Phase 06 statistical outputs from curated CSV files. | Supported directly. |
| Experimental rerun | Re-execute AirSimNH + PX4 SITL + ArUco + MAVLink direct trials. | Documented, requires local simulator/autopilot setup. |
| Raw-log audit | Inspect full raw CSV logs, screenshots, videos or simulator traces. | Not stored in Git; tracked by manifest and availability statement. |

## One-command analytical reproduction

```powershell
.\scripts\reproduce_analysis.ps1
```

Expected key check:

```text
Checks: 37 | OK: 37 | REVIEW: 0
```

## Required analytical inputs

```text
data/curated/phase05/phase05_run_summary.csv
data/logs/phase05_experiments/summary/phase05_run_summary.csv
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv
outputs/tables/phase05_experiments/phase05_formal_report.md
```

## Interpretation boundary

The reported results apply to controlled AirSimNH/PX4 simulation scenarios `S01` to `S08`, treatments `T0` and `T1`, and accepted formal runs. They do not validate real flight, other drones, other cameras, unprepared landing zones, or a universal control law.
