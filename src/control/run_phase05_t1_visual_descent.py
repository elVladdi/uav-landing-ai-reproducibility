"""Run the Phase 05 T1 vision-assisted descent using the validated MAVLink path.

This wrapper marks the active visual-servo routine as the formal T1 treatment.
T1 uses ArUco/image-space marker error to command bounded Offboard lateral
velocity setpoints and, when enabled by the shared routine, a conservative
positive-down descent command.

Scope:
    AirSimNH-PX4 SITL simulation only. The terminal event is a protocol-level
    simulated landing transition, not physical touchdown or real-flight proof.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.control.run_mavlink_visual_servo_test import parse_args, run_visual_servo_test


def main() -> None:
    """Attach Phase 05/T1 metadata before dispatching the shared visual descent."""
    args = parse_args()
    args.phase_label = "fase05"
    args.treatment_label = "T1"
    args.run_id_prefix = "phase05"
    if args.scenario_id is None:
        args.scenario_id = "P05_PILOT_T1_VISUAL_DESCENT"
    run_visual_servo_test(args)


if __name__ == "__main__":
    main()
