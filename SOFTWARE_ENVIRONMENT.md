# Software Environment

## Analytical environment

- Python: 3.10 recommended.
- Operating system used during the original experiment: Windows with PowerShell.
- Main Python packages: `numpy`, `pandas`, `scipy`, `matplotlib`, `opencv-contrib-python`, `pymavlink`, `mavsdk`, `airsim`, `python-dotenv`.

Install:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Experimental environment

The full experimental rerun requires AirSimNH, PX4 SITL through WSL2, MAVLink direct UDP channel on port `14601`, vehicle name `Drone1`, bottom camera `bottom_center`, and ArUco `DICT_4X4_50` marker id `23`.

Use `configs/px4_airsim.env.example` and `configs/airsim_px4_settings.example.json` as public templates. Do not commit local `.env` files or machine-specific paths.
