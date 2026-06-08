from __future__ import annotations

import unittest

from src.hemli_video_analyzer.calibration_status import classify_reporting_status


class CalibrationStatusTests(unittest.TestCase):
    def test_missing_spatial_timing_and_nu_adds_required_snippets(self) -> None:
        metadata = {
            "pixel_size_m": None,
            "fps": None,
            "slow_motion_factor": 1.0,
            "nu_m2_s": None,
            "density_kg_m3": 1000.0,
            "characteristic_length_m": None,
            "geometry": "",
        }

        result = classify_reporting_status(metadata)

        self.assertEqual(result["acceptance_level"], "L0")
        self.assertFalse(result["allowed_claims"]["can_report_physical_velocity"])
        self.assertFalse(result["allowed_claims"]["can_report_reynolds"])
        self.assertIn(
            "Spatial scale missing: velocities and length scales are pixel-based.",
            result["report_snippets"],
        )
        self.assertIn(
            "Timing calibration missing or inherited from video metadata.",
            result["report_snippets"],
        )
        self.assertIn(
            "Reynolds number is not reported because fluid viscosity is missing.",
            result["report_snippets"],
        )

    def test_complete_metadata_enables_l3_claims(self) -> None:
        metadata = {
            "pixel_size_m": 1e-3,
            "fps": 120.0,
            "slow_motion_factor": 1.0,
            "nu_m2_s": 1.5e-5,
            "density_kg_m3": 1.225,
            "characteristic_length_m": 0.2,
            "geometry": "cylinder",
        }

        result = classify_reporting_status(metadata)

        self.assertEqual(result["quality_score_0_100"], 100)
        self.assertEqual(result["acceptance_level"], "L3")
        self.assertTrue(result["allowed_claims"]["can_compare_hp"])
        self.assertTrue(result["allowed_claims"]["can_report_physical_velocity"])
        self.assertTrue(result["allowed_claims"]["can_report_reynolds"])
        self.assertTrue(result["allowed_claims"]["can_make_research_grade_claim"])
        self.assertEqual(result["report_snippets"], [])


if __name__ == "__main__":
    unittest.main()
