import unittest

from src.hemli_video_analyzer.calibration_status import (
    classify_quality_status,
    report_calibration_snippets,
    validate_calibration_metadata,
)


class CalibrationStatusTests(unittest.TestCase):
    def test_validation_flags_for_complete_dummy_metadata(self) -> None:
        metadata = {
            "pixel_size_m": 0.001,
            "fps": 240,
            "slow_motion_factor": 1.0,
            "nu_m2_s": 1.5e-5,
            "density_kg_m3": 1.2,
            "characteristic_length_m": 0.2,
        }
        flags = validate_calibration_metadata(metadata)
        self.assertEqual(
            flags,
            {
                "has_spatial_scale": True,
                "has_timing": True,
                "has_fluid_properties": True,
                "has_geometry": True,
            },
        )

    def test_missing_calibration_blocks_physical_claims(self) -> None:
        metadata = {
            "fps": 30,
            "slow_motion_factor": 1.0,
            "density_kg_m3": 998,
            "characteristic_length_m": 0.1,
        }
        result = classify_quality_status(metadata)
        self.assertEqual(result["acceptance_level"], "L1")
        self.assertFalse(result["allowed_claims"]["can_report_physical_velocity"])
        self.assertFalse(result["allowed_claims"]["can_report_reynolds"])
        self.assertFalse(result["allowed_claims"]["can_make_research_grade_claim"])

    def test_snippets_for_missing_required_fields(self) -> None:
        snippets = report_calibration_snippets({"density_kg_m3": 1.2})
        self.assertIn("Spatial scale missing: velocities and length scales are pixel-based.", snippets)
        self.assertIn("Timing calibration missing or inherited from video metadata.", snippets)
        self.assertIn("Reynolds number is not reported because fluid viscosity is missing.", snippets)


if __name__ == "__main__":
    unittest.main()
