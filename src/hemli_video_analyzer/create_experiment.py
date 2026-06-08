"""Experiment creation CLI for Hemli Vortex Lab.

Creates a standardized experiment folder with metadata and intake templates.
This module does not download or process videos.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

EXPERIMENT_FOLDERS = [
    "00_metadata",
    "01_input",
    "02_calibration",
    "03_config",
    "04_output_raw",
    "05_output_light",
    "06_validation",
    "07_interpretation",
]

DEFAULT_METADATA = {
    "experiment_id": "",
    "source_type": "local_video / youtube / university / cfd / piv / dns",
    "source_url": "",
    "local_video_file": "",
    "title": "",
    "institution_or_channel": "",
    "date_accessed": "",
    "rights_notes": "",
    "phenomenon": "",
    "medium": "",
    "geometry": "",
    "known_length_m": None,
    "known_length_pixels": None,
    "pixel_size_m": None,
    "fps": None,
    "slow_motion_factor": 1.0,
    "nu_m2_s": None,
    "density_kg_m3": None,
    "inlet_velocity_m_s": None,
    "characteristic_length_m": None,
    "rotation_f_1_s": None,
    "buoyancy_N_1_s": None,
    "sound_speed_m_s": None,
    "quality_score": None,
    "acceptance_level": "L0/L1/L2/L3",
    "analysis_status": "METADATA_STARTED",
    "notes": "",
}

TEMPLATE_MAP = {
    "intake_form_template.md": "intake_form.md",
    "calibration_sheet_template.md": "calibration_sheet.md",
    "quality_score_template.md": "quality_score.md",
    "acceptance_decision_template.md": "acceptance_decision.md",
}

FALLBACK_MARKDOWN = {
    "intake_form.md": "# Experiment Intake Form\n\n- Experiment ID:\n- Source URL:\n- Phenomenon:\n- Expected level:\n",
    "calibration_sheet.md": "# Calibration Sheet\n\n- known_length_m:\n- known_length_pixels:\n- pixel_size_m:\n- fps:\n",
    "quality_score.md": "# Quality Score\n\nTotal score: \nAcceptance level: \n",
    "acceptance_decision.md": "# Acceptance Decision\n\nDecision: L0 / L1 / L2 / L3 / Reject\n",
}


def repo_root_from_module() -> Path:
    """Best-effort repository root for locating template files."""
    return Path(__file__).resolve().parents[2]


def create_metadata(path: Path, experiment_id: str, force: bool = False) -> None:
    if path.exists() and not force:
        return
    payload = dict(DEFAULT_METADATA)
    payload["experiment_id"] = experiment_id
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def copy_or_create_template(
    templates_dir: Path,
    target_dir: Path,
    template_name: str,
    target_name: str,
    force: bool = False,
) -> None:
    target = target_dir / target_name
    if target.exists() and not force:
        return

    source = templates_dir / template_name
    if source.exists():
        shutil.copyfile(source, target)
    else:
        target.write_text(FALLBACK_MARKDOWN[target_name], encoding="utf-8")


def create_experiment(project_root: Path, experiment_id: str, force: bool = False) -> Path:
    project_root = project_root.expanduser().resolve()
    experiment_root = project_root / "02_experiments" / experiment_id

    if experiment_root.exists() and not force:
        # Do not overwrite existing experiment data. Create missing subfolders/templates only.
        pass

    for folder in EXPERIMENT_FOLDERS:
        (experiment_root / folder).mkdir(parents=True, exist_ok=True)

    metadata_dir = experiment_root / "00_metadata"
    create_metadata(metadata_dir / "metadata.json", experiment_id, force=force)

    templates_dir = repo_root_from_module() / "templates"
    for template_name, target_name in TEMPLATE_MAP.items():
        copy_or_create_template(templates_dir, metadata_dir, template_name, target_name, force=force)

    (experiment_root / "01_input" / "source_url.txt").touch(exist_ok=True)
    return experiment_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a standardized Hemli experiment folder."
    )
    parser.add_argument("project_root", help="Root folder for the research project")
    parser.add_argument("experiment_id", help="Experiment ID, e.g. EXP_KH_0001")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite generated metadata/template files. Does not delete raw data.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = create_experiment(Path(args.project_root), args.experiment_id, force=args.force)
    print(f"Experiment created/verified: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
