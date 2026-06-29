"""Phase 05 T1 wrapper for the validated MAVLink visual descent path."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.control.run_mavlink_visual_servo_test import parse_args, run_visual_servo_test


def main() -> None:
    args = parse_args()
    args.phase_label = "fase05"
    args.treatment_label = "T1"
    args.run_id_prefix = "phase05"
    if args.scenario_id is None:
        args.scenario_id = "P05_PILOT_T1_VISUAL_DESCENT"
    run_visual_servo_test(args)


if __name__ == "__main__":
    main()
