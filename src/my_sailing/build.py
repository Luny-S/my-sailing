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
    # Mirror the source tree under build/ (e.g. build/documents/passage-card/),
    # matching the LaTeX Workshop IDE output dir and the fill-doc registry.
    out_rel = tex_file.relative_to(ROOT).parent
    out_dir = BUILD_DIR / out_rel
    out_dir.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            f"-output-directory={out_dir}",
            str(tex_file),
        ],
        capture_output=True,
        # pdflatex logs aren't always valid UTF-8 (font/encoding names);
        # decode leniently so a stray byte can't crash the build.
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=tex_file.parent,
    )

    pdf_name = tex_file.with_suffix(".pdf").name
    if result.returncode == 0:
        print(f"  OK  {rel} -> build/{out_rel}/{pdf_name}")
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
