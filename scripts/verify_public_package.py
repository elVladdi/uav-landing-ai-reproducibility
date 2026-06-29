from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    "README.md",
    "REPRODUCIBILITY.md",
    "DATA_AVAILABILITY.md",
    "SOFTWARE_ENVIRONMENT.md",
    "CITATION.cff",
    "LICENSE",
    "configs/phase05_experiment_config.json",
    "configs/px4_airsim.env.example",
    "data/curated/phase05/phase05_run_summary.csv",
    "outputs/tables/phase05_experiments/phase05_accepted_runs.csv",
    "outputs/tables/phase05_experiments/phase05_pairwise_differences.csv",
    "outputs/tables/phase06_analysis/phase06_dataset_audit.md",
    "docs/methodology/experimental_design_t0_t1.md",
    "docs/article_support/data_availability_statement.md",
    "reproducibility_manifest/expected_outputs.md",
]
PRIVATE_PATTERNS = [
    re.compile(r"C:\\\\Users\\\\Vladimir", re.IGNORECASE),
    re.compile(r"OneDrive\\\\Documentos\\\\Tesis", re.IGNORECASE),
    re.compile(r"DNI\s*:\s*\d+", re.IGNORECASE),
]
TEXT_SUFFIXES = {".md", ".py", ".ps1", ".yml", ".yaml", ".json", ".txt", ".cff", ".csv", ".env", ".example"}


def git_export_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [ROOT / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def check_required_paths() -> list[str]:
    return [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]


def check_dataset_contract() -> list[str]:
    path = ROOT / "outputs/tables/phase05_experiments/phase05_accepted_runs.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    errors: list[str] = []
    if len(rows) != 160:
        errors.append(f"expected 160 accepted runs, observed {len(rows)}")
    if len({row.get("treatment_pair_id", "") for row in rows}) != 80:
        errors.append("expected 80 treatment pairs")
    if len({row.get("scenario_id", "") for row in rows}) != 8:
        errors.append("expected 8 scenarios")
    return errors


def check_private_paths() -> list[str]:
    offenders: list[str] = []
    for path in git_export_files():
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in PRIVATE_PATTERNS):
            offenders.append(path.relative_to(ROOT).as_posix())
    return sorted(set(offenders))


def main() -> int:
    errors: list[str] = []
    missing = check_required_paths()
    if missing:
        errors.append("missing required paths: " + ", ".join(missing))
    errors.extend(check_dataset_contract())
    private = check_private_paths()
    if private:
        errors.append("private/local references found in: " + ", ".join(private))
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    print("Public reproducibility package checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
