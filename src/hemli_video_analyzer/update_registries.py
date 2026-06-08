"""Update Hemli Vortex Lab registry CSVs from lightweight experiment metadata."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from .registry_schema import (
    EXPERIMENTS_FOLDER,
    REGISTRY_SCHEMAS,
    database_dir,
    registry_path,
)


JsonMap = Mapping[str, Any]
CsvRow = Dict[str, str]


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _first_value(*values: Any) -> str:
    for value in values:
        text = _text(value).strip()
        if text:
            return text
    return ""


def _blank_row(columns: Iterable[str]) -> CsvRow:
    return {column: "" for column in columns}


def _read_metadata(experiment_dir: Path) -> Dict[str, Any]:
    metadata_path = experiment_dir / "00_metadata" / "metadata.json"
    if not metadata_path.is_file():
        return {}
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _read_first_csv_row(paths: Iterable[Path]) -> CsvRow:
    for path in paths:
        if not path.is_file():
            continue
        try:
            with path.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                row = next(reader, None)
        except OSError:
            continue
        if row:
            return {key: _text(value) for key, value in row.items()}
    return {}


def _write_csv(path: Path, columns: List[str], rows: List[CsvRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def discover_experiment_dirs(project_root: Path) -> List[Path]:
    experiments_dir = project_root / EXPERIMENTS_FOLDER
    if not experiments_dir.is_dir():
        return []
    return sorted(path for path in experiments_dir.iterdir() if path.is_dir())


def _output_rows(experiment_dir: Path) -> Dict[str, CsvRow]:
    return {
        "calibration": _read_first_csv_row(
            [
                experiment_dir / "02_calibration" / "calibration_registry.csv",
                experiment_dir / "02_calibration" / "calibration_summary.csv",
                experiment_dir / "02_calibration" / "calibration.csv",
            ]
        ),
        "quality": _read_first_csv_row(
            [
                experiment_dir / "06_validation" / "quality_scores.csv",
                experiment_dir / "06_validation" / "quality_score.csv",
            ]
        ),
        "summary": _read_first_csv_row(
            [
                experiment_dir / "05_output_light" / "combined_hemli_summary.csv",
                experiment_dir / "05_output_light" / "hemli_summary.csv",
                experiment_dir / "05_output_light" / "summary.csv",
            ]
        ),
    }


def _experiment_id(folder_id: str, metadata: JsonMap) -> str:
    return _first_value(metadata.get("experiment_id"), folder_id)


def _experiments_row(
    folder_id: str,
    metadata: JsonMap,
    outputs: Mapping[str, CsvRow],
) -> CsvRow:
    row = _blank_row(REGISTRY_SCHEMAS["experiments_registry.csv"])
    summary = outputs["summary"]
    quality = outputs["quality"]
    experiment_id = _experiment_id(folder_id, metadata)

    row.update(
        {
            "experiment_id": experiment_id,
            "title": _first_value(metadata.get("title"), summary.get("title")),
            "phenomenon": _first_value(metadata.get("phenomenon")),
            "source_type": _first_value(metadata.get("source_type")),
            "source_url": _first_value(metadata.get("source_url")),
            "local_video_file": _first_value(
                metadata.get("local_video_file"), metadata.get("local_video_path")
            ),
            "institution_or_channel": _first_value(
                metadata.get("institution_or_channel")
            ),
            "date_accessed": _first_value(metadata.get("date_accessed")),
            "rights_status": _first_value(
                metadata.get("rights_status"), metadata.get("rights_notes")
            ),
            "medium": _first_value(metadata.get("medium")),
            "geometry": _first_value(metadata.get("geometry")),
            "fps": _first_value(metadata.get("fps")),
            "known_length_m": _first_value(metadata.get("known_length_m")),
            "known_length_pixels": _first_value(metadata.get("known_length_pixels")),
            "pixel_size_m": _first_value(metadata.get("pixel_size_m")),
            "nu_m2_s": _first_value(metadata.get("nu_m2_s")),
            "quality_score": _first_value(
                metadata.get("quality_score"), quality.get("total_score")
            ),
            "acceptance_level": _first_value(
                metadata.get("acceptance_level"), quality.get("acceptance_level")
            ),
            "analysis_status": _first_value(
                metadata.get("analysis_status"),
                "METADATA_MISSING" if not metadata else "METADATA_AVAILABLE",
            ),
            "notes": _first_value(metadata.get("notes"), summary.get("notes")),
        }
    )

    for target, source_names in {
        "HE": ["HE", "HE_energy_result"],
        "HO": ["HO", "HO_order"],
        "HS": ["HS", "HS_stability"],
        "HP": ["HP", "HP_overall"],
        "fractal_D": ["fractal_D"],
        "rot_dom": ["rot_dom"],
        "Re": ["Re"],
        "Ro": ["Ro"],
        "Fr": ["Fr"],
        "Ma": ["Ma"],
    }.items():
        row[target] = _first_value(*(summary.get(name) for name in source_names))

    return row


def _source_row(folder_id: str, metadata: JsonMap) -> CsvRow:
    row = _blank_row(REGISTRY_SCHEMAS["source_registry.csv"])
    experiment_id = _experiment_id(folder_id, metadata)
    row.update(
        {
            "source_id": _first_value(metadata.get("source_id"), experiment_id),
            "experiment_id": experiment_id,
            "source_url": _first_value(metadata.get("source_url")),
            "local_video_file": _first_value(
                metadata.get("local_video_file"), metadata.get("local_video_path")
            ),
            "title": _first_value(metadata.get("title")),
            "institution_or_channel": _first_value(
                metadata.get("institution_or_channel")
            ),
            "source_type": _first_value(metadata.get("source_type")),
            "phenomenon": _first_value(metadata.get("phenomenon")),
            "downloaded": _first_value(metadata.get("downloaded"), "no"),
            "rights_status": _first_value(
                metadata.get("rights_status"), metadata.get("rights_notes")
            ),
            "metadata_quality": _first_value(metadata.get("metadata_quality")),
            "recommended_use": _first_value(metadata.get("recommended_use")),
            "notes": _first_value(metadata.get("notes")),
        }
    )
    return row


def _calibration_row(
    folder_id: str,
    metadata: JsonMap,
    outputs: Mapping[str, CsvRow],
) -> CsvRow:
    row = _blank_row(REGISTRY_SCHEMAS["calibration_registry.csv"])
    calibration = outputs["calibration"]
    row["experiment_id"] = _experiment_id(folder_id, metadata)
    for column in row:
        if column == "experiment_id":
            continue
        row[column] = _first_value(calibration.get(column), metadata.get(column))
    return row


def _quality_row(
    folder_id: str,
    metadata: JsonMap,
    outputs: Mapping[str, CsvRow],
) -> CsvRow:
    row = _blank_row(REGISTRY_SCHEMAS["quality_scores.csv"])
    quality = outputs["quality"]
    row["experiment_id"] = _experiment_id(folder_id, metadata)
    for column in row:
        if column == "experiment_id":
            continue
        row[column] = _first_value(quality.get(column), metadata.get(column))
    row["total_score"] = _first_value(row["total_score"], metadata.get("quality_score"))
    row["acceptance_level"] = _first_value(
        row["acceptance_level"], metadata.get("acceptance_level")
    )
    return row


def _summary_row(
    folder_id: str,
    metadata: JsonMap,
    outputs: Mapping[str, CsvRow],
) -> CsvRow:
    row = _blank_row(REGISTRY_SCHEMAS["combined_hemli_summary.csv"])
    summary = outputs["summary"]
    row["experiment_id"] = _experiment_id(folder_id, metadata)
    for column in row:
        if column == "experiment_id":
            continue
        row[column] = _first_value(summary.get(column), metadata.get(column))
    return row


def update_registries(project_root: Path) -> Dict[str, Path]:
    root = project_root.expanduser().resolve()
    database_dir(root).mkdir(parents=True, exist_ok=True)

    rows: Dict[str, List[CsvRow]] = {filename: [] for filename in REGISTRY_SCHEMAS}
    for experiment_dir in discover_experiment_dirs(root):
        folder_id = experiment_dir.name
        metadata = _read_metadata(experiment_dir)
        outputs = _output_rows(experiment_dir)
        rows["experiments_registry.csv"].append(
            _experiments_row(folder_id, metadata, outputs)
        )
        rows["source_registry.csv"].append(_source_row(folder_id, metadata))
        rows["calibration_registry.csv"].append(
            _calibration_row(folder_id, metadata, outputs)
        )
        rows["quality_scores.csv"].append(_quality_row(folder_id, metadata, outputs))
        rows["combined_hemli_summary.csv"].append(
            _summary_row(folder_id, metadata, outputs)
        )

    written: Dict[str, Path] = {}
    for filename, columns in REGISTRY_SCHEMAS.items():
        path = registry_path(root, filename)
        _write_csv(path, columns, rows[filename])
        written[filename] = path

    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Update lightweight registry CSVs from experiment metadata."
    )
    parser.add_argument("project_root", help="Project root containing experiments.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    written = update_registries(Path(args.project_root))
    print("UPDATED_REGISTRIES")
    for filename in sorted(written):
        print(f"{filename}: {written[filename]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
