"""Validate a single Hemli Vortex Lab experiment without running analysis."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .registry_schema import EXPERIMENTS_FOLDER


@dataclass
class ExperimentValidationResult:
    experiment_root: Path
    missing: List[str]

    @property
    def ready(self) -> bool:
        return not self.missing


def _load_metadata(metadata_path: Path, missing: List[str]) -> Dict[str, Any]:
    if not metadata_path.is_file():
        missing.append("00_metadata/metadata.json")
        return {}
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        missing.append(f"00_metadata/metadata.json valid JSON ({exc})")
        return {}
    if not isinstance(data, dict):
        missing.append("00_metadata/metadata.json object root")
        return {}
    return data


def _has_value(metadata: Dict[str, Any], *keys: str) -> bool:
    for key in keys:
        value = metadata.get(key)
        if value is not None and str(value).strip():
            return True
    return False


def validate_experiment(project_root: Path, experiment_id: str) -> ExperimentValidationResult:
    root = project_root.expanduser().resolve()
    experiment_root = root / EXPERIMENTS_FOLDER / experiment_id
    missing: List[str] = []

    if not experiment_root.is_dir():
        missing.append(f"{EXPERIMENTS_FOLDER}/{experiment_id}/")
        return ExperimentValidationResult(experiment_root, missing)

    metadata = _load_metadata(experiment_root / "00_metadata" / "metadata.json", missing)

    if metadata:
        if not _has_value(metadata, "source_url", "local_video_path", "local_video_file"):
            missing.append("metadata source_url or local_video_path/local_video_file")
        if not _has_value(metadata, "phenomenon"):
            missing.append("metadata phenomenon")
        if not _has_value(metadata, "acceptance_level"):
            missing.append("metadata acceptance_level")

    if not (experiment_root / "03_config" / "config.json").is_file():
        missing.append("03_config/config.json")

    return ExperimentValidationResult(experiment_root, missing)


def print_summary(result: ExperimentValidationResult) -> None:
    if result.ready:
        print(f"READY_TO_ANALYZE: {result.experiment_root}")
        return

    print(f"BLOCKED: {result.experiment_root}")
    for item in result.missing:
        print(f"MISSING: {item}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a Hemli experiment without running analysis."
    )
    parser.add_argument("project_root", help="Project root containing experiments.")
    parser.add_argument("experiment_id", help="Experiment ID to validate.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_experiment(Path(args.project_root), args.experiment_id)
    print_summary(result)
    return 0 if result.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
