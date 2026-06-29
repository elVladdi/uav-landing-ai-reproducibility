"""Landing marker detector for Phase 03.

The detector is intentionally independent from AirSim. It receives an OpenCV BGR
image, segments a configurable HSV range, selects the strongest contour, and
returns the marker position relative to the image center.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from src.utils.constants import PROJECT_ROOT


DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "perception_config.json"


@dataclass(frozen=True)
class DetectorConfig:
    method: str = "hsv_color_contour"
    hsv_lower: tuple[int, int, int] = (0, 80, 80)
    hsv_upper: tuple[int, int, int] = (15, 255, 255)
    hsv_lower_alt: tuple[int, int, int] = (170, 80, 80)
    hsv_upper_alt: tuple[int, int, int] = (180, 255, 255)
    hsv_ranges: tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...] = ()
    use_alt_range: bool = True
    blur_kernel_size: int = 5
    morph_kernel_size: int = 5
    min_area_px: float = 300.0
    max_area_ratio: float = 0.8
    min_confidence: float = 0.0
    min_circularity: float = 0.0

    @classmethod
    def from_json(cls, config_path: Path = DEFAULT_CONFIG_PATH) -> "DetectorConfig":
        with config_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        detector = payload.get("detector", {})
        return cls.from_mapping(detector)

    @classmethod
    def from_json_for_environment(
        cls,
        environment: str,
        config_path: Path = DEFAULT_CONFIG_PATH,
    ) -> "DetectorConfig":
        with config_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        detector = dict(payload.get("detector", {}))
        overrides = payload.get("environment_overrides", {}).get(environment, {})
        detector.update(overrides)
        return cls.from_mapping(detector)

    @classmethod
    def from_mapping(cls, detector: dict[str, Any]) -> "DetectorConfig":
        hsv_ranges = tuple(
            (
                tuple(item["lower"]),
                tuple(item["upper"]),
            )
            for item in detector.get("hsv_ranges", [])
            if "lower" in item and "upper" in item
        )

        return cls(
            method=str(detector.get("method", cls.method)),
            hsv_lower=tuple(detector.get("hsv_lower", cls.hsv_lower)),
            hsv_upper=tuple(detector.get("hsv_upper", cls.hsv_upper)),
            hsv_lower_alt=tuple(detector.get("hsv_lower_alt", cls.hsv_lower_alt)),
            hsv_upper_alt=tuple(detector.get("hsv_upper_alt", cls.hsv_upper_alt)),
            hsv_ranges=hsv_ranges,
            use_alt_range=bool(detector.get("use_alt_range", cls.use_alt_range)),
            blur_kernel_size=int(detector.get("blur_kernel_size", cls.blur_kernel_size)),
            morph_kernel_size=int(detector.get("morph_kernel_size", cls.morph_kernel_size)),
            min_area_px=float(detector.get("min_area_px", cls.min_area_px)),
            max_area_ratio=float(detector.get("max_area_ratio", cls.max_area_ratio)),
            min_confidence=float(detector.get("min_confidence", cls.min_confidence)),
            min_circularity=float(detector.get("min_circularity", cls.min_circularity)),
        )


@dataclass(frozen=True)
class DetectionResult:
    detected: bool
    method: str
    image_width: int
    image_height: int
    center_x: float | None = None
    center_y: float | None = None
    error_x_px: float | None = None
    error_y_px: float | None = None
    error_x_norm: float | None = None
    error_y_norm: float | None = None
    area_px: float = 0.0
    area_ratio: float = 0.0
    confidence: float = 0.0
    bbox_x: int | None = None
    bbox_y: int | None = None
    bbox_width: int | None = None
    bbox_height: int | None = None
    contour_points: int = 0
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LandingMarkerDetector:
    """Detects a high-contrast landing marker using HSV color segmentation."""

    def __init__(self, config: DetectorConfig | None = None) -> None:
        self.config = config or DetectorConfig.from_json()

    def detect(self, image_bgr: np.ndarray) -> DetectionResult:
        if image_bgr is None or image_bgr.size == 0:
            raise ValueError("Input image is empty.")

        height, width = image_bgr.shape[:2]
        mask = self._build_mask(image_bgr)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        image_area = float(width * height)
        candidates = []
        for contour in contours:
            area = float(cv2.contourArea(contour))
            area_ratio = area / image_area if image_area else 0.0
            if area < self.config.min_area_px or area_ratio > self.config.max_area_ratio:
                continue

            perimeter = float(cv2.arcLength(contour, True))
            circularity = 0.0
            if perimeter > 0:
                circularity = float(4.0 * np.pi * area / (perimeter * perimeter))
            if circularity < self.config.min_circularity:
                continue

            candidates.append((area, contour, circularity))

        if not candidates:
            return DetectionResult(
                detected=False,
                method=self.config.method,
                image_width=width,
                image_height=height,
                notes="No contour matched configured thresholds.",
            )

        area, contour, circularity = max(candidates, key=lambda item: item[0])
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            return DetectionResult(
                detected=False,
                method=self.config.method,
                image_width=width,
                image_height=height,
                area_px=area,
                notes="Largest contour has zero moment.",
            )

        center_x = float(moments["m10"] / moments["m00"])
        center_y = float(moments["m01"] / moments["m00"])
        image_center_x = width / 2.0
        image_center_y = height / 2.0
        error_x = center_x - image_center_x
        error_y = center_y - image_center_y
        bbox_x, bbox_y, bbox_width, bbox_height = cv2.boundingRect(contour)
        area_ratio = area / image_area if image_area else 0.0
        confidence = min(1.0, max(0.0, area_ratio * 20.0))
        if confidence < self.config.min_confidence:
            return DetectionResult(
                detected=False,
                method=self.config.method,
                image_width=width,
                image_height=height,
                area_px=area,
                area_ratio=area_ratio,
                confidence=confidence,
                bbox_x=int(bbox_x),
                bbox_y=int(bbox_y),
                bbox_width=int(bbox_width),
                bbox_height=int(bbox_height),
                contour_points=int(len(contour)),
                notes=(
                    f"Rejected low-confidence contour: "
                    f"confidence={confidence:.3f}, min_confidence={self.config.min_confidence:.3f}"
                ),
            )

        return DetectionResult(
            detected=True,
            method=self.config.method,
            image_width=width,
            image_height=height,
            center_x=center_x,
            center_y=center_y,
            error_x_px=error_x,
            error_y_px=error_y,
            error_x_norm=error_x / image_center_x if image_center_x else 0.0,
            error_y_norm=error_y / image_center_y if image_center_y else 0.0,
            area_px=area,
            area_ratio=area_ratio,
            confidence=confidence,
            bbox_x=int(bbox_x),
            bbox_y=int(bbox_y),
            bbox_width=int(bbox_width),
            bbox_height=int(bbox_height),
            contour_points=int(len(contour)),
            notes=f"circularity={circularity:.3f}",
        )

    def annotate(self, image_bgr: np.ndarray, result: DetectionResult) -> np.ndarray:
        annotated = image_bgr.copy()
        height, width = annotated.shape[:2]
        image_center = (int(width / 2), int(height / 2))

        cv2.drawMarker(
            annotated,
            image_center,
            (255, 0, 0),
            markerType=cv2.MARKER_CROSS,
            markerSize=20,
            thickness=2,
        )

        if result.detected and result.center_x is not None and result.center_y is not None:
            marker_center = (int(result.center_x), int(result.center_y))
            cv2.drawMarker(
                annotated,
                marker_center,
                (0, 255, 0),
                markerType=cv2.MARKER_TILTED_CROSS,
                markerSize=24,
                thickness=2,
            )
            cv2.line(annotated, image_center, marker_center, (0, 255, 255), 2)

            if result.bbox_x is not None and result.bbox_y is not None:
                top_left = (result.bbox_x, result.bbox_y)
                bottom_right = (
                    result.bbox_x + int(result.bbox_width or 0),
                    result.bbox_y + int(result.bbox_height or 0),
                )
                cv2.rectangle(annotated, top_left, bottom_right, (0, 255, 0), 2)

            label = (
                f"dx={result.error_x_px:.1f}px dy={result.error_y_px:.1f}px "
                f"conf={result.confidence:.2f}"
            )
        else:
            label = "marker not detected"

        cv2.putText(
            annotated,
            label,
            (10, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        return annotated

    def _build_mask(self, image_bgr: np.ndarray) -> np.ndarray:
        blur_size = _odd_kernel_size(self.config.blur_kernel_size)
        morph_size = _odd_kernel_size(self.config.morph_kernel_size)

        blurred = cv2.GaussianBlur(image_bgr, (blur_size, blur_size), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        ranges = self.config.hsv_ranges or (
            (self.config.hsv_lower, self.config.hsv_upper),
        )

        for lower_tuple, upper_tuple in ranges:
            lower = np.array(lower_tuple, dtype=np.uint8)
            upper = np.array(upper_tuple, dtype=np.uint8)
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))

        if self.config.use_alt_range and not self.config.hsv_ranges:
            lower_alt = np.array(self.config.hsv_lower_alt, dtype=np.uint8)
            upper_alt = np.array(self.config.hsv_upper_alt, dtype=np.uint8)
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower_alt, upper_alt))

        kernel = np.ones((morph_size, morph_size), dtype=np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        return mask


def _odd_kernel_size(value: int) -> int:
    value = max(1, int(value))
    return value if value % 2 == 1 else value + 1
