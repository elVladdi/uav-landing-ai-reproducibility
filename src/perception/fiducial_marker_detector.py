"""Fiducial marker detector for Phase 04.

The first supported fiducial family is ArUco. The detector returns the same
DetectionResult shape used by the HSV detector so the visual-servo controller can
consume either perception backend without changing the control logic.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from src.perception.landing_marker_detector import DetectionResult
from src.utils.constants import PROJECT_ROOT


DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "perception_config.json"


@dataclass(frozen=True)
class FiducialDetectorConfig:
    method: str = "aruco_fiducial"
    family: str = "aruco"
    dictionary_name: str = "DICT_4X4_50"
    marker_id: int = 23
    min_area_px: float = 400.0
    min_confidence: float = 0.50
    corner_refinement: bool = True
    reject_other_ids: bool = True
    preprocess_variants: bool = True
    upscale_factor: float = 1.5

    @classmethod
    def from_json(
        cls,
        config_path: Path = DEFAULT_CONFIG_PATH,
    ) -> "FiducialDetectorConfig":
        with config_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return cls.from_mapping(payload.get("fiducial_detector", {}))

    @classmethod
    def from_json_for_environment(
        cls,
        environment: str,
        config_path: Path = DEFAULT_CONFIG_PATH,
    ) -> "FiducialDetectorConfig":
        with config_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        detector = dict(payload.get("fiducial_detector", {}))
        overrides = payload.get("environment_overrides", {}).get(environment, {})
        detector.update(overrides.get("fiducial_detector", {}))
        return cls.from_mapping(detector)

    @classmethod
    def from_mapping(cls, detector: dict[str, Any]) -> "FiducialDetectorConfig":
        return cls(
            method=str(detector.get("method", cls.method)),
            family=str(detector.get("family", cls.family)),
            dictionary_name=str(detector.get("dictionary_name", cls.dictionary_name)),
            marker_id=int(detector.get("marker_id", cls.marker_id)),
            min_area_px=float(detector.get("min_area_px", cls.min_area_px)),
            min_confidence=float(detector.get("min_confidence", cls.min_confidence)),
            corner_refinement=bool(detector.get("corner_refinement", cls.corner_refinement)),
            reject_other_ids=bool(detector.get("reject_other_ids", cls.reject_other_ids)),
            preprocess_variants=bool(detector.get("preprocess_variants", cls.preprocess_variants)),
            upscale_factor=float(detector.get("upscale_factor", cls.upscale_factor)),
        )


class ArucoFiducialDetector:
    """Detects an ArUco marker and reports its center in image coordinates."""

    def __init__(self, config: FiducialDetectorConfig | None = None) -> None:
        self.config = config or FiducialDetectorConfig.from_json()
        self._aruco = _require_aruco()
        self._dictionary = _get_aruco_dictionary(self._aruco, self.config.dictionary_name)
        self._parameters = _create_detector_parameters(self._aruco, self.config.corner_refinement)

    def detect(self, image_bgr: np.ndarray) -> DetectionResult:
        if image_bgr is None or image_bgr.size == 0:
            raise ValueError("Input image is empty.")

        height, width = image_bgr.shape[:2]
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected_count, variant_name = self._detect_with_variants(gray)

        if ids is None or len(ids) == 0:
            return DetectionResult(
                detected=False,
                method=self.config.method,
                image_width=width,
                image_height=height,
            notes=f"No ArUco marker detected; rejected_candidates={rejected_count}.",
            )

        candidate_index = self._select_candidate(ids)
        if candidate_index is None:
            seen_ids = ",".join(str(int(item[0])) for item in ids)
            return DetectionResult(
                detected=False,
                method=self.config.method,
                image_width=width,
                image_height=height,
                notes=(
                    f"ArUco marker(s) detected but target id={self.config.marker_id} "
                    f"was not present; seen_ids={seen_ids}."
                ),
            )

        marker_id = int(ids[candidate_index][0])
        marker_corners = np.asarray(corners[candidate_index], dtype=np.float32).reshape(4, 2)
        area = float(abs(cv2.contourArea(marker_corners)))
        if area < self.config.min_area_px:
            return DetectionResult(
                detected=False,
                method=self.config.method,
                image_width=width,
                image_height=height,
                area_px=area,
                notes=(
                    f"Rejected ArUco id={marker_id}: area={area:.1f}px "
                    f"< min_area_px={self.config.min_area_px:.1f}."
                ),
            )

        center_x = float(marker_corners[:, 0].mean())
        center_y = float(marker_corners[:, 1].mean())
        image_center_x = width / 2.0
        image_center_y = height / 2.0
        error_x = center_x - image_center_x
        error_y = center_y - image_center_y
        bbox_x, bbox_y, bbox_width, bbox_height = cv2.boundingRect(marker_corners.astype(np.int32))
        image_area = float(width * height)
        area_ratio = area / image_area if image_area else 0.0
        confidence = 1.0
        if confidence < self.config.min_confidence:
            return DetectionResult(
                detected=False,
                method=self.config.method,
                image_width=width,
                image_height=height,
                area_px=area,
                area_ratio=area_ratio,
                confidence=confidence,
                notes=(
                    f"Rejected ArUco id={marker_id}: confidence={confidence:.2f} "
                    f"< min_confidence={self.config.min_confidence:.2f}."
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
            contour_points=4,
            notes=(
                f"aruco_id={marker_id}; dictionary={self.config.dictionary_name}; "
                f"variant={variant_name}; rejected_candidates={rejected_count}; "
                f"area_ratio={area_ratio:.4f}"
            ),
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
                f"aruco id={self.config.marker_id} "
                f"dx={result.error_x_px:.1f}px dy={result.error_y_px:.1f}px "
                f"conf={result.confidence:.2f}"
            )
        else:
            label = "aruco marker not detected"

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

    def _select_candidate(self, ids: np.ndarray) -> int | None:
        if not self.config.reject_other_ids:
            return 0
        for index, marker_id in enumerate(ids.flatten().tolist()):
            if int(marker_id) == self.config.marker_id:
                return index
        return None

    def _detect_with_variants(
        self,
        gray: np.ndarray,
    ) -> tuple[Any, Any, int, str]:
        rejected_total = 0
        for variant_name, variant_gray, scale in self._image_variants(gray):
            corners, ids, rejected = _detect_markers(
                self._aruco,
                variant_gray,
                self._dictionary,
                self._parameters,
            )
            rejected_total += len(rejected) if rejected is not None else 0
            if ids is None or len(ids) == 0:
                continue

            if scale != 1.0:
                corners = [np.asarray(item, dtype=np.float32) / float(scale) for item in corners]
            if self._select_candidate(ids) is not None or not self.config.reject_other_ids:
                return corners, ids, rejected_total, variant_name

        return [], None, rejected_total, "none"

    def _image_variants(self, gray: np.ndarray) -> list[tuple[str, np.ndarray, float]]:
        variants: list[tuple[str, np.ndarray, float]] = [("raw", gray, 1.0)]
        if not self.config.preprocess_variants:
            return variants

        variants.append(("equalized", cv2.equalizeHist(gray), 1.0))
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(("otsu", otsu, 1.0))

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        variants.append(("clahe", clahe.apply(gray), 1.0))

        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        variants.append(("blurred", blurred, 1.0))

        scale = max(1.0, float(self.config.upscale_factor))
        if scale > 1.0:
            upscaled = cv2.resize(
                gray,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC,
            )
            variants.append((f"upscaled_{scale:.2f}", upscaled, scale))
            downscale = 1.0 / scale
            downscaled = cv2.resize(
                gray,
                None,
                fx=downscale,
                fy=downscale,
                interpolation=cv2.INTER_AREA,
            )
            variants.append((f"downscaled_{downscale:.2f}", downscaled, downscale))
        return variants


def render_aruco_marker(
    dictionary_name: str,
    marker_id: int,
    marker_size_px: int,
    border_bits: int = 1,
) -> np.ndarray:
    """Render a square ArUco marker as a grayscale image."""

    aruco = _require_aruco()
    dictionary = _get_aruco_dictionary(aruco, dictionary_name)
    marker_size_px = max(32, int(marker_size_px))
    marker_id = int(marker_id)

    if hasattr(aruco, "generateImageMarker"):
        return aruco.generateImageMarker(
            dictionary,
            marker_id,
            marker_size_px,
            borderBits=int(border_bits),
        )

    marker = np.zeros((marker_size_px, marker_size_px), dtype=np.uint8)
    aruco.drawMarker(dictionary, marker_id, marker_size_px, marker, int(border_bits))
    return marker


def _require_aruco() -> Any:
    aruco = getattr(cv2, "aruco", None)
    if aruco is None:
        raise ImportError(
            "cv2.aruco is not available. Install OpenCV contrib in the active "
            "environment: pip install opencv-contrib-python"
        )
    return aruco


def _get_aruco_dictionary(aruco: Any, dictionary_name: str) -> Any:
    if not hasattr(aruco, dictionary_name):
        available = sorted(name for name in dir(aruco) if name.startswith("DICT_"))
        raise ValueError(
            f"Unknown ArUco dictionary '{dictionary_name}'. "
            f"Available examples: {', '.join(available[:8])}"
        )
    return aruco.getPredefinedDictionary(getattr(aruco, dictionary_name))


def _create_detector_parameters(aruco: Any, corner_refinement: bool) -> Any:
    if hasattr(aruco, "DetectorParameters"):
        parameters = aruco.DetectorParameters()
    else:
        parameters = aruco.DetectorParameters_create()

    _set_if_present(parameters, "adaptiveThreshWinSizeMin", 3)
    _set_if_present(parameters, "adaptiveThreshWinSizeMax", 53)
    _set_if_present(parameters, "adaptiveThreshWinSizeStep", 4)
    _set_if_present(parameters, "minMarkerPerimeterRate", 0.02)
    _set_if_present(parameters, "maxMarkerPerimeterRate", 4.0)
    _set_if_present(parameters, "polygonalApproxAccuracyRate", 0.05)
    _set_if_present(parameters, "minCornerDistanceRate", 0.02)
    _set_if_present(parameters, "minDistanceToBorder", 1)
    _set_if_present(parameters, "errorCorrectionRate", 0.8)

    if corner_refinement and hasattr(parameters, "cornerRefinementMethod"):
        parameters.cornerRefinementMethod = getattr(aruco, "CORNER_REFINE_SUBPIX", 1)
    return parameters


def _set_if_present(target: Any, attribute: str, value: Any) -> None:
    if hasattr(target, attribute):
        setattr(target, attribute, value)


def _detect_markers(
    aruco: Any,
    gray: np.ndarray,
    dictionary: Any,
    parameters: Any,
) -> tuple[Any, Any, Any]:
    if hasattr(aruco, "ArucoDetector"):
        detector = aruco.ArucoDetector(dictionary, parameters)
        return detector.detectMarkers(gray)
    return aruco.detectMarkers(gray, dictionary, parameters=parameters)
