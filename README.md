# my-sailing

LaTeX document templates for sailing — Polish/English.  
Based on PZZ (Polski Związek Żeglarski) forms and practical sailing use.

## Documents

| Folder | Document | Zones |
|--------|----------|-------|
| `passage-card/` | Karta rejsu (PZZ sailing card) | Baltic, Mediterranean, Inland |
| `crew-opinion/` | Opinia z rejsu (PZZ post-trip assessment) | universal |
| `safety-briefing/` | Safety briefing / Odprawa bezpieczenstwa | Baltic, Mediterranean, Inland |
| `yacht-log/` | Dziennik jachtu / Yacht log | universal |
| `yacht-check-in/` | Przyjecie / zdanie jachtu (check-in/out form) | universal |
| `shopping-list/` | Lista zakupow / Shopping list | Baltic, Mediterranean, Inland |
| `packing-list/` | Lista pakownia / Packing list | Baltic, Mediterranean, Inland |

Shared LaTeX preamble lives in `documents/shared/preamble.tex`.

---

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- Python 3.13 (uv manages this automatically)
- A LaTeX distribution with Polish support, e.g.:
  - **Linux**: `sudo apt install texlive-latex-extra texlive-lang-polish`
  - **macOS**: MacTeX (`brew install --cask mactex`) or BasicTeX + packages
  - **Docker**: see below — no local LaTeX needed

---

## Quick start with uv

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and enter the repo
git clone <repo-url>
cd my-sailing

# Install Python dependencies and create virtualenv
uv sync

# Compile all documents to build/
uv run build-docs
```

PDFs are written to `build/<document-folder>/`.

### Compile a single document manually

```bash
cd documents/safety-briefing
pdflatex safety_briefing_baltic.tex
```

---

## Docker (no local LaTeX required)

Build the image:

```bash
docker build -t my-sailing .
```

Compile all documents (mounts `build/` into the container):

```bash
docker run --rm -v "$(pwd)/build:/app/build" my-sailing
```

---

## Pre-filling forms (karta rejsu)

`passage-card` is a fillable PDF form (real AcroForm fields). You can pre-fill it
from a JSON file and get a flattened, ready-to-print PDF. The JSON is validated
against a [pydantic model](src/my_sailing/models/passage_card.py); an internal
adapter maps it to the PDF's field names. Polish diacritics are rendered with
Latin Modern (the document's own typeface).

```bash
# Build the form first, then fill it
uv run build-docs

# See which documents can be filled
uv run fill-doc --list

# Generate an empty data template (keys, no values) for a document
uv run fill-doc passage-card --blank > data/passage_card.json

# Fill from JSON and flatten (default)
uv run fill-doc passage-card examples/passage_card.json -o tmp/karta.pdf

# Keep it interactive instead of flattening
uv run fill-doc passage-card examples/passage_card.json -o tmp/karta.pdf --keep-editable

# Inspect the input shape / underlying field names
uv run fill-doc passage-card --schema
uv run fill-doc passage-card --fields
```

Crew is a list of objects (`Lp.` is auto-numbered); the first six fill the
left on-page table, the next six the right. See [examples/passage_card.json](examples/passage_card.json).

You can also call it from Python:

```python
import json
from my_sailing.fill import fill_document
from my_sailing.models import get_document

spec = get_document("passage-card")
data = json.loads(open("examples/passage_card.json").read())
fill_document(spec, data, "tmp/karta.pdf")            # flatten=True by default
```

---

## Project structure

```
my-sailing/
├── pyproject.toml          # Python project (uv / hatchling)
├── Dockerfile              # uv + texlive (+ git)
├── examples/
│   └── passage_card.json   # sample data for the passage card form
├── src/
│   └── my_sailing/
│       ├── build.py        # compile all documents/*.tex -> build/
│       ├── fill.py         # fill + flatten a form PDF from JSON
│       └── models/         # pydantic models + document registry
│           ├── base.py
│           └── passage_card.py
└── documents/
    ├── shared/
    │   ├── preamble.tex    # shared LaTeX preamble (\input'd by every doc)
    │   └── assets/         # logos / images (e.g. pzz-logo.png)
    ├── passage-card/        # fillable PZŻ voyage card (PL + EN)
    ├── crew-opinion/
    ├── safety-briefing/
    ├── yacht-log/
    ├── yacht-check-in/
    ├── shopping-list/
    └── packing-list/
```

---

## Adding a new document

1. Create a folder under `documents/`.
2. Start your `.tex` file with `\input{../shared/preamble}` (adjust relative path if nested deeper).
3. Run `uv run build-docs` — it discovers all `.tex` files automatically.

---

## Development

```bash
# Run the builder in watch-like fashion (re-run manually after edits)
uv run build-docs

# Or compile a single file directly (run from its folder so \input resolves)
cd documents/passage-card && latexmk -pdf -cd passage_card.tex
```
