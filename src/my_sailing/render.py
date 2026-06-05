"""Render a document model to a print-ready PDF with HTML/CSS + WeasyPrint.

This is the print-only path (no interactive form fields): a pydantic model is
bound directly into a Jinja2 template and rendered to an A4 PDF. CSS handles
field underlines, table layout and text wrapping, so long values no longer
overflow. Bilingual fields render their per-language value on each page.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import ValidationError
from weasyprint import CSS, HTML

from .models import DOCUMENTS, DocumentSpec, get_document

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
LOGO_PATH = ROOT / "documents" / "shared" / "assets" / "pzz-logo.png"


def _logo_data_uri() -> str:
    data = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def _bilingual(value: object, lang: str) -> str:
    """Pick the ``lang`` ('pl'/'en') side of a Bilingual value (or '')."""
    if value is None:
        return ""
    return getattr(value, lang, "") or ""


def _environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["bi"] = _bilingual
    env.globals["logo"] = _logo_data_uri()
    return env


def render_html(spec: DocumentSpec, data: dict) -> str:
    """Validate ``data`` against the document model and render the HTML."""
    model = spec.model.model_validate(data)
    template = _environment().get_template(spec.html_template)
    return template.render(d=model)


def render_document(spec: DocumentSpec, data: dict, out_path: Path) -> None:
    """Validate, render and write the print-ready PDF."""
    html = render_html(spec, data)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stylesheets = [CSS(filename=str(TEMPLATES_DIR / "form.css"))]
    HTML(string=html, base_url=str(TEMPLATES_DIR)).write_pdf(
        str(out_path), stylesheets=stylesheets
    )


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="render-doc",
        description="Render a print-ready, pre-filled PDF (HTML/CSS + WeasyPrint).",
    )
    ap.add_argument("document", nargs="?", help="which document (e.g. passage-card)")
    ap.add_argument("data", type=Path, nargs="?", help="JSON file with the data")
    ap.add_argument("-o", "--output", type=Path, help="output PDF path")
    ap.add_argument("-l", "--list", action="store_true", dest="list_documents",
                    help="list available documents and exit")
    ap.add_argument("--html", action="store_true", help="write rendered HTML instead of PDF")
    args = ap.parse_args()

    if args.list_documents or (args.document is None and args.data is None):
        print("Available documents:\n")
        for spec in DOCUMENTS.values():
            print(f"  {spec.name:<14} {spec.title}")
        return

    try:
        spec = get_document(args.document)
    except KeyError as exc:
        sys.exit(exc.args[0])

    if args.data is None or args.output is None:
        ap.error("a DATA json file and -o/--output are required")

    data = json.loads(args.data.read_text(encoding="utf-8"))
    try:
        if args.html:
            args.output.write_text(render_html(spec, data), encoding="utf-8")
        else:
            render_document(spec, data, args.output)
    except ValidationError as exc:
        errors = "\n".join(
            f"  - {'.'.join(str(p) for p in e['loc']) or '(root)'}: {e['msg']}"
            for e in exc.errors()
        )
        sys.exit(f"Invalid {spec.name} data in {args.data}:\n{errors}")

    print(f"Wrote {args.output}")
