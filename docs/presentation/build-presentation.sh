#!/usr/bin/env bash
# Unpack PPTX (OOXML zip) for editing, repack to .pptx, export PDF via LibreOffice.
set -euo pipefail

PRES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "${DECK_BASENAME:-}" ]]; then
  DECK_BASENAME="lc26-apex-cursors"
fi
PPTX="${PRES_DIR}/${DECK_BASENAME}.pptx"
PDF="${PRES_DIR}/${DECK_BASENAME}.pdf"
SRC="${PRES_DIR}/src"
SLIDES="${SRC}/ppt/slides"
TEMPLATES="${PRES_DIR}/templateslides"
SOFFICE="${SOFFICE:-}"

usage() {
  cat <<'EOF'
Usage: build-presentation.sh <command>

Commands:
  unpack           Extract .pptx into src/ for XML/media editing
  build            Rasterize diagrams/*.svg, zip src/ -> .pptx, -> .pdf
  diagrams         Convert diagrams/*.svg to src/ppt/media/*.png only
  all              unpack then build (refreshes src/ from current .pptx)
  templates        Refresh templateslides/ from src/ppt/slides/
  apply <tpl> <n>  Copy templateslides/<tpl>.xml -> src/ppt/slides/slide<n>.xml
  list-templates   List available template slide files

Environment:
  DECK_BASENAME   Deck file name without extension
  SOFFICE         Path to LibreOffice soffice (auto-detected if unset)

Edit slides under: src/ppt/slides/
Template catalog: templateslides/INDEX.md
EOF
}

require_pptx() {
  if [[ ! -f "$PPTX" ]]; then
    echo "error: missing source PPTX: $PPTX" >&2
    echo "Place the deck in this directory or set DECK_BASENAME." >&2
    exit 1
  fi
}

find_soffice() {
  if [[ -n "$SOFFICE" && -x "$SOFFICE" ]]; then
    return 0
  fi
  local candidate
  for candidate in /opt/homebrew/bin/soffice /usr/local/bin/soffice soffice; do
    if command -v "$candidate" >/dev/null 2>&1; then
      SOFFICE="$(command -v "$candidate")"
      return 0
    fi
  done
  echo "error: LibreOffice soffice not found. Install LibreOffice or set SOFFICE." >&2
  exit 1
}

cmd_unpack() {
  require_pptx
  echo "Unpacking -> ${SRC}/"
  rm -rf "$SRC"
  mkdir -p "$SRC"
  unzip -q "$PPTX" -d "$SRC"
  echo "Done. Edit slide XML in: ${SRC}/ppt/slides/"
}

cmd_embed_diagrams() {
  if [[ -x "${PRES_DIR}/embed-diagrams.sh" ]]; then
    "${PRES_DIR}/embed-diagrams.sh"
  fi
}

cmd_zip_pptx() {
  if [[ ! -d "$SRC" ]]; then
    echo "error: ${SRC}/ does not exist. Run: $(basename "$0") unpack" >&2
    exit 1
  fi
  if [[ ! -f "${SRC}/[Content_Types].xml" ]]; then
    echo "error: ${SRC}/ does not look like an unpacked PPTX (missing [Content_Types].xml)" >&2
    exit 1
  fi

  local tmp_pptx
  tmp_pptx="${TMPDIR:-/tmp}/deck-build-$$.pptx"
  rm -f "$tmp_pptx"

  echo "Packing src/ -> ${PPTX##*/}"
  (
    cd "$SRC"
    find . -name '.DS_Store' -delete
    zip -qrX "$tmp_pptx" .
  )
  mv "$tmp_pptx" "$PPTX"
}

cmd_pdf() {
  find_soffice
  echo "Converting -> ${PDF##*/}"
  "$SOFFICE" --headless --convert-to pdf --outdir "$PRES_DIR" "$PPTX" >/dev/null
  if [[ ! -f "$PDF" ]]; then
    echo "error: PDF was not created at $PDF" >&2
    exit 1
  fi
  echo "PDF: $PDF"
}

