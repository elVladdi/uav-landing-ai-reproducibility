"""Registro mínimo de estado del UAV en AirSim.

Uso desde la raíz del proyecto:
    python src/logging/run_logger.py

Genera un CSV en data/logs/ con lecturas de posición, orientación y velocidad.
"""
from __future__ import annotations

import csv
import sys
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.connection.airsim_client import connect_multirotor
from src.utils.constants import LOGS_DIR, VEHICLE_NAME


def read_state_row(client, run_id: str, sample_idx: int) -> dict[str, object]:
    state = client.getMultirotorState(vehicle_name=VEHICLE_NAME)
    kin = state.kinematics_estimated
    pos = kin.position
    ori = kin.orientation
    vel = kin.linear_velocity

    return {
        "run_id": run_id,
        "sample_idx": sample_idx,
        "timestamp": datetime.now().isoformat(timespec="milliseconds"),
        "vehicle_name": VEHICLE_NAME,
        "position_x": pos.x_val,
        "position_y": pos.y_val,
        "position_z": pos.z_val,
        "orientation_w": ori.w_val,
        "orientation_x": ori.x_val,
        "orientation_y": ori.y_val,
        "orientation_z": ori.z_val,
        "velocity_x": vel.x_val,
        "velocity_y": vel.y_val,
        "velocity_z": vel.z_val,
        "landed_state": str(state.landed_state),
    }


def log_state_samples(duration_seconds: float = 5.0, sample_interval_seconds: float = 0.5) -> Path:
    client = connect_multirotor(vehicle_name=VEHICLE_NAME)
    run_id = f"phase02_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = LOGS_DIR / f"{run_id}_state_log.csv"

    fieldnames = [
        "run_id",
        "sample_idx",
        "timestamp",
        "vehicle_name",
        "position_x",
        "position_y",
        "position_z",
        "orientation_w",
        "orientation_x",
        "orientation_y",
        "orientation_z",
        "velocity_x",
        "velocity_y",
        "velocity_z",
        "landed_state",
    ]

    print(f"Registrando estado durante {duration_seconds:.1f} s...")
    start = time.time()
    sample_idx = 0

    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while time.time() - start <= duration_seconds:
            row = read_state_row(client, run_id, sample_idx)
            writer.writerow(row)
            print(
                f"[{sample_idx}] "
                f"x={row['position_x']:.3f}, y={row['position_y']:.3f}, z={row['position_z']:.3f}"
            )
            sample_idx += 1
            time.sleep(sample_interval_seconds)

    print(f"Log guardado: {output_path}")
    return output_path


def main() -> None:
    log_state_samples()


if __name__ == "__main__":
    main()
