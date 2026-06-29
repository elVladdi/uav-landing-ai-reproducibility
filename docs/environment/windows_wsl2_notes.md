# Windows and WSL2 Notes

The original experimental stack used Windows PowerShell for orchestration and PX4 SITL through WSL2. When repeating the experiment, confirm the WSL2 host IP and MAVLink route before running any formal trial.

Recommended preflight checks:

```powershell
wsl -l -v
python src\control\run_px4_telemetry_check.py --duration 5
python src\perception\diagnose_camera_views.py
```
