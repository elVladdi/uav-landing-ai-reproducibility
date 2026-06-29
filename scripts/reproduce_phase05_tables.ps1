$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { $Python = "python" }
if (-not (Test-Path -LiteralPath "data\logs\phase05_experiments\summary\phase05_run_summary.csv")) {
    throw "Missing curated Phase 05 summary."
}
& $Python "src\analysis\phase05_formal_report.py"
Write-Host "Phase 05 formal report refreshed where source summaries are available."
