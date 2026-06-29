"""PX4/MAVSDK helpers for Phase 04 Offboard control."""
from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, AsyncIterator

from mavsdk import System
from mavsdk.action import ActionError
from mavsdk.offboard import (
    OffboardError,
    PositionNedYaw,
    VelocityBodyYawspeed,
    VelocityNedYaw,
)

from src.connection.px4_client import Px4ConnectionSettings, connect_px4
from src.control.control_config import ControlConfig
from src.control.visual_servo_controller import BodyVelocityCommand


@dataclass(frozen=True)
class Px4TelemetrySnapshot:
    timestamp: str
    armed: bool | None
    flight_mode: str
    health_global_position_ok: bool | None
    health_home_position_ok: bool | None
    health_local_position_ok: bool | None
    north_m: float | None
    east_m: float | None
    down_m: float | None
    velocity_north_m_s: float | None
    velocity_east_m_s: float | None
    velocity_down_m_s: float | None

    @property
    def altitude_m(self) -> float | None:
        if self.down_m is None:
            return None
        return max(0.0, -float(self.down_m))

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["altitude_m"] = self.altitude_m
        return row


class Px4OffboardClient:
    """Small operational wrapper around MAVSDK for safe Phase 04 scripts."""

    def __init__(self, drone: System, config: ControlConfig) -> None:
        self.drone = drone
        self.config = config

    @classmethod
    async def connect(cls, config: ControlConfig) -> "Px4OffboardClient":
        settings = Px4ConnectionSettings.from_environment()
        settings = Px4ConnectionSettings(
            system_address=settings.system_address,
            timeout_seconds=config.px4.connection_timeout_seconds,
        )
        drone = await connect_px4(settings)
        return cls(drone, config)

    async def telemetry_snapshot(self) -> Px4TelemetrySnapshot:
        timeout = self.config.px4.telemetry_timeout_seconds
        health = await _first_or_none(self.drone.telemetry.health(), timeout)
        armed = await _first_or_none(self.drone.telemetry.armed(), timeout)
        flight_mode = await _first_or_none(self.drone.telemetry.flight_mode(), timeout)
        position_velocity = await _first_or_none(
            self.drone.telemetry.position_velocity_ned(),
            timeout,
        )

        position = getattr(position_velocity, "position", None)
        velocity = getattr(position_velocity, "velocity", None)

        return Px4TelemetrySnapshot(
            timestamp=datetime.now().isoformat(timespec="milliseconds"),
            armed=armed,
            flight_mode=str(flight_mode) if flight_mode is not None else "",
            health_global_position_ok=getattr(health, "is_global_position_ok", None),
            health_home_position_ok=getattr(health, "is_home_position_ok", None),
            health_local_position_ok=getattr(health, "is_local_position_ok", None),
            north_m=getattr(position, "north_m", None),
            east_m=getattr(position, "east_m", None),
            down_m=getattr(position, "down_m", None),
            velocity_north_m_s=getattr(velocity, "north_m_s", None),
            velocity_east_m_s=getattr(velocity, "east_m_s", None),
            velocity_down_m_s=getattr(velocity, "down_m_s", None),
        )

    async def wait_until_ready(self) -> Px4TelemetrySnapshot:
        snapshot = await self.telemetry_snapshot()
        if (
            self.config.px4.require_local_position
            and snapshot.health_local_position_ok is not True
        ):
            raise RuntimeError(
                "PX4 local position is not OK. Do not start Offboard until "
                "health_local_position_ok=True."
            )
        return snapshot

    async def arm_and_takeoff(self, altitude_m: float | None = None) -> None:
        altitude = altitude_m or self.config.offboard.takeoff_altitude_m
        await self.prepare_for_arm()
        await self.drone.action.set_takeoff_altitude(float(altitude))
        await self.drone.action.arm()
        await self.drone.action.takeoff()
        await self.wait_until_takeoff_altitude(float(altitude))
        await asyncio.sleep(self.config.offboard.hover_seconds_after_takeoff)

    async def prepare_for_arm(self) -> None:
        """Recover from stale disarmed modes before arming again."""
        snapshot = await self.telemetry_snapshot()
        if (
            snapshot.flight_mode in {"LAND", "OFFBOARD"}
            and snapshot.armed is False
            and (snapshot.altitude_m or 0.0) <= 0.30
        ):
            try:
                await self.drone.action.hold()
                await asyncio.sleep(1.0)
            except ActionError as exc:
                raise RuntimeError(
                    "PX4 is disarmed on the ground but still in "
                    f"{snapshot.flight_mode} mode, and "
                    "the HOLD recovery command was denied. Restart PX4/AirSimNH "
                    "or run run_mavlink_mode_recovery.py before arming again."
                ) from exc

    async def wait_until_takeoff_altitude(
        self,
        altitude_m: float,
        timeout_seconds: float = 30.0,
    ) -> Px4TelemetrySnapshot:
        """Wait until PX4 reports enough local altitude after takeoff."""
        timeout = max(timeout_seconds, self.config.offboard.takeoff_timeout_seconds)
        target_altitude = max(
            self.config.offboard.takeoff_min_acceptance_altitude_m,
            altitude_m * self.config.offboard.takeoff_acceptance_ratio,
        )
        start = asyncio.get_event_loop().time()
        last_snapshot = await self.telemetry_snapshot()
        while asyncio.get_event_loop().time() - start <= timeout:
            last_snapshot = await self.telemetry_snapshot()
            if (last_snapshot.altitude_m or 0.0) >= target_altitude:
                return last_snapshot
            await asyncio.sleep(0.5)
        raise RuntimeError(
            "Takeoff altitude timeout: "
            f"target>={target_altitude:.2f} m, "
            f"last_altitude={last_snapshot.altitude_m}"
        )

    async def start_offboard(self) -> None:
        await self.prime_offboard_setpoints()
        await self.drone.offboard.start()

    async def prime_offboard_setpoints(self) -> None:
        """Send neutral setpoints before Offboard start.

        Some PX4/MAVSDK combinations reject Offboard start unless the first
        registered setpoint is a local NED setpoint. The pilot tests prime with
        current-position plus zero-velocity NED setpoints, and only switch to
        body-frame velocity commands after Offboard starts.
        """
        period = self.config.offboard.control_period_seconds
        duration = max(self.config.offboard.preflight_setpoint_seconds, period)
        repeats = max(3, int(duration / period))
        snapshot = await self.telemetry_snapshot()
        if snapshot.north_m is None or snapshot.east_m is None or snapshot.down_m is None:
            raise RuntimeError("Cannot prime Offboard: missing local NED position.")
        position_setpoint = PositionNedYaw(
            float(snapshot.north_m),
            float(snapshot.east_m),
            float(snapshot.down_m),
            0.0,
        )
        velocity_setpoint = VelocityNedYaw(0.0, 0.0, 0.0, 0.0)
        for _ in range(repeats):
            await self.drone.offboard.set_position_velocity_ned(
                position_setpoint,
                velocity_setpoint,
            )
            await asyncio.sleep(period)

    async def set_body_velocity(self, command: BodyVelocityCommand) -> None:
        await self.drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(
                command.forward_m_s,
                command.right_m_s,
                command.down_m_s,
                command.yawspeed_deg_s,
            )
        )

    async def stop_offboard(self) -> None:
        try:
            await self.drone.offboard.stop()
        except OffboardError as exc:
            print(f"Warning: could not stop Offboard cleanly: {exc}")

    async def land(self) -> None:
        await self.drone.action.land()

    async def hold(self) -> None:
        await self.drone.action.hold()

    async def disarm(self) -> None:
        try:
            await self.drone.action.disarm()
        except ActionError as exc:
            print(f"Warning: could not disarm: {exc}")


async def _first_or_none(stream: AsyncIterator[Any], timeout_seconds: float) -> Any:
    async def _read_first() -> Any:
        async for item in stream:
            return item
        return None

    try:
        return await asyncio.wait_for(_read_first(), timeout=timeout_seconds)
    except (asyncio.TimeoutError, TimeoutError):
        return None
