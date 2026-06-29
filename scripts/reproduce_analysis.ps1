$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { $Python = "python" }
& $Python "scripts\verify_public_package.py"
& $Python "src\analysis\phase06_dataset_audit.py"
& $Python "src\analysis\phase06_descriptive_statistics.py"
& $Python "src\analysis\phase06_hypothesis_tests.py"
& $Python "src\analysis\phase06_scenario_analysis.py"
& $Python "src\analysis\phase06_incident_analysis.py"
& $Python "scripts\generate_checksums.py"
Write-Host "Reproduction complete. Review outputs/tables/phase06_analysis/."
