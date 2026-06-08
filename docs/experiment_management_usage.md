# Experiment Management CLI Usage

These commands create and verify the standardized folder structure for Hemli Vortex Lab research projects.

Budget-safe rule: these commands do not download videos, do not run optical flow, do not run batch video analysis, and do not install packages.

## Initialize a project

Run these commands from the repository root so `src/` is importable.

```powershell
python -m src.hemli_video_analyzer.project_init C:\Hemli_Vortex_Research
```

This creates:

```text
00_admin/
01_sources/
02_experiments/
03_processed_results/
04_combined_database/
05_reports/
06_figures_for_papers/
07_code/
08_archive/
```

It also creates empty registry CSV files under `04_combined_database/`.

## Create an experiment

```powershell
python -m src.hemli_video_analyzer.create_experiment C:\Hemli_Vortex_Research EXP_KH_0001
```

This creates:

```text
02_experiments/EXP_KH_0001/
  00_metadata/
  01_input/
  02_calibration/
  03_config/
  04_output_raw/
  05_output_light/
  06_validation/
  07_interpretation/
```

Generated metadata and forms are placed under `00_metadata/`.

## Data policy

Do not store raw videos or large `flow_field_xyuv.csv` files in lightweight research handoff archives. Keep them in local raw-data storage only.

## Calibrated vs uncalibrated reporting levels

- **L0 Demonstration**: no usable spatial and timing calibration, only qualitative interpretation.
- **L1 Comparative**: partial calibration, HP trends can be compared across similarly processed runs.
- **L2 Semi-Quantitative**: calibrated scale and timing with geometry context; allows conservative physical reporting.
- **L3 Research-grade**: complete spatial, timing, fluid-property, and geometry calibration; supports research-grade claims.

Report snippet text for future HTML integration:

- `Spatial scale missing: velocities and length scales are pixel-based.`
- `Timing calibration missing or inherited from video metadata.`
- `Reynolds number is not reported because fluid viscosity is missing.`
