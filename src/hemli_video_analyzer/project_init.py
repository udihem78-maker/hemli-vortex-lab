"""Project initialization CLI for Hemli Vortex Lab.

Creates the standardized research project folder tree and empty registry CSVs.
This module does not download or process videos.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

PROJECT_FOLDERS = [
    "00_admin",
    "01_sources",
    "02_experiments",
    "03_processed_results",
    "04_combined_database",
    "05_reports",
    "06_figures_for_papers",
    "07_code",
    "08_archive",
]

REGISTRY_SCHEMAS = {
        "local_video_file",
        "date_accessed",
        "rights_status",
        "medium",
        "geometry",
        "fps_known",
        "scale_known",
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
        "source_url",
        "title",
        "institution_or_channel",
        "source_type",
        "phenomenon",
        "downloaded",
        "local_file",
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
        "U0_m_s",
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


def write_csv_if_missing(path: Path, headers: list[str]) -> None:
    """Create a CSV file with headers if it does not already exist."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)


def init_project(project_root: Path) -> list[Path]:
    """Create the standard project tree and registry files.

    Existing folders and registry files are preserved.
    Returns the list of created/verified paths.
    """
    project_root = project_root.expanduser().resolve()
    created_or_verified: list[Path] = []

    for folder in PROJECT_FOLDERS:
        path = project_root / folder
        path.mkdir(parents=True, exist_ok=True)
        created_or_verified.append(path)

    database_dir = project_root / "04_combined_database"
    for filename, headers in REGISTRY_SCHEMAS.items():
        path = database_dir / filename
        write_csv_if_missing(path, headers)
        created_or_verified.append(path)

    return created_or_verified


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize a standardized Hemli Vortex Lab project tree."
    )
    parser.add_argument("project_root", help="Root folder for the research project")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paths = init_project(Path(args.project_root))
    print("Hemli project initialized/verified:")
    for path in paths:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
