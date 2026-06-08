"""Create the standard Hemli Vortex Lab project structure."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Union


PROJECT_FOLDERS: Tuple[str, ...] = (
    "00_admin",
    "01_sources",
    "02_experiments",
    "03_processed_results",
    "04_combined_database",
    "05_reports",
    "06_figures_for_papers",
    "07_code",
    "08_archive",
)

REGISTRY_FILES: Tuple[str, ...] = (
    "experiments_registry.csv",
    "source_registry.csv",
    "calibration_registry.csv",
    "quality_scores.csv",
    "combined_hemli_summary.csv",
)


def ensure_directories(project_root: Path, folders: Iterable[str]) -> List[Path]:
    """Create expected directories and return their paths."""
    created_paths: List[Path] = []
    for folder in folders:
        path = project_root / folder
        path.mkdir(parents=True, exist_ok=True)
        created_paths.append(path)
    return created_paths


def ensure_registry_files(project_root: Path, registry_files: Iterable[str]) -> List[Path]:
    """Create missing registry files without modifying existing content."""
    created_paths: List[Path] = []
    for filename in registry_files:
        path = project_root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        created_paths.append(path)
    return created_paths


def initialize_project(project_root: Union[str, Path]) -> Dict[str, List[Path]]:
    """Create the standard project folders and empty registry CSV files."""
    root = Path(project_root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    return {
        "folders": ensure_directories(root, PROJECT_FOLDERS),
        "registries": ensure_registry_files(root, REGISTRY_FILES),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create the standard Hemli Vortex Lab project structure."
    )
    parser.add_argument("project_root", help="Project root folder to initialize.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = initialize_project(args.project_root)
    print(f"Initialized project: {Path(args.project_root).expanduser().resolve()}")
    print(f"Folders ready: {len(result['folders'])}")
    print(f"Registry files ready: {len(result['registries'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
