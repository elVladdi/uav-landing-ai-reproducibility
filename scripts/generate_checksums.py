from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reproducibility_manifest" / "files.sha256"
INCLUDE_DIRS = ["configs", "data/curated", "outputs/tables", "scripts", "src/analysis", "docs/methodology", "docs/article_support"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files() -> list[Path]:
    files: list[Path] = []
    for directory in INCLUDE_DIRS:
        base = ROOT / directory
        if base.exists():
            files.extend(path for path in base.rglob("*") if path.is_file())
    return sorted(set(files), key=lambda item: item.relative_to(ROOT).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SHA256 checksums for public reproducibility files.")
    parser.add_argument("--check", action="store_true", help="Check existing checksum file instead of writing it.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    content = "\n".join(f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}" for path in iter_files()) + "\n"
    if args.check:
        if not output.exists():
            print(f"Missing checksum file: {output}")
            return 1
        if output.read_text(encoding="utf-8") != content:
            print("Checksum file is out of date.")
            return 1
        print("Checksum file is current.")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
