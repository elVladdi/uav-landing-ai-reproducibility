# AirSimNH–PX4 Reproducibility Package for Vision-Assisted UAV Landing Evaluation

[Spanish version](README.es.md)

This repository contains the public reproducibility package for a simulation-based UAV landing study. The study evaluates whether an external vision-assisted Offboard layer changes autonomous landing performance over a marked platform in an AirSimNH–PX4 SITL workflow.

The repository is intended to support analytical reproducibility of the reported results from curated CSV files, configuration snapshots, analysis scripts, derived tables, and verification utilities. It is not presented as a real-flight validation package.

For exact reproduction of the published analytical tables, use Python 3.10 with the dependencies in `requirements.txt`, including `scipy`. If `scipy` is unavailable, the hypothesis-test script can still run with documented standard-library fallbacks, but those fallback outputs should be treated as approximate and should not replace the reported thesis/article statistics.

## Study overview

The experiment compares two matched landing treatments:

| Treatment | Description | Active visual lateral correction |
|---|---|---|
| `T0` | Baseline autonomous descent over the marked platform. ArUco perception may be logged, but visual error is not used for lateral control. | No |
| `T1` | Vision-assisted descent using an ArUco-marked platform, image-space error, and bounded Offboard lateral corrections sent through MAVLink/PX4. | Yes |

The formal design uses eight simulated scenarios defined by initial altitude, lateral offset, and yaw. Each scenario contains ten matched `T0/T1` repetitions, producing 160 accepted formal runs and 80 paired comparisons.

## Main findings

| Outcome | `T0` | `T1` | Interpretation |
|---|---:|---:|---|
| Mean terminal landing error | `0.5831 m` | `0.0206 m` | `T1` substantially reduced terminal error. |
| Mean landing-loop time | `20.6399 s` | `28.8897 s` | `T1` required a longer controlled landing loop. |
| Accepted-detection rate | `0.6889` | `0.9978` | `T1` showed higher simulated detection availability. |
| Protocol-level simulated success | `80/80` | `80/80` | Binary success did not discriminate between treatments. |

The result should be interpreted as a precision–time–correction trade-off: the vision-assisted treatment reduced terminal error while increasing landing-loop time and corrective activity. It does not establish global superiority of `T1`, real-flight validity, operational readiness, or sim-to-real transfer.

## What this repository supports

| Reproducibility level | Status | Scope |
|---|---|---|
| Exact analytical reproduction | Supported with full dependencies | Rebuild curated tables, Phase 06 statistical outputs, and publication-oriented analysis artifacts from versioned CSV inputs using the scientific Python stack in `requirements.txt`. |
| Lightweight analytical check | Supported | Verify package completeness, dataset consistency, and expected audit checks without rerunning the simulator. |
| Experimental rerun | Documented | Requires a local AirSimNH-PX4 SITL setup, simulator configuration, PX4 environment, and machine-specific runtime settings. |
| Raw-log audit | Limited | Full raw simulator/control/perception logs, videos, screenshots, temporary diagnostic artifacts, and local virtual environments are not stored in Git. Availability is documented through the manifest. |

## Repository structure

```text
uav-landing-ai-reproducibility/
|-- .github/workflows/                 # Public repository checks, if enabled
|-- configs/                           # Experiment, perception, control, and environment templates
|-- data/                              # Curated data and raw-log manifest references
|-- docs/                              # Methodology, environment notes, traceability, and article-support documentation
|-- outputs/                           # Versioned derived outputs and analysis tables
|-- reproducibility_manifest/          # Reproducibility inventory, checksums, and expected outputs
|-- scripts/                           # Reproduction and utility scripts
|-- src/                               # Source code for analysis and verification routines
|   `-- analysis/                      # Phase 06 audit, descriptive, hypothesis, scenario, and incident analyses
|-- tests/                             # Verification utilities and lightweight checks
|-- CITATION.cff                       # Citation metadata
|-- DATA_AVAILABILITY.md               # Data availability statement
|-- LICENSE                            # MIT license
|-- LICENSES.md                        # License scope by artifact type
|-- README.md                          # Main English README
|-- README.es.md                       # Spanish README
|-- REPRODUCIBILITY.md                 # Reproducibility guide
|-- SOFTWARE_ENVIRONMENT.md            # Software and runtime environment notes
`-- requirements.txt                   # Python dependencies
```

