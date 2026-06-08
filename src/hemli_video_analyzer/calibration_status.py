"""Calibration completeness checks and claim gating for metadata-only workflows."""

from __future__ import annotations

from typing import Any


def _as_positive_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str) and value.strip():
        try:
            number = float(value.strip())
        except ValueError:
            return None
    else:
        return None
    return number if number > 0 else None


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def assess_calibration_completeness(metadata: dict[str, Any]) -> dict[str, bool]:
    """Return calibration availability flags from metadata fields."""
    spatial_scale_available = _as_positive_float(metadata.get("pixel_size_m")) is not None
    fps_known = _as_positive_float(metadata.get("fps")) is not None
    slow_motion_valid = _as_positive_float(metadata.get("slow_motion_factor")) is not None
    timing_available = fps_known and slow_motion_valid

    fluid_properties_available = (
        _as_positive_float(metadata.get("nu_m2_s")) is not None
        and _as_positive_float(metadata.get("density_kg_m3")) is not None
    )

    known_length_available = (
        _as_positive_float(metadata.get("known_length_m")) is not None
        or _as_positive_float(metadata.get("characteristic_length_m")) is not None
    )
    known_object_available = _has_text(metadata.get("geometry"))
    geometry_available = known_length_available or known_object_available

    return {
        "spatial_scale_available": spatial_scale_available,
        "timing_available": timing_available,
        "fluid_properties_available": fluid_properties_available,
        "geometry_available": geometry_available,
    }


def classify_reporting_status(metadata: dict[str, Any]) -> dict[str, Any]:
    """Classify acceptance level, allowed claims, and report snippets."""
    checks = assess_calibration_completeness(metadata)
    score = int(sum(25 for ok in checks.values() if ok))

    if score >= 100:
        acceptance_level = "L3"
    elif score >= 75:
        acceptance_level = "L2"
    elif score >= 50:
        acceptance_level = "L1"
    else:
        acceptance_level = "L0"

    can_report_physical_velocity = (
        checks["spatial_scale_available"] and checks["timing_available"]
    )
    can_report_reynolds = can_report_physical_velocity and checks["fluid_properties_available"]
    can_compare_hp = acceptance_level in {"L1", "L2", "L3"}
    can_make_research_grade_claim = acceptance_level == "L3" and can_report_reynolds

    snippets: list[str] = []
    if not checks["spatial_scale_available"]:
        snippets.append(
            "Spatial scale missing: velocities and length scales are pixel-based."
        )
    if not checks["timing_available"]:
        snippets.append("Timing calibration missing or inherited from video metadata.")
    if _as_positive_float(metadata.get("nu_m2_s")) is None:
        snippets.append(
            "Reynolds number is not reported because fluid viscosity is missing."
        )

    return {
        **checks,
        "quality_score_0_100": score,
        "acceptance_level": acceptance_level,
        "allowed_claims": {
            "can_compare_hp": can_compare_hp,
            "can_report_physical_velocity": can_report_physical_velocity,
            "can_report_reynolds": can_report_reynolds,
            "can_make_research_grade_claim": can_make_research_grade_claim,
        },
        "report_snippets": snippets,
    }
