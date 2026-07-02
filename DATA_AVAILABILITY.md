# Data Availability Statement

The curated data and derived tables required to reproduce the reported analytical results are included in this public branch.

Curated datasets and derived CSV files included in this repository are released under the Creative Commons Attribution 4.0 International License (CC BY 4.0), unless a specific file states otherwise. Code, scripts and software utilities are released under the MIT License. See `LICENSES.md`.

## Included in Git

- `data/curated/phase05/phase05_run_summary.csv`
- `data/logs/phase05_experiments/summary/phase05_run_summary.csv`
- `outputs/tables/phase05_experiments/`
- `outputs/tables/phase06_analysis/`
- `configs/phase05_experiment_config.json`

## Not included in Git

The full raw simulator/control/perception logs, screenshots, videos, temporary diagnostic artifacts and local virtual environments are not included because they are heavy, machine-specific or not required for analytical reproduction.

The public manifest in `data/raw_manifest/` records expected raw-log references derived from the curated summary. If the raw archive is later deposited in Zenodo, Figshare, OSF or another repository, add the DOI and archive checksum in `data/raw_manifest/raw_logs_availability.md`.

## Recommended article wording

The curated dataset, configuration snapshot and scripts required to reproduce the reported tables and statistical analyses are available in the public repository. Full raw execution logs are not stored in Git due to size and simulator-specific artifacts; their inventory and availability notes are provided in the repository manifest.

The curated datasets and derived tables are released under CC BY 4.0, while code and reproducibility scripts are released under the MIT License.
