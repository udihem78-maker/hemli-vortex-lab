"""Calibration completeness checks and conservative reporting claims."""

from __future__ import annotations

from typing import Any


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and value > 0


def validate_calibration_metadata(metadata: dict[str, Any]) -> dict[str, bool]:
    """Return completeness flags required for calibrated reporting."""
    has_spatial_scale = _is_positive_number(metadata.get("pixel_size_m"))
    has_timing = _is_positive_number(metadata.get("fps")) and _is_positive_number(
        metadata.get("slow_motion_factor", 1.0)
    )
    has_fluid_properties = _is_positive_number(metadata.get("nu_m2_s")) and _is_positive_number(
        metadata.get("density_kg_m3")
    )
    has_geometry = _is_positive_number(metadata.get("characteristic_length_m")) or _is_positive_number(
        metadata.get("known_length_m")
    )
    return {
        "has_spatial_scale": has_spatial_scale,
        "has_timing": has_timing,
        "has_fluid_properties": has_fluid_properties,
        "has_geometry": has_geometry,
    }


def report_calibration_snippets(metadata: dict[str, Any]) -> list[str]:
    """Return report snippets describing missing calibration requirements."""
    snippets: list[str] = []
    if not _is_positive_number(metadata.get("pixel_size_m")):
        snippets.append("Spatial scale missing: velocities and length scales are pixel-based.")
    if not _is_positive_number(metadata.get("fps")):
        snippets.append("Timing calibration missing or inherited from video metadata.")
    if not _is_positive_number(metadata.get("nu_m2_s")):
        snippets.append("Reynolds number is not reported because fluid viscosity is missing.")
    return snippets


def classify_quality_status(metadata: dict[str, Any]) -> dict[str, Any]:
    """Classify analysis acceptance level and conservative claim permissions."""
    validation = validate_calibration_metadata(metadata)

    quality_score_0_100 = (
        int(validation["has_spatial_scale"]) * 30
        + int(validation["has_timing"]) * 25
        + int(validation["has_fluid_properties"]) * 25
        + int(validation["has_geometry"]) * 20
    )

    if all(validation.values()):
        acceptance_level = "L3"
    elif (
        validation["has_spatial_scale"]
        and validation["has_timing"]
        and validation["has_geometry"]
        and quality_score_0_100 >= 75
    ):
        acceptance_level = "L2"
    elif validation["has_spatial_scale"] or validation["has_timing"]:
        acceptance_level = "L1"
    else:
        acceptance_level = "L0"

    can_report_physical_velocity = validation["has_spatial_scale"] and validation["has_timing"]
    can_report_reynolds = (
        can_report_physical_velocity and validation["has_fluid_properties"] and validation["has_geometry"]
    )

    return {
        "quality_score_0_100": quality_score_0_100,
        "acceptance_level": acceptance_level,
        "allowed_claims": {
            "can_compare_hp": acceptance_level in {"L1", "L2", "L3"},
            "can_report_physical_velocity": can_report_physical_velocity,
            "can_report_reynolds": can_report_reynolds,
            "can_make_research_grade_claim": acceptance_level == "L3",
        },
        "calibration_validation": validation,
        "report_snippets": report_calibration_snippets(metadata),
    }