## Included artifacts

The public branch includes the lightweight materials required to inspect and reproduce the reported analytical results:

- curated run-level CSV files;
- accepted-run and pairwise-difference tables;
- scenario-treatment summaries;
- configuration snapshots and public templates;
- Phase 06 statistical outputs;
- analysis scripts;
- verification utilities;
- methodological and data-availability documentation.

## Artifacts not stored in Git

The following materials are intentionally excluded from Git because they are heavy, machine-specific, temporary, or not required for analytical reproduction:

- full raw simulator/control/perception logs;
- videos, screenshots, and diagnostic captures;
- local virtual environments;
- local `.env` files;
- machine-specific paths and simulator state;
- temporary diagnostic artifacts.

Their expected inventory and availability notes are documented in the repository manifest. If a raw archive is later deposited in Zenodo, Figshare, OSF, or another repository, the DOI and checksum should be added to the manifest and data-availability files.

## Software requirements

### Analytical reproduction

Recommended analytical environment for exact table reproduction:

- Windows with PowerShell;
- Python 3.10;
- virtual environment `.venv`;
- Python packages listed in `requirements.txt`, especially:
  - `airsim==1.8.1`
  - `numpy`
  - `opencv-contrib-python`
  - `mavsdk`
  - `pymavlink`
  - `python-dotenv`
  - `scipy`
  - `pandas`
  - `matplotlib`

`scipy` is required for exact reproduction of the reported Shapiro-Wilk, paired t-test, and Wilcoxon signed-rank outputs. Without it, `src/analysis/phase06_hypothesis_tests.py` writes clearly labeled fallback results for inspection only.

### Full experimental rerun

A full rerun requires additional local infrastructure:

- AirSimNH;
- PX4 SITL through WSL2;
- MAVLink direct UDP channel on port `14601`;
- simulated vehicle name: `Drone1`;
- downward-facing camera: `bottom_center`;
- ArUco dictionary: `DICT_4X4_50`;
- marker ID: `23`;
- local simulator/autopilot settings derived from the public templates in `configs/`.

Do not commit local `.env` files, machine-specific paths, large generated logs, or virtual environments.

## Installation

From a Windows PowerShell terminal:

```powershell
cd "<REPO_ROOT>"
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

To reuse an existing virtual environment:

```powershell
cd "<REPO_ROOT>"
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Reproduce the analytical results

The recommended one-command analytical reproduction is:

```powershell
.\scripts\reproduce_analysis.ps1
```

A successful verification should report:

```text
Public reproducibility package checks passed.
Checks: 37 | OK: 37 | REVIEW: 0
SciPy available: True
```

If the output reports `SciPy available: False`, install the dependencies from `requirements.txt` and rerun the workflow before using the hypothesis-test tables as article or thesis evidence.

The same workflow can be executed step by step:

```powershell
cd "<REPO_ROOT>"
.\.venv\Scripts\python.exe scripts\verify_public_package.py
.\.venv\Scripts\python.exe src\analysis\phase06_dataset_audit.py
.\.venv\Scripts\python.exe src\analysis\phase06_descriptive_statistics.py
.\.venv\Scripts\python.exe src\analysis\phase06_hypothesis_tests.py
.\.venv\Scripts\python.exe src\analysis\phase06_scenario_analysis.py
.\.venv\Scripts\python.exe src\analysis\phase06_incident_analysis.py
.\.venv\Scripts\python.exe scripts\generate_checksums.py --check
```

Expected analytical outputs include:

- dataset audit summaries;
- descriptive statistics by treatment;
- paired hypothesis tests and effect summaries;
- scenario-level summaries;
- incident and boundary-case summaries;
- publication-oriented derived tables.

## Verification checklist

Before using this repository as a public reproducibility artifact, run:

```powershell
.\.venv\Scripts\python.exe scripts\verify_public_package.py
.\.venv\Scripts\python.exe scripts\generate_checksums.py --check
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\scripts\reproduce_analysis.ps1
```

Expected results:

```text
Public reproducibility package checks passed.
Checksum file is current.
Ran 6 tests ... OK
Checks: 37 | OK: 37 | REVIEW: 0
SciPy available: True
```

## Reproduction map

