"""Offline Phase 03 validation over stored images."""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2

from src.perception.landing_marker_detector import DetectorConfig, LandingMarkerDetector
from src.utils.constants import LOGS_DIR, PHASE03_PROCESSED_DIR, RAW_DIR


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}


def validate_images(
    input_dir: Path = RAW_DIR,
    environment: str = "mixed",
    scenario_id: str = "P03_offline",
) -> Path:
    run_id = f"phase03_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
    detector = LandingMarkerDetector(DetectorConfig.from_json_for_environment(environment))
    image_paths = sorted(
        path for path in input_dir.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS
    )

    if not image_paths:
        raise RuntimeError(f"No images found in {input_dir}.")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    PHASE03_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_csv = LOGS_DIR / f"{run_id}_perception_validation.csv"

    fieldnames = [
        "run_id",
        "timestamp",
        "phase",
        "environment",
        "scenario_id",
        "image_path",
        "annotated_image_path",
        "detected",
        "method",
        "image_width",
        "image_height",
        "center_x",
        "center_y",
        "error_x_px",
        "error_y_px",
        "error_x_norm",
        "error_y_norm",
        "area_px",
        "area_ratio",
        "confidence",
        "bbox_x",
        "bbox_y",
        "bbox_width",
        "bbox_height",
        "contour_points",
        "notes",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for image_path in image_paths:
            image_bgr = cv2.imread(str(image_path))
            if image_bgr is None:
                print(f"Skipping unreadable image: {image_path}")
                continue

            result = detector.detect(image_bgr)
            annotated = detector.annotate(image_bgr, result)
            annotated_path = PHASE03_PROCESSED_DIR / f"{run_id}_{image_path.stem}_annotated.png"
            cv2.imwrite(str(annotated_path), annotated)

            row = {
                "run_id": run_id,
                "timestamp": datetime.now().isoformat(timespec="milliseconds"),
                "phase": "fase03",
                "environment": environment,
                "scenario_id": scenario_id,
                "image_path": str(image_path),
                "annotated_image_path": str(annotated_path),
                **result.to_dict(),
            }
            writer.writerow(row)
            print(f"{image_path.name}: detected={result.detected}, confidence={result.confidence:.3f}")

    print(f"Validation CSV: {output_csv}")
    return output_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Phase 03 perception over stored images.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=RAW_DIR,
        help="Directory with input images. Default: data/raw",
    )
    parser.add_argument(
        "--environment",
        default="mixed",
        help="Environment label for the validation CSV, for example Blocks or AirSimNH.",
    )
    parser.add_argument(
        "--scenario-id",
        default="P03_offline",
        help="Scenario identifier for traceability.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validate_images(args.input_dir, args.environment, args.scenario_id)


if __name__ == "__main__":
    main()
