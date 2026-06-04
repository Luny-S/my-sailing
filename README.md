# my-sailing

LaTeX document templates for sailing — Polish/English.  
Based on PZZ (Polski Związek Żeglarski) forms and practical sailing use.

## Documents

| Folder | Document | Zones |
|--------|----------|-------|
| `karta-rejsu/` | Karta rejsu (PZZ sailing card) | Baltic, Mediterranean, Inland |
| `opinia-z-rejsu/` | Opinia z rejsu (PZZ post-trip assessment) | universal |
| `safety-briefing/` | Safety briefing / Odprawa bezpieczenstwa | Baltic, Mediterranean, Inland |
| `dziennik-jachtu/` | Dziennik jachtu / Yacht log | universal |
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
pdflatex safety_briefing_baltyk.tex
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

## Project structure

```
my-sailing/
├── pyproject.toml          # Python project (uv / hatchling)
├── Dockerfile              # Multi-stage: uv + texlive
├── src/
│   └── my_sailing/
│       └── build.py        # PDF build script (pdflatex wrapper)
└── documents/
    ├── shared/
    │   └── preamble.tex    # Shared LaTeX preamble (\input'd by every doc)
    ├── karta-rejsu/
    ├── opinia-z-rejsu/
    ├── safety-briefing/
    ├── dziennik-jachtu/
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

# Or compile a specific file directly
pdflatex -output-directory=build/karta-rejsu documents/karta-rejsu/karta_rejsu_baltyk.tex
```
