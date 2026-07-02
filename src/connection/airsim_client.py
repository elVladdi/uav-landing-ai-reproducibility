"""Basic AirSim connection helper for the simulated UAV workflow.

Usage from the repository root:
    python src/connection/airsim_client.py

Requirements:
    1. Open Blocks.exe or AirSimNH.exe before running this script.
    2. Use AirSim settings configured for Multirotor mode and vehicle `Drone1`.

Scope:
    Diagnostic/helper module only. A successful connection confirms simulator
    availability, not statistical evidence or real-flight validity.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow direct execution from the repository root while preserving package imports.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import airsim

from src.utils.constants import VEHICLE_NAME


def connect_multirotor(vehicle_name: str = VEHICLE_NAME) -> airsim.MultirotorClient:
    """Create and verify an AirSim multirotor connection.

    Args:
        vehicle_name: Vehicle name defined in AirSim settings.

    Returns:
        AirSim client ready for simulator commands.

    Raises:
        RuntimeError: If the simulator or the configured vehicle is unavailable.
    """
    client = airsim.MultirotorClient()
    try:
        client.confirmConnection()
        # This call verifies that the named multirotor exists in the scene.
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
