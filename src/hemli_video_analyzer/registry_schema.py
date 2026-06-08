"""Shared registry schemas for Hemli Vortex Lab experiment management."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


EXPERIMENTS_FOLDER = "02_experiments"
DATABASE_FOLDER = "04_combined_database"

REQUIRED_TOP_LEVEL_FOLDERS = [
    "00_admin",
    "01_sources",
    EXPERIMENTS_FOLDER,
    "03_processed_results",
    DATABASE_FOLDER,
    "05_reports",
    "06_figures_for_papers",
    "07_code",
    "08_archive",
]

REGISTRY_SCHEMAS: Dict[str, List[str]] = {
    "experiments_registry.csv": [
        "experiment_id",
        "title",
        "phenomenon",
        "source_type",
        "source_url",
        "local_video_file",
        "institution_or_channel",
        "date_accessed",
        "rights_status",
        "medium",
        "geometry",
        "fps",
        "known_length_m",
        "known_length_pixels",
        "pixel_size_m",
        "nu_m2_s",
        "quality_score",
        "acceptance_level",
        "HE",
        "HO",
        "HS",
        "HP",
        "fractal_D",
        "rot_dom",
        "Re",
        "Ro",
        "Fr",
        "Ma",
        "analysis_status",
        "notes",
    ],
    "source_registry.csv": [
        "source_id",
        "experiment_id",
        "source_url",
        "local_video_file",
        "title",
        "institution_or_channel",
        "source_type",
        "phenomenon",
        "downloaded",
        "rights_status",
        "metadata_quality",
        "recommended_use",
        "notes",
    ],
    "calibration_registry.csv": [
        "experiment_id",
        "known_length_type",
        "known_length_m",
        "known_length_pixels",
        "pixel_size_m",
        "fps",
        "slow_motion_factor",
        "nu_m2_s",
        "density_kg_m3",
        "calibration_level",
        "uncertainty_level",
        "notes",
    ],
    "quality_scores.csv": [
        "experiment_id",
        "resolution_score",
        "camera_stability_score",
        "contrast_score",
        "fps_score",
        "spatial_calibration_score",
        "fluid_properties_score",
        "geometry_score",
        "frames_score",
        "source_reliability_score",
        "total_score",
        "acceptance_level",
    ],
    "combined_hemli_summary.csv": [
        "experiment_id",
        "video_id",
        "HE_energy_result",
        "HO_order",
        "HS_stability",
        "HP_overall",
        "O_spec",
        "O_frac",
        "fractal_D",
        "rot_dom",
        "gentle_grad",
        "Re",
        "Ro",
        "Fr",
        "Ma",
        "notes",
    ],
}

REQUIRED_REGISTRY_FILES = list(REGISTRY_SCHEMAS)


def database_dir(project_root: Path) -> Path:
    return project_root / DATABASE_FOLDER


def registry_path(project_root: Path, filename: str) -> Path:
    return database_dir(project_root) / filename
