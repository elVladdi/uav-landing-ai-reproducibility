"""Phase 06 dataset audit.

Validates that the Phase 05 experimental dataset is ready for Phase 06
statistical analysis. The script is intentionally conservative: it reports
missing files, incomplete counts, duplicated identifiers, incomplete T0/T1
pairs, scenario coverage, and run status summaries.

Example:
    python src/analysis/phase06_dataset_audit.py
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


EXPECTED_ACCEPTED_RUNS = 160
EXPECTED_PAIRS = 80
EXPECTED_SCENARIOS = [f"S{i:02d}" for i in range(1, 9)]
EXPECTED_REPETITIONS_PER_SCENARIO_TREATMENT = 10
EXPECTED_TREATMENTS = ("T0", "T1")

DEFAULT_ACCEPTED_RUNS_CANDIDATES = (
    "outputs/tables/phase05_experiments/phase05_accepted_runs.csv",
    "outputs/tables/phase05_metrics/accepted_runs.csv",
    "outputs/tables/phase05/accepted_runs.csv",
    "outputs/phase05/accepted_runs.csv",
    "outputs/tables/accepted_runs.csv",
)
DEFAULT_PAIRWISE_CANDIDATES = (
    "outputs/tables/phase05_experiments/phase05_pairwise_differences.csv",
    "outputs/tables/phase05_metrics/pairwise_differences.csv",
    "outputs/tables/phase05/pairwise_differences.csv",
    "outputs/phase05/pairwise_differences.csv",
    "outputs/tables/pairwise_differences.csv",
)
DEFAULT_SCENARIO_CANDIDATES = (
    "outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv",
    "outputs/tables/phase05_metrics/scenario_summary.csv",
    "outputs/tables/phase05/scenario_summary.csv",
    "outputs/phase05/scenario_summary.csv",
    "outputs/tables/scenario_summary.csv",
)
DEFAULT_FORMAL_REPORT_CANDIDATES = (
    "outputs/tables/phase05_experiments/phase05_formal_report.md",
    "outputs/reports/phase05_formal_report.md",
    "outputs/tables/phase05_metrics/formal_report.md",
    "outputs/phase05/formal_report.md",
    "outputs/tables/formal_report.md",
)


@dataclass(frozen=True)
class Check:
    category: str
    check: str
    status: str
    observed: str
    expected: str
    detail: str


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def find_first_existing(root: Path, candidates: Iterable[str]) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.exists():
            return path
    return None


def normalize_key(row: dict[str, str]) -> dict[str, str]:
    return {str(key).strip().lower(): (value or "").strip() for key, value in row.items()}


def pick(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = row.get(name.lower())
        if value:
            return value
    return ""


def canonical_scenario(value: str) -> str:
    match = re.search(r"S(\d{2})", value.upper())
    if match:
        return f"S{match.group(1)}"
    return value.upper()


def status(ok: bool) -> str:
    return "OK" if ok else "REVIEW"


def add_check(
    checks: list[Check],
    category: str,
    check_name: str,
    ok: bool,
    observed: object,
    expected: object,
    detail: str = "",
) -> None:
    checks.append(
        Check(
            category=category,
            check=check_name,
            status=status(ok),
            observed=str(observed),
            expected=str(expected),
            detail=detail,
        )
    )


def audit_required_files(root: Path, paths: dict[str, Path | None], checks: list[Check]) -> None:
    for name, path in paths.items():
        add_check(
            checks,
            "input_files",
            f"{name}_exists",
            path is not None,
            path.relative_to(root).as_posix() if path else "missing",
            "existing file",
        )


def audit_accepted_runs(rows: list[dict[str, str]], checks: list[Check]) -> None:
    normalized = [normalize_key(row) for row in rows]
    add_check(
        checks,
        "accepted_runs",
        "accepted_run_count",
        len(normalized) == EXPECTED_ACCEPTED_RUNS,
        len(normalized),
        EXPECTED_ACCEPTED_RUNS,
    )

    run_ids = [pick(row, "run_id", "run", "id", "corrida_id") for row in normalized]
    nonempty_run_ids = [run_id for run_id in run_ids if run_id]
    duplicate_run_ids = sorted(
        run_id for run_id, count in Counter(nonempty_run_ids).items() if count > 1
    )
    add_check(
        checks,
        "accepted_runs",
        "run_id_uniqueness",
        len(nonempty_run_ids) == len(normalized) and not duplicate_run_ids,
        f"{len(nonempty_run_ids)} non-empty, {len(duplicate_run_ids)} duplicates",
        "all rows with unique run_id",
        "; ".join(duplicate_run_ids[:20]),
    )

    by_scenario_treatment: Counter[tuple[str, str]] = Counter()
    missing_scenario_or_treatment = 0
    for row in normalized:
        scenario = pick(row, "scenario", "scenario_id", "escenario")
        treatment = pick(row, "treatment", "tratamiento")
        if not scenario or not treatment:
            missing_scenario_or_treatment += 1
            continue
        by_scenario_treatment[(canonical_scenario(scenario), treatment.upper())] += 1

    add_check(
        checks,
        "accepted_runs",
        "scenario_treatment_fields",
        missing_scenario_or_treatment == 0,
        missing_scenario_or_treatment,
        0,
        "Rows missing scenario or treatment.",
    )

    for scenario in EXPECTED_SCENARIOS:
        for treatment in EXPECTED_TREATMENTS:
            observed = by_scenario_treatment[(scenario, treatment)]
            add_check(
                checks,
                "accepted_runs",
                f"{scenario}_{treatment}_repetitions",
                observed == EXPECTED_REPETITIONS_PER_SCENARIO_TREATMENT,
                observed,
                EXPECTED_REPETITIONS_PER_SCENARIO_TREATMENT,
            )

    status_values = Counter(
        pick(row, "curation_status", "status", "run_status", "estado").lower()
        for row in normalized
        if pick(row, "curation_status", "status", "run_status", "estado")
    )
    add_check(
        checks,
        "accepted_runs",
        "status_values_documented",
        bool(status_values),
        json.dumps(status_values, ensure_ascii=True, sort_keys=True),
        "status column present when available",
        "Useful for accepted/excluded/superseded traceability.",
    )


def audit_pairwise(rows: list[dict[str, str]], checks: list[Check]) -> None:
    normalized = [normalize_key(row) for row in rows]
    add_check(
        checks,
        "pairwise_differences",
        "pair_count",
        len(normalized) == EXPECTED_PAIRS,
        len(normalized),
        EXPECTED_PAIRS,
    )

    pair_ids = [
        pick(row, "treatment_pair_id", "pair_id", "pair", "id", "par_id")
        for row in normalized
    ]
    nonempty_pair_ids = [pair_id for pair_id in pair_ids if pair_id]
    duplicate_pair_ids = sorted(
        pair_id for pair_id, count in Counter(nonempty_pair_ids).items() if count > 1
    )
    add_check(
        checks,
        "pairwise_differences",
        "pair_id_uniqueness",
        not duplicate_pair_ids,
        f"{len(nonempty_pair_ids)} non-empty, {len(duplicate_pair_ids)} duplicates",
        "unique pair_id when present",
        "; ".join(duplicate_pair_ids[:20]),
    )

    by_scenario: Counter[str] = Counter()
    missing_scenario = 0
    for row in normalized:
        scenario = pick(row, "scenario", "scenario_id", "escenario")
        if not scenario:
            missing_scenario += 1
            continue
        by_scenario[canonical_scenario(scenario)] += 1

    add_check(
        checks,
        "pairwise_differences",
        "pair_scenario_field",
        missing_scenario == 0,
        missing_scenario,
        0,
    )
    for scenario in EXPECTED_SCENARIOS:
        observed = by_scenario[scenario]
        add_check(
            checks,
            "pairwise_differences",
            f"{scenario}_pairs",
            observed == EXPECTED_REPETITIONS_PER_SCENARIO_TREATMENT,
            observed,
            EXPECTED_REPETITIONS_PER_SCENARIO_TREATMENT,
        )

    t0_cols = [key for key in normalized[0].keys() if "t0" in key] if normalized else []
    t1_cols = [key for key in normalized[0].keys() if "t1" in key] if normalized else []
    add_check(
        checks,
        "pairwise_differences",
        "t0_t1_columns_present",
        bool(t0_cols) and bool(t1_cols),
        f"T0={len(t0_cols)}, T1={len(t1_cols)}",
        "columns referencing both T0 and T1",
        f"T0 columns: {', '.join(t0_cols[:8])}; T1 columns: {', '.join(t1_cols[:8])}",
    )


def audit_scenario_summary(rows: list[dict[str, str]], checks: list[Check]) -> None:
    normalized = [normalize_key(row) for row in rows]
    scenarios = {
        canonical_scenario(pick(row, "scenario", "scenario_id", "escenario"))
        for row in normalized
        if pick(row, "scenario", "scenario_id", "escenario")
    }
    missing = [scenario for scenario in EXPECTED_SCENARIOS if scenario not in scenarios]
    add_check(
        checks,
        "scenario_summary",
        "all_scenarios_present",
        not missing,
        ", ".join(sorted(scenarios)) if scenarios else "none",
        ", ".join(EXPECTED_SCENARIOS),
        f"Missing: {', '.join(missing)}" if missing else "",
    )


def write_outputs(checks: list[Check], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "phase06_dataset_audit.csv"
    md_path = output_dir / "phase06_dataset_audit.md"

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["category", "check", "status", "observed", "expected", "detail"],
        )
        writer.writeheader()
        for check in checks:
            writer.writerow(check.__dict__)

    review_count = sum(1 for check in checks if check.status != "OK")
    ok_count = len(checks) - review_count

    lines = [
        "# Phase 06 dataset audit",
        "",
        f"- Total checks: {len(checks)}",
        f"- OK: {ok_count}",
        f"- REVIEW: {review_count}",
        "",
        "| Category | Check | Status | Observed | Expected | Detail |",
        "|---|---|---:|---|---|---|",
    ]
    for check in checks:
        lines.append(
            "| {category} | {check} | {status} | {observed} | {expected} | {detail} |".format(
                category=escape_md(check.category),
                check=escape_md(check.check),
                status=escape_md(check.status),
                observed=escape_md(check.observed),
                expected=escape_md(check.expected),
                detail=escape_md(check.detail),
            )
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path, md_path


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Phase 05 outputs for Phase 06.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root. Defaults to current working directory.",
    )
    parser.add_argument("--accepted-runs", type=Path, default=None)
    parser.add_argument("--pairwise-differences", type=Path, default=None)
    parser.add_argument("--scenario-summary", type=Path, default=None)
    parser.add_argument("--formal-report", type=Path, default=None)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/tables/phase06_analysis"),
        help="Directory for audit outputs.",
    )
    return parser.parse_args()


def resolve_optional(root: Path, explicit: Path | None, candidates: Iterable[str]) -> Path | None:
    if explicit:
        return explicit if explicit.is_absolute() else root / explicit
    return find_first_existing(root, candidates)


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir

    paths = {
        "accepted_runs": resolve_optional(
            root, args.accepted_runs, DEFAULT_ACCEPTED_RUNS_CANDIDATES
        ),
        "pairwise_differences": resolve_optional(
            root, args.pairwise_differences, DEFAULT_PAIRWISE_CANDIDATES
        ),
        "scenario_summary": resolve_optional(
            root, args.scenario_summary, DEFAULT_SCENARIO_CANDIDATES
        ),
        "formal_report": resolve_optional(
            root, args.formal_report, DEFAULT_FORMAL_REPORT_CANDIDATES
        ),
    }

    checks: list[Check] = []
    audit_required_files(root, paths, checks)

    if paths["accepted_runs"] and paths["accepted_runs"].exists():
        audit_accepted_runs(read_csv_rows(paths["accepted_runs"]), checks)

    if paths["pairwise_differences"] and paths["pairwise_differences"].exists():
        audit_pairwise(read_csv_rows(paths["pairwise_differences"]), checks)

    if paths["scenario_summary"] and paths["scenario_summary"].exists():
        audit_scenario_summary(read_csv_rows(paths["scenario_summary"]), checks)

    csv_path, md_path = write_outputs(checks, output_dir)
    review_count = sum(1 for check in checks if check.status != "OK")

    print(f"Audit CSV: {csv_path}")
    print(f"Audit report: {md_path}")
    print(f"Checks: {len(checks)} | OK: {len(checks) - review_count} | REVIEW: {review_count}")

    return 1 if review_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
