"""Pre-fill a form PDF (e.g. the karta rejsu) from a JSON data file.

The form PDFs built from ``documents/`` contain real AcroForm fields. This
module fills them from a ``{field_name: value}`` JSON mapping and, by default,
*flattens* the result to a static, non-editable PDF.

Flattening is done in three steps so that Polish diacritics render correctly:

1. capture every filled field's rectangle and value;
2. ``doc.bake()`` turns the (still empty) field borders/underlines into static
   page content and removes the interactive widgets;
3. the values are drawn on top using **Latin Modern Roman** — the same family
   the LaTeX document uses, and one that covers the full Polish alphabet.

The base-14 Helvetica that form widgets use cannot render ł/ż/ą/ę/…, which is
why we draw the text ourselves rather than letting the widget appearance show.

Usage::

    uv run fill-doc data.json -o filled.pdf            # flatten (default)
    uv run fill-doc data.json -o filled.pdf --keep-editable
    uv run fill-doc --list-fields                      # list field names
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

import fitz  # PyMuPDF
from pydantic import ValidationError

from .models import DOCUMENTS, DocumentSpec, get_document

ROOT = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = ROOT / "build"

# PDF text-field flag: bit 13 (1<<12) marks a multiline field.
_FF_MULTILINE = 1 << 12

# Latin Modern Roman ships with texlive-fonts-recommended (see Dockerfile) and
# covers the full Polish alphabet. Resolve it lazily so import never fails.
_FONT_NAME = "LMR"
_FONT_GLOBS = (
    "/usr/share/texmf/fonts/opentype/public/lm/lmroman10-regular.otf",
    "/usr/share/texlive/**/lmroman10-regular.otf",
    "/usr/share/**/lmroman10-regular.otf",
)


def _font_path() -> str:
    for pattern in _FONT_GLOBS:
        if "*" in pattern:
            hits = glob.glob(pattern, recursive=True)
            if hits:
                return hits[0]
        elif Path(pattern).exists():
            return pattern
    raise FileNotFoundError(
        "Latin Modern Roman OTF not found. Install texlive-fonts-recommended "
        "(it provides lmroman10-regular.otf)."
    )


def _coerce(value: object) -> str:
    if isinstance(value, bool):
        return "TAK" if value else "NIE"
    return str(value)


def fill_pdf(
    template: Path,
    data: dict,
    out_path: Path,
    *,
    flatten: bool = True,
) -> dict:
    """Fill ``template``'s form fields from ``data`` and write ``out_path``.

    Returns a report dict with ``applied`` / ``unknown`` / ``missing`` keys.
    """
    doc = fitz.open(template)
    field_names: set[str] = set()
    applied: set[str] = set()

    if not flatten:
        # Keep the form interactive: set widget values directly.
        for page in doc:
            for w in page.widgets() or []:
                field_names.add(w.field_name)
                if w.field_name in data:
                    w.field_value = _coerce(data[w.field_name])
                    w.update()
                    applied.add(w.field_name)
    else:
        font_path = _font_path()
        # 1. capture rectangles + values before the widgets are removed.
        to_draw: list[tuple[int, fitz.Rect, str, float, bool]] = []
        for pno, page in enumerate(doc):
            for w in page.widgets() or []:
                field_names.add(w.field_name)
                if w.field_name not in data:
                    continue
                text = _coerce(data[w.field_name])
                applied.add(w.field_name)
                if not text.strip():
                    continue
                multiline = bool((w.field_flags or 0) & _FF_MULTILINE)
                size = w.text_fontsize or 9.0
                to_draw.append((pno, fitz.Rect(w.rect), text, size, multiline))

        # 2. flatten borders/underlines and drop the interactive widgets.
        doc.bake(annots=True, widgets=True)

        # 3. draw the values on top with a Polish-capable font.
        for pno, rect, text, size, multiline in to_draw:
            page = doc[pno]
            page.insert_font(fontname=_FONT_NAME, fontfile=font_path)
            if multiline:
                page.insert_textbox(
                    rect + (2, 1, -2, -1), text,
                    fontname=_FONT_NAME, fontfile=font_path,
                    fontsize=size, align=fitz.TEXT_ALIGN_LEFT,
                )
            else:
                baseline = rect.y0 + rect.height / 2 + size * 0.35
                page.insert_text(
                    fitz.Point(rect.x0 + 2, baseline), text,
                    fontname=_FONT_NAME, fontfile=font_path, fontsize=size,
                )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path, garbage=4, deflate=True)
    doc.close()
    return {
        "applied": sorted(applied),
        "unknown": sorted(set(data) - field_names),
        "missing": sorted(field_names - applied),
    }


def fill_document(
    spec: DocumentSpec,
    data: dict,
    out_path: Path,
    *,
    flatten: bool = True,
) -> dict:
    """Validate ``data`` against the document's model, adapt it to form fields
    and write the filled PDF. Raises ``pydantic.ValidationError`` on bad input.
    """
    model = spec.model.model_validate(data)
    fields = model.to_form_fields()
    return fill_pdf(spec.template, fields, out_path, flatten=flatten)


def list_fields(template: Path) -> list[str]:
    doc = fitz.open(template)
    names = sorted({w.field_name for p in doc for w in (p.widgets() or [])})
    doc.close()
    return names


def _print_documents() -> None:
    print("Available documents:\n")
    for spec in DOCUMENTS.values():
        built = "" if spec.template_built else "  (not built — run `uv run build-docs`)"
        print(f"  {spec.name:<14} {spec.title}{built}")


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="fill-doc",
        description="Fill a sailing form PDF from a JSON data file and flatten it.",
    )
    ap.add_argument("document", nargs="?",
                    help="which document to fill (e.g. passage-card)")
    ap.add_argument("data", type=Path, nargs="?",
                    help="JSON file with the document data")
    ap.add_argument("-o", "--output", type=Path, help="output PDF path")
    ap.add_argument("--keep-editable", action="store_true",
                    help="do not flatten; keep the form interactive")
    ap.add_argument("-l", "--list", action="store_true", dest="list_documents",
                    help="list available documents and exit")
    ap.add_argument("--fields", action="store_true",
                    help="list the document's PDF field names and exit")
    ap.add_argument("--schema", action="store_true",
                    help="print the document's input JSON schema and exit")
    args = ap.parse_args()

    if args.list_documents or (args.document is None and not args.data):
        _print_documents()
        return

    try:
        spec = get_document(args.document)
    except KeyError as exc:
        sys.exit(exc.args[0])

    if args.schema:
        print(json.dumps(spec.model.model_json_schema(), indent=2, ensure_ascii=False))
        return

    if not spec.template_built:
        sys.exit(f"Template not built: {spec.template}\nRun `uv run build-docs` first.")

    if args.fields:
        print("\n".join(list_fields(spec.template)))
        return

    if args.data is None or args.output is None:
        ap.error("a DATA json file and -o/--output are required to fill a document")

    data = json.loads(args.data.read_text(encoding="utf-8"))
    try:
        report = fill_document(spec, data, args.output, flatten=not args.keep_editable)
    except ValidationError as exc:
        errors = "\n".join(
            f"  - {'.'.join(str(p) for p in e['loc']) or '(root)'}: {e['msg']}"
            for e in exc.errors()
        )
        sys.exit(f"Invalid {spec.name} data in {args.data}:\n{errors}")

    mode = "editable" if args.keep_editable else "flattened"
    print(f"Wrote {args.output}  ({len(report['applied'])} field(s) filled, {mode})")
