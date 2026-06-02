# Presentation deck build (PPTX → PDF)

London's Calling deck files live in this directory. A PPTX is an OOXML zip: unpack, edit slide XML and media, then repack and export PDF.

## Layout

```
docs/presentation/
  build-presentation.sh   # unpack / build / templates / apply
  README.md
  py/                     # slide generator scripts
  templateslides/         # named slide XML templates (by layout style)
  lc26-apex-cursors.pptx  # built deck (default DECK_BASENAME)
  lc26-apex-cursors.pdf   # built export + landing page slides link
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

Rendering quality:

- Diagram rasterization defaults to `DIAGRAM_RASTER_DPI=288` and `DIAGRAM_RASTER_SCALE=2` for sharper on-slide text/lines.
- Override per build if needed, e.g. `DIAGRAM_RASTER_DPI=192 DIAGRAM_RASTER_SCALE=1 ./build-presentation.sh build`.

## Slide generator scripts (`py/`)

| Script | Slide(s) |
|--------|----------|
| `py/update-usecases-slide.py` | 5 — Use cases |
| `py/update-highlights-slide.py` | 7, 9, 11 — Demo summaries |
| `py/update-usage-best-practices-slide.py` | 12 — Usage Best Practices (3×2 code grid) |
| `py/update-limits-slide.py` | 13 — Limits table |
| `py/update-tips-slide.py` | 14 — Other Use Cases |
| `py/update-qa-slide.py` | 15 — Q&A + GitHub QR code |
| `py/restructure-outline.py` | Rebuild deck outline (one-off) |
| `py/add-dataset-access-slide.py` | 2 — Dataset access diagram |
| `py/insert-sql-slide-at-3.py` | 3–4 — Cursor overview diagrams |
| `py/insert-slide.py` | Generic slide insert helper |

Run from `docs/presentation/` (scripts resolve paths relative to that directory).

## Code sample color convention

Keep syntax highlighting consistent across all deck code samples:

- **Types/classes**: `569CD6` (blue)
- **Method calls**: `DCDCAA`
- **Literals/args**: `CE9178`
- **Neutral text/variables**: `D4D4D4`

`py/update-usecases-slide.py` defines these as `CODE_COLOR_*` constants; reuse this palette in other slide scripts.

## Usage Best Practices slide

Regenerate the 3×2 code sample grid (slide 12). Inserts a new slide slot on first run if Limits is still at slide 12:

```bash
python3 py/update-usage-best-practices-slide.py && ./build-presentation.sh build
```

Edit `PRACTICES` in `py/update-usage-best-practices-slide.py` (label + code lines per cell).

## Demo screenshots

UI captures live under `screenshots/` and are copied into `src/ppt/media/` for embedding (e.g. `demo1-virtual-datatable.png` slide 6, `demo2-reporting-drilldown.png` slide 8, `demo3-adaptive-async.png` slide 10).

For crisp screenshots, capture at higher resolution (recommended width `>= 1920px`) before copying into `screenshots/`.

## Other Use Cases slide

Regenerate the use-case card grid (slide 14; 2 columns, rows sized to `USE_CASES`):

```bash
python3 py/update-tips-slide.py && ./build-presentation.sh build
```

Edit `USE_CASES` in `py/update-tips-slide.py` (emoji, title, body, card colours).

## Demo summary slides

Regenerate demo summary slides (3 shadow code boxes + bullet panel):

```bash
python3 py/update-highlights-slide.py        # all demos
python3 py/update-highlights-slide.py 1      # Demo 1 only (slide 7)
python3 py/update-highlights-slide.py 2 3    # Demo 2 + 3 (slides 9, 11)
python3 py/update-highlights-slide.py && ./build-presentation.sh build
```

Edit `DEMOS` in `py/update-highlights-slide.py` (code snippets and bullets per demo).

## Limits slide

Regenerate the 3-column limits table (slide 13):

```bash
python3 py/update-limits-slide.py && ./build-presentation.sh build
```

Edit `LIMIT_SECTIONS` and `INFO_NOTES` in `py/update-limits-slide.py`.

## Q&A slide

Regenerate Q&A slide with GitHub repo QR code (slide 15). Requires `qrencode` (`brew install qrencode`):

```bash
python3 py/update-qa-slide.py && ./build-presentation.sh build
```

Set `GITHUB_URL` in `py/update-qa-slide.py` to change the encoded link.

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
