from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.hemli_video_analyzer.registry_schema import (
    REGISTRY_SCHEMAS,
    REQUIRED_TOP_LEVEL_FOLDERS,
    registry_path,
)
from src.hemli_video_analyzer.update_registries import update_registries
from src.hemli_video_analyzer.validate_experiment import validate_experiment
from src.hemli_video_analyzer.validate_project import validate_project


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class Issue2ValidationRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_project_folders(self) -> None:
        for folder in REQUIRED_TOP_LEVEL_FOLDERS:
            (self.root / folder).mkdir(parents=True, exist_ok=True)

    def create_ready_experiment(self, experiment_id: str = "EXP_DUMMY_READY") -> Path:
        experiment_root = self.root / "02_experiments" / experiment_id
        write_json(
            experiment_root / "00_metadata" / "metadata.json",
            {
                "experiment_id": experiment_id,
                "title": "Dummy vortex metadata",
                "source_url": "dummy://local-metadata-only",
                "phenomenon": "dummy vortex",
                "acceptance_level": "L1",
                "pixel_size_m": 0.001,
                "fps": 30,
                "quality_score": 80,
            },
        )
        write_json(experiment_root / "03_config" / "config.json", {"dummy": True})
        summary_path = experiment_root / "05_output_light" / "hemli_summary.csv"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with summary_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["HE", "HO", "HS", "HP"])
            writer.writeheader()
            writer.writerow({"HE": "0.1", "HO": "0.2", "HS": "0.3", "HP": "0.4"})
        return experiment_root

    def test_validate_experiment_reports_ready_and_blocked_states(self) -> None:
        self.create_project_folders()
        self.create_ready_experiment()

        ready = validate_experiment(self.root, "EXP_DUMMY_READY")
        self.assertTrue(ready.ready)
        self.assertEqual([], ready.missing)

        blocked_root = self.root / "02_experiments" / "EXP_BLOCKED"
        write_json(
            blocked_root / "00_metadata" / "metadata.json",
            {"experiment_id": "EXP_BLOCKED", "acceptance_level": "L0"},
        )
        blocked = validate_experiment(self.root, "EXP_BLOCKED")
        self.assertFalse(blocked.ready)
        self.assertIn(
            "metadata source_url or local_video_path/local_video_file",
            blocked.missing,
        )
        self.assertIn("metadata phenomenon", blocked.missing)
        self.assertIn("03_config/config.json", blocked.missing)

    def test_update_registries_writes_stable_dummy_csvs(self) -> None:
        self.create_project_folders()
        self.create_ready_experiment()

        written = update_registries(self.root)

        self.assertEqual(set(REGISTRY_SCHEMAS), set(written))
        for filename, columns in REGISTRY_SCHEMAS.items():
            with registry_path(self.root, filename).open(
                newline="", encoding="utf-8"
            ) as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(columns, reader.fieldnames)
                rows = list(reader)
            self.assertEqual(1, len(rows), filename)
            self.assertEqual("EXP_DUMMY_READY", rows[0]["experiment_id"])

        with registry_path(self.root, "experiments_registry.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual("dummy vortex", row["phenomenon"])
        self.assertEqual("0.4", row["HP"])

    def test_validate_project_passes_after_registry_update(self) -> None:
        self.create_project_folders()
        self.create_ready_experiment()
        update_registries(self.root)

        result = validate_project(self.root)

        self.assertTrue(result.passed, result.errors)

    def test_validate_project_fails_for_missing_structure(self) -> None:
        result = validate_project(self.root)

        self.assertFalse(result.passed)
        self.assertTrue(any("missing required folder" in item for item in result.errors))


if __name__ == "__main__":
    unittest.main()
