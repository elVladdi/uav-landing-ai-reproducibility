from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase06AnalysisOutputsTest(unittest.TestCase):
    def test_core_reports_exist(self) -> None:
        for relative in [
            "outputs/tables/phase06_analysis/phase06_dataset_audit.md",
            "outputs/tables/phase06_analysis/phase06_descriptive_statistics.md",
            "outputs/tables/phase06_analysis/phase06_hypothesis_tests.md",
            "outputs/tables/phase06_analysis/phase06_scenario_analysis.md",
            "outputs/tables/phase06_analysis/phase06_incident_analysis.md",
        ]:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_dataset_audit_reports_no_review(self) -> None:
        text = (ROOT / "outputs/tables/phase06_analysis/phase06_dataset_audit.md").read_text(encoding="utf-8")
        self.assertIn("OK: 37", text)
        self.assertIn("REVIEW: 0", text)


if __name__ == "__main__":
    unittest.main()
