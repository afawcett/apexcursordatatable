# Slide templates

Named copies of slide XML from the deck. The **style name** matches the title placeholder text (or slide role for title/Q&A/thank-you slides).

| Template file | Style / title | Source slide | Notes |
|---------------|---------------|--------------|-------|
| `title-slide.xml` | *(title slide)* | slide1 | Main headline + speaker info |
| `basic-layout.xml` | Basic Layout | slide2 | Title + body |
| `basic-2-layout.xml` | Basic 2 Layout | slide3 | Title + body (variant) |
| `2-column-layout.xml` | 2-Column Layout | slide4 | Two content placeholders |
| `3-column-layout.xml` | 3-Column Layout | slide5 | Three content placeholders |
| `third-split-large-left.xml` | Third Split | slide6 | Wide left, narrow right |
| `third-split-large-right.xml` | Third Split | slide7 | Narrow left, wide right |
| `4-column.xml` | 4 Column | slide8 | Four columns |
| `4-column-multi.xml` | 4 Column Multi | slide9 | Four columns (multi-row) |
| `qa.xml` | Q&A | slide10 | Q&A closing slide |
| `thank-you.xml` | Thank You | slide11 | Thank-you closing slide |

## Apply a template to the working deck

```bash
# Copy template into src/ppt/slides/ (then edit text and run build)
./build-presentation.sh apply basic-layout 12
./build-presentation.sh apply 2-column-layout slide5
```

You must also register the new slide in `src/ppt/presentation.xml` and add `_rels` entries — applying XML alone is not enough for a **new** slide. Replacing an existing `slideN.xml` is the simple case.

## Refresh templates from src

After editing slides in `src/`, update the library:

```bash
./build-presentation.sh templates
```
