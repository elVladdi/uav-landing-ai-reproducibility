"""State machine for gradual vision-assisted landing trials."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from src.control.control_config import ControlConfig
from src.control.px4_offboard_control import Px4TelemetrySnapshot
from src.control.visual_servo_controller import BodyVelocityCommand


class LandingPhase(str, Enum):
    ALIGN = "align"
    DESCEND = "descend"
    LAND = "land"
    ABORT = "abort"


@dataclass(frozen=True)
class LandingDecision:
    phase: LandingPhase
    command: BodyVelocityCommand
    should_land: bool
    should_abort: bool
    reason: str


class VisionLandingStateMachine:
    """Conservative state machine: align first, descend only while centered."""

    def __init__(self, config: ControlConfig) -> None:
        self.config = config
        self.phase = LandingPhase.ALIGN
        self.centered_cycles = 0
        self.missing_detections = 0

    def update(
        self,
        telemetry: Px4TelemetrySnapshot,
        visual_command: BodyVelocityCommand,
        elapsed_seconds: float,
    ) -> LandingDecision:
        altitude_m = telemetry.altitude_m

        if elapsed_seconds > self.config.landing.max_trial_seconds:
            return self._abort("max_trial_time_reached")

        if not visual_command.accepted_detection:
            self.missing_detections += 1
            self.centered_cycles = 0
            if self.missing_detections > self.config.visual_servo.max_missing_detections:
                return self._abort("marker_lost")
            return LandingDecision(
                phase=self.phase,
                command=BodyVelocityCommand.hover(reason=visual_command.reason),
                should_land=False,
                should_abort=False,
                reason=visual_command.reason,
            )

        self.missing_detections = 0
        if visual_command.centered:
            self.centered_cycles += 1
        else:
            self.centered_cycles = 0

        if altitude_m is not None and altitude_m <= self.config.landing.landing_complete_altitude_m:
            self.phase = LandingPhase.LAND
            return LandingDecision(
                phase=self.phase,
                command=BodyVelocityCommand.hover(reason="landing_altitude_reached"),
                should_land=True,
                should_abort=False,
                reason="landing_altitude_reached",
            )

        if self.phase == LandingPhase.ALIGN:
            if elapsed_seconds > self.config.landing.align_timeout_seconds:
                return self._abort("align_timeout")
            if self.centered_cycles >= self.config.landing.centered_cycles_required:
                self.phase = LandingPhase.DESCEND
            else:
                return LandingDecision(
                    phase=self.phase,
                    command=replace(visual_command, down_m_s=0.0, reason="align"),
                    should_land=False,
                    should_abort=False,
                    reason="align",
                )

        if self.phase == LandingPhase.DESCEND:
            if not visual_command.centered:
                self.phase = LandingPhase.ALIGN
                return LandingDecision(
                    phase=self.phase,
                    command=replace(visual_command, down_m_s=0.0, reason="re_align"),
                    should_land=False,
                    should_abort=False,
                    reason="re_align",
                )
            return LandingDecision(
                phase=self.phase,
                command=replace(
                    visual_command,
                    down_m_s=self.config.landing.descent_rate_m_s,
                    reason="vision_descent",
                ),
                should_land=False,
                should_abort=False,
                reason="vision_descent",
            )

        return self._abort("invalid_state")

    def _abort(self, reason: str) -> LandingDecision:
        self.phase = LandingPhase.ABORT
        return LandingDecision(
            phase=self.phase,
            command=BodyVelocityCommand.hover(reason=reason),
            should_land=self.config.landing.abort_action == "land",
            should_abort=True,
            reason=reason,
        )
