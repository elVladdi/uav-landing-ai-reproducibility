from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReproducibilityCommandsTest(unittest.TestCase):
    def test_reproduction_scripts_exist(self) -> None:
        for relative in [
            "scripts/reproduce_analysis.ps1",
            "scripts/reproduce_phase05_tables.ps1",
            "scripts/reproduce_phase06_tables.ps1",
            "scripts/verify_public_package.py",
            "scripts/generate_checksums.py",
        ]:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_execution_order_mentions_core_scripts(self) -> None:
        text = (ROOT / "reproducibility_manifest/execution_order.md").read_text(encoding="utf-8")
        self.assertIn("phase06_dataset_audit.py", text)
        self.assertIn("phase06_hypothesis_tests.py", text)


if __name__ == "__main__":
    unittest.main()
