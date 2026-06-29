"""Cliente básico para conectar Python con AirSim.

Uso desde la raíz del proyecto:
    python src/connection/airsim_client.py

Requisitos:
    1. Abrir Blocks.exe o AirSimNH.exe antes de ejecutar este script.
    2. Tener settings.json en modo Multirotor con VehicleName = Drone1.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Permite importar src/utils/constants.py aunque se ejecute este archivo directamente.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import airsim

from src.utils.constants import VEHICLE_NAME


def connect_multirotor(vehicle_name: str = VEHICLE_NAME) -> airsim.MultirotorClient:
    """Crea y verifica una conexión con AirSim.

    Args:
        vehicle_name: Nombre del vehículo definido en settings.json.

    Returns:
        Cliente AirSim listo para usar.

    Raises:
        RuntimeError: Si no se puede confirmar la conexión.
    """
    client = airsim.MultirotorClient()
    try:
        client.confirmConnection()
        # Esta llamada verifica que el vehículo exista en modo multirrotor.
        client.getMultirotorState(vehicle_name=vehicle_name)
    except Exception as exc:
        raise RuntimeError(
            "No se pudo conectar con AirSim. Verifica que el simulador esté abierto, "
            "que settings.json tenga SimMode='Multirotor' y que el vehículo se llame "
            f"'{vehicle_name}'. Error original: {exc}"
        ) from exc

    return client


def main() -> None:
    client = connect_multirotor()
    state = client.getMultirotorState(vehicle_name=VEHICLE_NAME)
    position = state.kinematics_estimated.position

    print("Conexión correcta con AirSim")
    print(f"Vehículo: {VEHICLE_NAME}")
    print(
        "Posición inicial aproximada: "
        f"x={position.x_val:.3f}, y={position.y_val:.3f}, z={position.z_val:.3f}"
    )


if __name__ == "__main__":
    main()
