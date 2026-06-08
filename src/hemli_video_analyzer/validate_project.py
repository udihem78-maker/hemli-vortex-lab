"""Validate a Hemli Vortex Lab project structure without modifying data."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from .registry_schema import (
    EXPERIMENTS_FOLDER,
    REGISTRY_SCHEMAS,
    REQUIRED_REGISTRY_FILES,
    REQUIRED_TOP_LEVEL_FOLDERS,
    registry_path,
)


@dataclass
class ProjectValidationResult:
    project_root: Path
    errors: List[str]
    warnings: List[str]

    @property
    def passed(self) -> bool:
        return not self.errors


def _read_metadata_experiment_id(metadata_path: Path) -> str:
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return ""
    value = data.get("experiment_id", "")
    return str(value).strip() if value is not None else ""


def _duplicate_values(values: Iterable[str]) -> List[str]:
    seen = set()
    duplicates = set()
    for value in values:
        normalized = value.strip().casefold()
        if not normalized:
            continue
        if normalized in seen:
            duplicates.add(value)
        seen.add(normalized)
    return sorted(duplicates)


def _registry_duplicate_ids(path: Path) -> List[str]:
    if not path.exists():
        return []
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return _duplicate_values(
                row.get("experiment_id", "") for row in csv.DictReader(handle)
            )
    except OSError:
        return []


def validate_project(project_root: Path) -> ProjectValidationResult:
    root = project_root.expanduser().resolve()
    errors: List[str] = []
    warnings: List[str] = []

    for folder in REQUIRED_TOP_LEVEL_FOLDERS:
        if not (root / folder).is_dir():
            errors.append(f"missing required folder: {folder}")

    for filename in REQUIRED_REGISTRY_FILES:
        path = registry_path(root, filename)
        if not path.is_file():
            errors.append(f"missing registry CSV: {path.relative_to(root)}")
            continue

        expected_header = REGISTRY_SCHEMAS[filename]
        try:
            with path.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.reader(handle)
                actual_header = next(reader, [])
        except OSError as exc:
            errors.append(f"cannot read registry CSV {path.relative_to(root)}: {exc}")
            continue

        if actual_header != expected_header:
            errors.append(f"unstable registry schema: {path.relative_to(root)}")

    experiments_dir = root / EXPERIMENTS_FOLDER
    if experiments_dir.is_dir():
        folder_ids = [path.name for path in experiments_dir.iterdir() if path.is_dir()]
        duplicate_folder_ids = _duplicate_values(folder_ids)
        if duplicate_folder_ids:
            errors.append(
                "duplicate experiment folder IDs: " + ", ".join(duplicate_folder_ids)
            )

        metadata_ids = [
            _read_metadata_experiment_id(path / "00_metadata" / "metadata.json")
            for path in experiments_dir.iterdir()
            if path.is_dir()
        ]
        duplicate_metadata_ids = _duplicate_values(metadata_ids)
        if duplicate_metadata_ids:
            errors.append(
                "duplicate metadata experiment IDs: "
                + ", ".join(duplicate_metadata_ids)
            )

        for path in experiments_dir.iterdir():
            if not path.is_dir():
                continue
            metadata_id = _read_metadata_experiment_id(
                path / "00_metadata" / "metadata.json"
            )
            if metadata_id and metadata_id.casefold() != path.name.casefold():
                warnings.append(
                    "metadata experiment_id differs from folder name: "
                    f"{path.name} -> {metadata_id}"
                )

    duplicate_registry_ids = _registry_duplicate_ids(
        registry_path(root, "experiments_registry.csv")
    )
    if duplicate_registry_ids:
        errors.append(
            "duplicate experiments_registry experiment IDs: "
            + ", ".join(duplicate_registry_ids)
        )

    return ProjectValidationResult(root, errors, warnings)


def print_summary(result: ProjectValidationResult) -> None:
    status = "PASS" if result.passed else "FAIL"
    print(f"{status}: project validation for {result.project_root}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a Hemli Vortex Lab project without modifying data."
    )
    parser.add_argument("project_root", help="Project root to validate.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_project(Path(args.project_root))
    print_summary(result)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
