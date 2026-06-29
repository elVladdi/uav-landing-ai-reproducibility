from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase05DatasetContractTest(unittest.TestCase):
    def test_accepted_runs_contract(self) -> None:
        path = ROOT / "outputs/tables/phase05_experiments/phase05_accepted_runs.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(160, len(rows))
        self.assertEqual({"T0", "T1"}, {row["treatment"] for row in rows})
        self.assertEqual(8, len({row["scenario_id"] for row in rows}))
        self.assertEqual(80, len({row["treatment_pair_id"] for row in rows}))
        self.assertTrue(all(row["curation_status"] == "accepted" for row in rows))


if __name__ == "__main__":
    unittest.main()
