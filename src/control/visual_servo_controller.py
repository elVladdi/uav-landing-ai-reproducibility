"""Visual servo helper for Phase 04.

This module turns the Phase 03 image-space detection error into a conservative
body-frame velocity command. The sign mapping is configurable because it must be
confirmed in AirSimNH before closing the loop.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.control.control_config import OffboardConfig, VisualServoConfig
from src.perception.landing_marker_detector import DetectionResult


@dataclass(frozen=True)
class BodyVelocityCommand:
    forward_m_s: float
    right_m_s: float
    down_m_s: float
    yawspeed_deg_s: float = 0.0
    accepted_detection: bool = False
    centered: bool = False
    reason: str = "manual"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def hover(cls, reason: str = "hover") -> "BodyVelocityCommand":
        return cls(
            forward_m_s=0.0,
            right_m_s=0.0,
            down_m_s=0.0,
            yawspeed_deg_s=0.0,
            accepted_detection=False,
            centered=False,
            reason=reason,
        )


class VisualServoController:
    """Maps normalized image error to saturated body-frame velocity."""

    def __init__(
        self,
        visual_config: VisualServoConfig,
        offboard_config: OffboardConfig,
    ) -> None:
        self.visual_config = visual_config
        self.offboard_config = offboard_config

    def command_from_detection(
        self,
        detection: DetectionResult,
        down_m_s: float = 0.0,
    ) -> BodyVelocityCommand:
        if not detection.detected:
            return BodyVelocityCommand.hover(reason="marker_not_detected")

        confidence = float(detection.confidence or 0.0)
        if confidence < self.visual_config.min_confidence:
            return BodyVelocityCommand.hover(
                reason=(
                    "low_confidence:"
                    f"{confidence:.3f}<"
                    f"{self.visual_config.min_confidence:.3f}"
                )
            )

        error_x = float(detection.error_x_norm or 0.0)
        error_y = float(detection.error_y_norm or 0.0)
        command_error_x = _apply_deadband(error_x, self.visual_config.command_deadband_norm)
        command_error_y = _apply_deadband(error_y, self.visual_config.command_deadband_norm)

        right_m_s = (
            self.visual_config.right_error_sign
            * self.visual_config.gain_right_mps_per_norm_error
            * command_error_x
        )
        forward_m_s = (
            self.visual_config.forward_error_sign
            * self.visual_config.gain_forward_mps_per_norm_error
            * command_error_y
        )
        centered = (
            abs(error_x) <= self.visual_config.center_tolerance_norm
            and abs(error_y) <= self.visual_config.center_tolerance_norm
        )

        return BodyVelocityCommand(
            forward_m_s=_clamp(
                forward_m_s,
                -self.offboard_config.max_forward_m_s,
                self.offboard_config.max_forward_m_s,
            ),
            right_m_s=_clamp(
                right_m_s,
                -self.offboard_config.max_right_m_s,
                self.offboard_config.max_right_m_s,
            ),
            down_m_s=_clamp(
                down_m_s,
                -self.offboard_config.max_down_m_s,
                self.offboard_config.max_down_m_s,
            ),
            yawspeed_deg_s=0.0,
            accepted_detection=True,
            centered=centered,
            reason="visual_servo",
        )


def _apply_deadband(value: float, deadband: float) -> float:
    return 0.0 if abs(value) < abs(deadband) else value


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))
