# Presentation deck build (PPTX → PDF)

London's Calling deck files live in this directory. A PPTX is an OOXML zip: unpack, edit slide XML and media, then repack and export PDF.

## Layout

```
docs/presentation/
  build-presentation.sh   # unpack / build / templates / apply
  README.md
  py/                     # slide generator scripts
  templateslides/         # named slide XML templates (by layout style)
  *.pptx                  # built deck
  *.pdf                   # built export
  screenshots/            # UI captures for demo slides
  src/                    # unpacked OOXML (after unpack)
```

## Prerequisites

- **LibreOffice** (`soffice` on PATH, or `brew install --cask libreoffice`)
- `unzip`, `zip`

## Workflow

```bash
cd docs/presentation

# Explode .pptx → src/ (replaces src/ each run)
./build-presentation.sh unpack

# Edit:
#   src/ppt/slides/slide1.xml, slide2.xml, ...
#   src/ppt/media/
#   src/ppt/notesSlides/

# Zip src/ → .pptx, then .pptx → .pdf
./build-presentation.sh build
```

After editing in PowerPoint, run `unpack` again to refresh `src/` from the saved `.pptx`.

## Diagrams (SVG source, PNG in deck)

Author diagrams as SVG under `diagrams/`. On `build`, `embed-diagrams.sh` rasterizes them to `src/ppt/media/diagram-<name>.png` (PPTX/LO do not reliably embed raw SVG in this workflow).

```bash
# Edit source
diagrams/soql-dataset-access-today.svg  # slide 2 - OFFSET/LIMIT vs chunk processing
diagrams/cursor-rdbms-overview.svg      # slide 3 - SQL cursor
diagrams/cursor-soql-overview.svg       # slide 4 - SOQL / Apex cursor

# Rasterize only
./build-presentation.sh diagrams

# Full build (diagrams + pptx + pdf)
./build-presentation.sh build
```

Requires `rsvg-convert` (`brew install librsvg`).

## Slide generator scripts (`py/`)

| Script | Slide(s) |
|--------|----------|
| `py/update-usecases-slide.py` | 5 — Use cases |
| `py/update-highlights-slide.py` | 7, 9, 11 — Demo highlights |
| `py/update-limits-slide.py` | 12 — Limits table |
| `py/update-tips-slide.py` | 13 — Tips & Tricks |
| `py/restructure-outline.py` | Rebuild deck outline (one-off) |
| `py/add-dataset-access-slide.py` | 2 — Dataset access diagram |
| `py/insert-sql-slide-at-3.py` | 3–4 — Cursor overview diagrams |
| `py/insert-slide.py` | Generic slide insert helper |

Run from `docs/presentation/` (scripts resolve paths relative to that directory).

## Demo screenshots

UI captures live under `screenshots/` and are copied into `src/ppt/media/` for embedding (e.g. `demo1-virtual-datatable.png` slide 6, `demo2-reporting-drilldown.png` slide 8, `demo3-adaptive-async.png` slide 10).

## Tips and Tricks slide

Regenerate the 2×3 tip card grid (slide 13):

```bash
python3 py/update-tips-slide.py && ./build-presentation.sh build
```

Edit `TIPS` in `py/update-tips-slide.py` (emoji, title, body, card colours).

## Demo Highlights slides

Regenerate highlights slides (3 shadow code boxes + bullet panel):

```bash
python3 py/update-highlights-slide.py        # all demos
python3 py/update-highlights-slide.py 1      # Demo 1 only (slide 7)
python3 py/update-highlights-slide.py 2 3    # Demo 2 + 3 (slides 9, 11)
python3 py/update-highlights-slide.py && ./build-presentation.sh build
```

Edit `DEMOS` in `py/update-highlights-slide.py` (code snippets and bullets per demo).

## Limits slide

Regenerate the 3-column limits table (slide 12):

```bash
python3 py/update-limits-slide.py && ./build-presentation.sh build
```

Edit `LIMIT_ROWS` and `INFO_NOTES` in `py/update-limits-slide.py`.

## Template slides

Layout templates live in `templateslides/`, named by style (from the slide title). See `templateslides/INDEX.md` for the catalog.

```bash
./build-presentation.sh list-templates
./build-presentation.sh apply basic-layout 5    # copy template -> src/ppt/slides/slide5.xml
./build-presentation.sh templates               # refresh templates from src after edits
```

## Commands

| Command | Action |
|---------|--------|
| `unpack` | Extract `.pptx` → `src/` |
| `build` | Zip `src/` → `.pptx`, then `.pptx` → `.pdf` |
| `all` | `unpack` then `build` |
| `templates` | Copy current `src` slides into `templateslides/` |
| `apply <tpl> <n>` | Copy `templateslides/<tpl>.xml` → `slide<n>.xml` |
| `list-templates` | List template base names |

## Custom deck name

```bash
DECK_BASENAME="My Deck Title" ./build-presentation.sh build
```

## XML editing tips

- Prefer small edits (text in `<a:t>` nodes). Broken XML or relationship IDs break the deck.
- Slide order lives in `ppt/presentation.xml` and `_rels` — do not rename slide files without updating relationships.
- Open the rebuilt `.pptx` in PowerPoint or Keynote after large structural changes.
