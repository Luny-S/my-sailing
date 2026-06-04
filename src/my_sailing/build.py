"""Compile all LaTeX documents in documents/ to PDFs under build/."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = ROOT / "documents"
BUILD_DIR = ROOT / "build"
SKIP_DIRS = {"shared"}


def compile_doc(tex_file: Path) -> bool:
    rel = tex_file.relative_to(DOCS_DIR)
    out_dir = BUILD_DIR / rel.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            f"-output-directory={out_dir}",
            str(tex_file),
        ],
        capture_output=True,
        text=True,
        cwd=tex_file.parent,
    )

    pdf_name = tex_file.with_suffix(".pdf").name
    if result.returncode == 0:
        print(f"  OK  {rel} -> build/{rel.parent}/{pdf_name}")
        return True

    print(f"FAIL  {rel}", file=sys.stderr)
    print(result.stdout[-3000:], file=sys.stderr)
    return False


def main() -> None:
    tex_files = sorted(
        f
        for f in DOCS_DIR.rglob("*.tex")
        if not any(part in SKIP_DIRS for part in f.relative_to(DOCS_DIR).parts)
    )

    if not tex_files:
        print("No .tex files found under documents/.")
        sys.exit(0)

    BUILD_DIR.mkdir(exist_ok=True)
    print(f"Building {len(tex_files)} document(s)...\n")

    failures = [f for f in tex_files if not compile_doc(f)]

    print()
    if failures:
        print(f"{len(failures)} document(s) failed.")
        sys.exit(1)
    print(f"All {len(tex_files)} documents compiled successfully.")
