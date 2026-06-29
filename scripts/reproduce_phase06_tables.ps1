$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { $Python = "python" }
& $Python "src\analysis\phase06_dataset_audit.py"
& $Python "src\analysis\phase06_descriptive_statistics.py"
& $Python "src\analysis\phase06_hypothesis_tests.py"
& $Python "src\analysis\phase06_scenario_analysis.py"
& $Python "src\analysis\phase06_incident_analysis.py"
Write-Host "Phase 06 analysis outputs refreshed."
