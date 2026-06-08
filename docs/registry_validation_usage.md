# Registry Validation Usage

These tools only inspect lightweight project metadata and small CSV files. They do not download videos, run optical flow, run batch analysis, process video files, or install packages.

Run commands from the repository root so the `src/` package is importable.

## Validate a project

```powershell
python -m src.hemli_video_analyzer.validate_project C:\tmp\hemli_dummy_project
```

The command checks the required top-level folders, registry CSV files under `04_combined_database\`, stable CSV headers, and duplicate experiment IDs. It prints a `PASS` or `FAIL` summary and does not modify files.

## Validate an experiment

```powershell
python -m src.hemli_video_analyzer.validate_experiment C:\tmp\hemli_dummy_project EXP_DUMMY_READY
```

The command prints `READY_TO_ANALYZE` when the experiment has metadata, a source reference in metadata, a phenomenon, an acceptance level, and `03_config\config.json`. Otherwise it prints `BLOCKED` with the missing items. It does not run analysis.

## Update registries

```powershell
python -m src.hemli_video_analyzer.update_registries C:\tmp\hemli_dummy_project
```

The command scans experiment folders, reads `00_metadata\metadata.json`, and merges any lightweight output CSVs found under calibration, validation, or light-output folders. Missing output CSVs are handled as empty fields.

Updated registry files:

```text
04_combined_database/experiments_registry.csv
04_combined_database/source_registry.csv
04_combined_database/calibration_registry.csv
04_combined_database/quality_scores.csv
04_combined_database/combined_hemli_summary.csv
```