| Input or source | Script | Main outputs |
|---|---|---|
| `data/curated/phase05/phase05_run_summary.csv` | `src/analysis/phase05_metrics.py` | Accepted-run, pairwise-difference, and scenario-treatment Phase 05 tables. |
| `outputs/tables/phase05_experiments/phase05_accepted_runs.csv` | `src/analysis/phase06_dataset_audit.py` | Dataset audit CSV and Markdown report with 37 consistency checks. |
| `outputs/tables/phase05_experiments/phase05_accepted_runs.csv` | `src/analysis/phase06_descriptive_statistics.py` | Treatment, scenario, pairwise, and success summaries. |
| `outputs/tables/phase05_experiments/phase05_pairwise_differences.csv` | `src/analysis/phase06_hypothesis_tests.py` | Hypothesis-test tables, effect sizes, and categorical success test. |
| Phase 05 accepted-run and pairwise tables | `src/analysis/phase06_scenario_analysis.py` | Scenario-level rankings and factor summaries. |
| Phase 05 accepted-run table | `src/analysis/phase06_incident_analysis.py` | Incident, boundary-case, and terminal-state summaries. |
| Public reproducibility files | `scripts/generate_checksums.py --check` | SHA256 integrity check against `reproducibility_manifest/files.sha256`. |

## Core analytical inputs

The analytical reproduction workflow depends on the curated and derived CSV files versioned in the public branch, including:

```text
data/curated/phase05/phase05_run_summary.csv
data/logs/phase05_experiments/summary/phase05_run_summary.csv
outputs/tables/phase05_experiments/phase05_accepted_runs.csv
outputs/tables/phase05_experiments/phase05_pairwise_differences.csv
outputs/tables/phase05_experiments/phase05_scenario_treatment_summary.csv
outputs/tables/phase05_experiments/phase05_formal_report.md
outputs/tables/phase06_analysis/
```

## Interpretation boundaries

Use the results with the following scope restrictions:

1. The evidence applies to the controlled AirSimNH–PX4 SITL scenarios `S01`–`S08`.
2. The comparison applies to the implemented `T0/T1` treatments and accepted formal runs.
3. The terminal condition is a simulated protocol-level terminal transition, not physical touchdown validation.
4. The workflow does not validate real flight, physical contact dynamics, outdoor deployment, wind robustness, lighting robustness, other drones, other cameras, unprepared landing zones, or a universal control law.
5. Binary success was saturated in both treatments; therefore, terminal precision, time, detection availability, and corrective activity must be interpreted jointly.

## Methodological contribution

The repository supports the study’s central methodological contribution: a paired, traceable, and reproducible workflow for evaluating how an Offboard visual-assistance layer modifies simulated UAV landing performance under matched scenario conditions.

The contribution is not:

- a new fiducial marker;
- a new PX4 controller;
- a universal landing law;
- a real-flight validation package;
- a full sim-to-real benchmark.

## Citation

If you use this repository, cite the reproducibility package and the associated manuscript when available.

```text
Molleapasa Gutierrez, V. UAV Landing AI Reproducibility Package. Public reproducibility package for an AirSimNH–PX4 SITL experiment comparing baseline autonomous descent and ArUco-based Offboard visual assistance for simulated UAV landing evaluation.
```

For machine-readable citation metadata, see `CITATION.cff`.

## License

This repository uses licenses by artifact type. See `LICENSES.md` for the full scope statement.

| Artifact type | License |
|---|---|
| Code, scripts, tests, configuration templates, and reproducibility utilities | MIT License; see `LICENSE`. |
| Documentation, Markdown reports, methodology notes, article-support text, and explanatory tables | Creative Commons Attribution 4.0 International License (CC BY 4.0). |
| Curated datasets and derived CSV files included for analytical reproducibility | CC BY 4.0, unless a specific file states otherwise. |
| Third-party software, simulators, libraries, and dependencies | Their respective licenses. |

The MIT license applies primarily to software artifacts. The CC BY 4.0 scope is used for academic documentation, curated data, and derived tables so they can be reused with attribution in thesis, article, and reproducibility contexts.

## Contact

Author: Vladimir Molleapasa Gutierrez  
Research topic: reproducible AirSimNH–PX4 workflow for vision-assisted autonomous UAV landing evaluation  
Repository: `https://github.com/elVladdi/uav-landing-ai-reproducibility`
