"""Prueba básica de comandos de vuelo en AirSim.

Uso desde la raíz del proyecto:
    python src/control/command_test.py

Ejecuta:
    conexión -> habilitar API -> armar -> despegar -> subir a altura definida -> aterrizar.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.connection.airsim_client import connect_multirotor
from src.utils.constants import DEFAULT_ALTITUDE_M, DEFAULT_HOVER_SECONDS, DEFAULT_SPEED_MPS, VEHICLE_NAME


def run_takeoff_land_test() -> None:
    client = connect_multirotor(vehicle_name=VEHICLE_NAME)

    print("Habilitando control por API...")
    client.enableApiControl(True, vehicle_name=VEHICLE_NAME)
    client.armDisarm(True, vehicle_name=VEHICLE_NAME)

    try:
        print("Despegando...")
        client.takeoffAsync(vehicle_name=VEHICLE_NAME).join()

        # En AirSim, z negativo equivale a altura sobre el suelo.
        target_z = -abs(DEFAULT_ALTITUDE_M)
        print(f"Moviendo a altura aproximada de {DEFAULT_ALTITUDE_M:.1f} m...")
        client.moveToPositionAsync(
            0,
            0,
            target_z,
            DEFAULT_SPEED_MPS,
            vehicle_name=VEHICLE_NAME,
        ).join()

        print(f"Manteniendo vuelo por {DEFAULT_HOVER_SECONDS:.1f} segundos...")
        time.sleep(DEFAULT_HOVER_SECONDS)

        state = client.getMultirotorState(vehicle_name=VEHICLE_NAME)
        pos = state.kinematics_estimated.position
        print(f"Posición antes de aterrizar: x={pos.x_val:.3f}, y={pos.y_val:.3f}, z={pos.z_val:.3f}")

        print("Aterrizando...")
        client.landAsync(vehicle_name=VEHICLE_NAME).join()
        print("Aterrizaje completado.")

    finally:
        print("Desarmando y liberando control API...")
        client.armDisarm(False, vehicle_name=VEHICLE_NAME)
        client.enableApiControl(False, vehicle_name=VEHICLE_NAME)


def main() -> None:
    run_takeoff_land_test()


if __name__ == "__main__":
    main()
