"""render-voyage — render all documents from a single VoyageRecord JSON.

Usage examples::

    # Write an empty template you can fill in
    render-voyage --template -o data/voyage.json

    # Render all documents to output/
    render-voyage voyage.json -o output/

    # Render one specific document
    render-voyage voyage.json --doc passage-card -o passage_card.pdf

    # Write individual sub-JSON files instead of PDFs
    render-voyage voyage.json --split -o data/

    # List which documents would be produced
    render-voyage voyage.json --list
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from .models import DOCUMENTS, get_document
from .models.voyage import VoyageRecord
from .render import render_document


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="render-voyage",
        description="Render all documents from a single VoyageRecord JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument(
        "--template", action="store_true",
        help="write an empty voyage JSON template and exit (use with -o)",
    )
    ap.add_argument("voyage", type=Path, nargs="?", help="voyage JSON file (VoyageRecord)")
    ap.add_argument(
        "--doc", metavar="NAME",
        help="render only this document (default: all)",
    )
    ap.add_argument(
        "-o", "--output", type=Path, metavar="PATH",
        help="output directory (all docs) or output file (--doc); required unless --list",
    )
    ap.add_argument(
        "--split", action="store_true",
        help="write individual JSON files instead of PDFs",
    )
    ap.add_argument(
        "--list", action="store_true", dest="list_docs",
        help="list document names and their data keys, then exit",
    )
    args = ap.parse_args()

    # --- --template mode ---
    if args.template:
        from .models.voyage import VoyageCrewMember, VoyageCaptain, VoyageCruise, VoyageYacht
        template = VoyageRecord(crew=[VoyageCrewMember()])
        text = template.model_dump_json(indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
            print(f"Wrote {args.output}")
        else:
            print(text)
        return

    if args.voyage is None:
        ap.error("voyage file is required (or use --template to generate one)")

    # --- Load and validate VoyageRecord ---
    try:
        raw = args.voyage.read_text(encoding="utf-8")
    except FileNotFoundError:
        sys.exit(f"File not found: {args.voyage}")

    try:
        record = VoyageRecord.model_validate(json.loads(raw))
    except ValidationError as exc:
        errors = "\n".join(
            f"  - {'.'.join(str(p) for p in e['loc']) or '(root)'}: {e['msg']}"
            for e in exc.errors()
        )
        sys.exit(f"Invalid voyage JSON in {args.voyage}:\n{errors}")

    docs = record.split()

    # --- --list mode ---
    if args.list_docs:
        print(f"VoyageRecord from {args.voyage}\n")
        for name, data in docs.items():
            spec = DOCUMENTS.get(name)
            title = spec.title if spec else name
            keys = ", ".join(sorted(data)) or "(no data)"
            print(f"  {name:<18} {title}")
            print(f"  {'':18} fields: {keys}\n")
        return

    if args.output is None:
        ap.error("-o/--output is required")

    # --- Filter to a single doc if requested ---
    if args.doc:
        try:
            get_document(args.doc)
        except KeyError as exc:
            sys.exit(exc.args[0])
        docs = {args.doc: docs[args.doc]}

    # --- --split mode: write JSON files ---
    if args.split:
        out_dir: Path = args.output
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, data in docs.items():
            dest = out_dir / f"{name.replace('-', '_')}.json"
            dest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Wrote {dest}")
        return

    # --- PDF render mode ---
    if args.doc:
        # Single doc → output is a file path
        out_path: Path = args.output
        name, data = next(iter(docs.items()))
        spec = get_document(name)
        try:
            render_document(spec, data, out_path)
        except ValidationError as exc:
            errors = "\n".join(
                f"  - {'.'.join(str(p) for p in e['loc']) or '(root)'}: {e['msg']}"
                for e in exc.errors()
            )
            sys.exit(f"Data error for {name}:\n{errors}")
        print(f"Wrote {out_path}")
    else:
        # All docs → output is a directory
        out_dir = args.output
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, data in docs.items():
            spec = get_document(name)
            dest = out_dir / f"{name.replace('-', '_')}.pdf"
            try:
                render_document(spec, data, dest)
                print(f"Wrote {dest}")
            except ValidationError as exc:
                errors = "\n".join(
                    f"  - {'.'.join(str(p) for p in e['loc']) or '(root)'}: {e['msg']}"
                    for e in exc.errors()
                )
                print(f"SKIP {name}: data error\n{errors}", file=sys.stderr)
