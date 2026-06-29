"""Cliente basico MAVSDK para conectar Python con PX4.

Uso desde la raiz del proyecto:
    python src/connection/px4_client.py

Este modulo no reemplaza el cliente de AirSim. Sirve para validar que PX4 esta
disponible y que el agente Python puede leer telemetria del autopiloto.
"""
from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from mavsdk import System


@dataclass(frozen=True)
class Px4ConnectionSettings:
    """Configuracion de conexion MAVSDK/PX4."""

    system_address: str = "udpin://0.0.0.0:14601"
    timeout_seconds: float = 30.0

    @classmethod
    def from_environment(cls) -> "Px4ConnectionSettings":
        load_dotenv(PROJECT_ROOT / "configs" / "px4_airsim.env")
        return cls(
            system_address=os.getenv("PX4_SYSTEM_ADDRESS", cls.system_address),
            timeout_seconds=float(
                os.getenv("PX4_CONNECTION_TIMEOUT_SECONDS", cls.timeout_seconds)
            ),
        )


async def connect_px4(settings: Px4ConnectionSettings | None = None) -> System:
    """Crea una conexion MAVSDK y espera hasta detectar PX4."""
    settings = settings or Px4ConnectionSettings.from_environment()
    drone = System()

    print(f"Conectando con PX4 en {settings.system_address} ...")
    await drone.connect(system_address=settings.system_address)

    async def wait_until_connected() -> None:
        async for state in drone.core.connection_state():
            if state.is_connected:
                return

    await asyncio.wait_for(wait_until_connected(), timeout=settings.timeout_seconds)
    return drone


async def print_px4_status() -> None:
    """Imprime una lectura minima de salud, armado y posicion local."""
    settings = Px4ConnectionSettings.from_environment()
    drone = await connect_px4(settings)

    print("Conexion correcta con PX4")

    async for health in drone.telemetry.health():
        print(
            "Health: "
            f"global_position_ok={health.is_global_position_ok}, "
            f"home_position_ok={health.is_home_position_ok}, "
            f"local_position_ok={health.is_local_position_ok}"
        )
        break

    async for armed in drone.telemetry.armed():
        print(f"Armed: {armed}")
        break

    async for position in drone.telemetry.position_velocity_ned():
        pos = position.position
        vel = position.velocity
        print(
            "NED: "
            f"north={pos.north_m:.3f}, east={pos.east_m:.3f}, down={pos.down_m:.3f}, "
            f"vn={vel.north_m_s:.3f}, ve={vel.east_m_s:.3f}, vd={vel.down_m_s:.3f}"
        )
        break


def main() -> None:
    try:
        asyncio.run(print_px4_status())
    except TimeoutError:
        print("No se detecto PX4 dentro del tiempo configurado.")
        print("Verifica que PX4/AirSim este corriendo y que el puerto MAVLink coincida.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
