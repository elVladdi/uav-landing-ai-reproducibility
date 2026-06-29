# Execution Order

Recommended analytical reproduction order:

1. `python scripts/verify_public_package.py`
2. `python src/analysis/phase06_dataset_audit.py`
3. `python src/analysis/phase06_descriptive_statistics.py`
4. `python src/analysis/phase06_hypothesis_tests.py`
5. `python src/analysis/phase06_scenario_analysis.py`
6. `python src/analysis/phase06_incident_analysis.py`
7. `python scripts/generate_checksums.py`

On Windows PowerShell, use:

```powershell
.\scripts\reproduce_analysis.ps1
```
