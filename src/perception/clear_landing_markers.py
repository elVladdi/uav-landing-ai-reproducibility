"""Remove spawned landing markers from the AirSim scene."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.connection.airsim_client import connect_multirotor
from src.utils.constants import VEHICLE_NAME


def clear_markers(object_regex: str, vehicle_name: str = VEHICLE_NAME) -> list[str]:
    client = connect_multirotor(vehicle_name=vehicle_name)
    object_names = client.simListSceneObjects(object_regex)
    destroyed: list[str] = []

    print(f"Objects matching '{object_regex}': {len(object_names)}")
    for object_name in object_names:
        try:
            ok = bool(client.simDestroyObject(object_name))
        except Exception as exc:
            print(f"{object_name}: destroy failed -> {exc}")
            continue

        print(f"{object_name}: destroyed={ok}")
        if ok:
            destroyed.append(object_name)

    return destroyed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove spawned AirSim landing markers.")
    parser.add_argument("--object-regex", default=".*phase0[34].*marker.*")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    destroyed = clear_markers(args.object_regex)
    print(f"Destroyed objects: {len(destroyed)}")


if __name__ == "__main__":
    main()
