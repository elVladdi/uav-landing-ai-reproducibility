from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".ps1", ".yml", ".yaml", ".json", ".txt", ".cff", ".csv", ".env", ".example"}
PATTERNS = [
    re.compile(r"C:\\\\Users\\\\Vladimir", re.IGNORECASE),
    re.compile(r"OneDrive\\\\Documentos\\\\Tesis", re.IGNORECASE),
    re.compile(r"DNI\s*:\s*\d+", re.IGNORECASE),
]


def git_export_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [ROOT / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


class NoPrivatePathsTest(unittest.TestCase):
    def test_no_private_paths_in_exported_text_files(self) -> None:
        offenders: list[str] = []
        for path in git_export_files():
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if any(pattern.search(text) for pattern in PATTERNS):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