cmd_build() {
  cmd_embed_diagrams
  cmd_zip_pptx
  cmd_pdf
  echo "Build complete."
}

cmd_all() {
  cmd_unpack
  cmd_build
}

cmd_templates() {
  if [[ ! -d "$SLIDES" ]]; then
    echo "error: ${SLIDES}/ missing. Run unpack first." >&2
    exit 1
  fi
  mkdir -p "$TEMPLATES"
  cp "$SLIDES/slide1.xml"  "$TEMPLATES/title-slide.xml"
  cp "$SLIDES/slide2.xml"  "$TEMPLATES/basic-layout.xml"
  cp "$SLIDES/slide3.xml"  "$TEMPLATES/basic-2-layout.xml"
  cp "$SLIDES/slide4.xml"  "$TEMPLATES/2-column-layout.xml"
  cp "$SLIDES/slide5.xml"  "$TEMPLATES/3-column-layout.xml"
  cp "$SLIDES/slide6.xml"  "$TEMPLATES/third-split-large-left.xml"
  cp "$SLIDES/slide7.xml"  "$TEMPLATES/third-split-large-right.xml"
  cp "$SLIDES/slide8.xml"  "$TEMPLATES/4-column.xml"
  cp "$SLIDES/slide9.xml"  "$TEMPLATES/4-column-multi.xml"
  cp "$SLIDES/slide10.xml" "$TEMPLATES/qa.xml"
  cp "$SLIDES/slide11.xml" "$TEMPLATES/thank-you.xml"
  echo "Updated templateslides/ (11 templates). See templateslides/INDEX.md"
}

normalize_template() {
  local name="$1"
  name="${name%.xml}"
  echo "$name"
}

normalize_slide_num() {
  local target="$1"
  target="${target#slide}"
  target="${target%.xml}"
  if [[ ! "$target" =~ ^[0-9]+$ ]]; then
    echo "error: slide target must be a number or slideN (got: $1)" >&2
    exit 1
  fi
  echo "$target"
}

cmd_list_templates() {
  if [[ ! -d "$TEMPLATES" ]]; then
    echo "error: ${TEMPLATES}/ missing. Run templates first." >&2
    exit 1
  fi
  ls -1 "$TEMPLATES"/*.xml 2>/dev/null | while read -r f; do
    basename "$f" .xml
  done
}

cmd_apply() {
  local tpl target src_file dest
  tpl="$(normalize_template "${1:-}")"
  target="$(normalize_slide_num "${2:-}")"
  if [[ -z "$tpl" || -z "$target" ]]; then
    echo "error: usage: $(basename "$0") apply <template> <slide-number>" >&2
    echo "example: $(basename "$0") apply basic-layout 12" >&2
    exit 1
  fi
  if [[ ! -d "$SLIDES" ]]; then
    echo "error: ${SLIDES}/ missing. Run unpack first." >&2
    exit 1
  fi
  src_file="${TEMPLATES}/${tpl}.xml"
  if [[ ! -f "$src_file" ]]; then
    echo "error: template not found: $src_file" >&2
    echo "Run: $(basename "$0") list-templates" >&2
    exit 1
  fi
  dest="${SLIDES}/slide${target}.xml"
  cp "$src_file" "$dest"
  echo "Applied ${tpl}.xml -> ${dest}"
  echo "Run build after editing content (and presentation.xml if this is a new slide)."
}

main() {
  local cmd="${1:-}"
  case "$cmd" in
    unpack) cmd_unpack ;;
    build) cmd_build ;;
    diagrams) cmd_embed_diagrams ;;
    all) cmd_all ;;
    templates) cmd_templates ;;
    apply) shift; cmd_apply "$@" ;;
    list-templates) cmd_list_templates ;;
    -h|--help|help|'') usage; [[ -z "$cmd" ]] && exit 0 ;;
    *)
      echo "error: unknown command: $cmd" >&2
      usage >&2
      exit 1
      ;;
  esac
}

main "$@"
