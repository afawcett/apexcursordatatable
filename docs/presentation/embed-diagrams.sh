#!/usr/bin/env bash
# Convert diagrams/*.svg -> src/ppt/media/*.png for PPTX embedding.
set -euo pipefail

PRES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIAGRAMS="${PRES_DIR}/diagrams"
MEDIA="${PRES_DIR}/src/ppt/media"
DPI="${DIAGRAM_RASTER_DPI:-144}"

if [[ ! -d "$DIAGRAMS" ]]; then
  exit 0
fi

if ! command -v rsvg-convert >/dev/null 2>&1; then
  echo "error: rsvg-convert not found (brew install librsvg)" >&2
  exit 1
fi

shopt -s nullglob
svgs=("$DIAGRAMS"/*.svg)
if [[ ${#svgs[@]} -eq 0 ]]; then
  exit 0
fi

mkdir -p "$MEDIA"
for svg in "${svgs[@]}"; do
  base="$(basename "$svg" .svg)"
  out="${MEDIA}/diagram-${base}.png"
  echo "diagram: ${svg##*/} -> ppt/media/$(basename "$out")"
  rsvg-convert -d "$DPI" -p "$DPI" -b white -o "$out" "$svg"
done
