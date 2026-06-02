#!/usr/bin/env python3
"""Build slide 12: Usage Best Practices — 3×2 code sample grid."""
from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

PRES = Path(__file__).resolve().parent.parent
SRC = PRES / "src"
SLIDES = SRC / "ppt/slides"
SLIDE_RELS = SLIDES / "_rels"
NOTES = SRC / "ppt/notesSlides"
NOTES_RELS = NOTES / "_rels"

SLIDE_NUM = 12
TITLE = "Usage Best Practices"

# Six API usage patterns with fragments from this repo
PRACTICES: list[dict] = [
    {
        "label": "Stable ORDER BY",
        "prompt": "soql>",
        "lines": [
            [("'SELECT ... FROM Account ", "CE9178")],
            [("  WHERE Name LIKE 'TEST%'", "CE9178")],
            [("  ORDER BY Name',", "CE9178")],
            [("  AccessLevel.USER_MODE);", "CE9178")],
        ],
        "notes": [
            "Sort on a unique, stable key.",
            "Keeps offsets and page indexes predictable.",
        ],
    },
    {
        "label": "Guard number of records",
        "lines": [
            [
                ("if (cursor.getNumRecords()", "DCDCAA"),
                (" == ", "D4D4D4"),
                ("0", "CE9178"),
                (") {", "D4D4D4"),
            ],
            [
                ("  ", "D4D4D4"),
                ("return", "569CD6"),
                (" result;", "D4D4D4"),
            ],
            [("}", "D4D4D4")],
        ],
        "notes": [
            "Exit early when the result set is empty.",
            "fetch(0, 0) can throw a GACK.",
        ],
    },
    {
        "label": "Cap fetchPage size",
        "lines": [
            [("pageSize = Math.min(", "DCDCAA")],
            [("  PAGE_SIZE,", "CE9178")],
            [("  pc.getNumRecords()", "DCDCAA")],
            [("    - startIndex);", "CE9178")],
            [("pc.fetchPage(start, pageSize);", "DCDCAA")],
        ],
        "notes": [
            "Do not request rows past the result set end.",
            "Critical for partial last pages.",
        ],
    },
    {
        "label": "Retry transient errors",
        "lines": [
            [("} catch (System.", "569CD6")],
            [("  TransientCursorException e) {", "569CD6")],
            [("  if (++retries <= MAX)", "DCDCAA")],
            [("    return retry();", "CE9178")],
            [("  throw e;", "DCDCAA")],
        ],
        "notes": [
            "TransientCursorException may be retried.",
            "Do not retry FatalCursorException.",
        ],
    },
    {
        "label": "Cursor returns to LWC",
        "lines": [
            [("@AuraEnabled", "569CD6")],
            [("public static Result load(...) {", "DCDCAA")],
            [("  result.cursor = cursor;", "CE9178")],
            [("  return result;", "DCDCAA")],
            [("}", "569CD6")],
        ],
        "notes": [
            "Cursors are Aura-serializable.",
            "Return on @AuraEnabled result.",
        ],
    },
    {
        "label": "Check for latest security changes",
        "lines": [
            [
                ("[SELECT Id FROM Account", "CE9178"),
            ],
            [
                ("  WHERE Id IN :ids", "CE9178"),
            ],
            [
                ("  WITH USER_MODE];", "CE9178"),
            ],
            [
                ("cursor = Database.getCursor(", "DCDCAA"),
            ],
            [
                ("  soql, AccessLevel.USER_MODE);", "CE9178"),
            ],
        ],
        "notes": [
            "Fetch does not re-evaluate security, per Batch Apex. "
            "If critical requery changes.",
        ],
    },
]

SLIDE_CY = 6_858_000
MARGIN_X = 338_325
FULL_W = 11_484_900
TITLE_BOTTOM = 999_000
BOTTOM_MARGIN = 200_000
HEADER_GAP = 85_000
COLS = 3
ROWS = 2
COL_GAP = 95_000
ROW_GAP = 85_000
CELL_W = (FULL_W - (COLS - 1) * COL_GAP) // COLS
LABEL_H = 260_000
CODE_H = 920_000
INFO_GAP = 40_000
INFO_H = 580_000
INFO_PAD = 42_000
INFO_FONT_SZ = 1280
CODE_FONT_SZ = 1150
CODE_PAD_T = 38_000
CODE_PAD_B = 75_000
CODE_PAD_LR = 50_000
ROUND_ADJ = 5000
CELL_BLOCK_H = LABEL_H + CODE_H + INFO_GAP + INFO_H

GRID_H = ROWS * CELL_BLOCK_H + (ROWS - 1) * ROW_GAP
_CONTENT_TOP = TITLE_BOTTOM + HEADER_GAP
_CONTENT_BOTTOM = SLIDE_CY - BOTTOM_MARGIN
GRID_Y = _CONTENT_TOP + (_CONTENT_BOTTOM - _CONTENT_TOP - GRID_H) // 2

CARD_SHADOW = (
    '<a:effectLst><a:outerShdw blurRad="50800" dist="31750" dir="2700000" '
    'algn="ctr" rotWithShape="0"><a:srgbClr val="000000">'
    '<a:alpha val="28000"/></a:srgbClr></a:outerShdw></a:effectLst>'
)

SLIDE_RELS_STUB = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout2.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide{num}.xml"/></Relationships>
"""

NOTES_RELS_STUB = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/></Relationships>
"""


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def code_line_para(
    runs: list[tuple[str, str]], before_pts: str = "0", after_pts: str = "0"
) -> str:
    run_xml = "".join(
        f'<a:r><a:rPr lang="en-US" sz="{CODE_FONT_SZ}" typeface="Consolas">'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr>'
        f"<a:t>{esc(text)}</a:t></a:r>"
        for text, color in runs
    )
    return (
        f'<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l">'
        f'<a:lnSpc><a:spcPct val="98000"/></a:lnSpc>'
        f'<a:spcBef><a:spcPts val="{before_pts}"/></a:spcBef>'
        f'<a:spcAft><a:spcPts val="{after_pts}"/></a:spcAft><a:buNone/></a:pPr>'
        f"{run_xml}<a:endParaRPr/></a:p>"
    )


def terminal_body(
    lines: list[list[tuple[str, str]]], *, prompt: str = "apex>"
) -> str:
    parts = [code_line_para([(prompt, "6A9955")], "60")]
    for i, runs in enumerate(lines):
        is_last = i == len(lines) - 1
        parts.append(
            code_line_para(runs, "35" if i else "25", after_pts="120" if is_last else "0")
        )
    return "".join(parts)


def info_note_para(text: str, before_pts: str = "0", after_pts: str = "0") -> str:
    return f"""<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:lnSpc><a:spcPct val="108000"/></a:lnSpc><a:spcBef><a:spcPts val="{before_pts}"/></a:spcBef><a:spcAft><a:spcPts val="{after_pts}"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="{INFO_FONT_SZ}"><a:solidFill><a:srgbClr val="444444"/></a:solidFill></a:rPr><a:t>{esc(text)}</a:t></a:r><a:endParaRPr/></a:p>"""


def info_body(notes: list[str]) -> str:
    parts = []
    for i, note in enumerate(notes):
        is_last = i == len(notes) - 1
        parts.append(
            info_note_para(note, "180" if i == 0 else "100", after_pts="80" if is_last else "0")
        )
    return "".join(parts)


def info_box(shape_id: int, x: int, y: int, notes: list[str]) -> str:
    body = info_body(notes)
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="usage-info-{shape_id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{CELL_W}" cy="{INFO_H}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {ROUND_ADJ}"/></a:avLst></a:prstGeom><a:solidFill><a:srgbClr val="F4F7FC"/></a:solidFill><a:ln><a:noFill/></a:ln>{CARD_SHADOW}</p:spPr><p:txBody><a:bodyPr anchor="t" anchorCtr="0" wrap="square" lIns="{INFO_PAD}" rIns="{INFO_PAD}" tIns="{INFO_PAD}" bIns="{INFO_PAD}"><a:noAutofit/></a:bodyPr><a:lstStyle/>{body}</p:txBody></p:sp>"""


def label_shape(shape_id: int, x: int, y: int, text: str) -> str:
    t = esc(text)
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="usage-label-{shape_id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{CELL_W}" cy="{LABEL_H}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr anchor="b" anchorCtr="0" wrap="none"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="l"><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="1550" b="1"><a:solidFill><a:srgbClr val="891019"/></a:solidFill></a:rPr><a:t>{t}</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp>"""


def code_box(
    shape_id: int,
    x: int,
    y: int,
    lines: list[list[tuple[str, str]]],
    *,
    prompt: str = "apex>",
) -> str:
    body = terminal_body(lines, prompt=prompt)
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="usage-code-{shape_id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{CELL_W}" cy="{CODE_H}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {ROUND_ADJ}"/></a:avLst></a:prstGeom><a:solidFill><a:srgbClr val="1E1E1E"/></a:solidFill><a:ln><a:noFill/></a:ln>{CARD_SHADOW}</p:spPr><p:txBody><a:bodyPr anchor="t" anchorCtr="0" wrap="square" lIns="{CODE_PAD_LR}" rIns="{CODE_PAD_LR}" tIns="{CODE_PAD_T}" bIns="{CODE_PAD_B}"><a:noAutofit/></a:bodyPr><a:lstStyle/>{body}</p:txBody></p:sp>"""


def grid_xml() -> str:
    parts: list[str] = []
    sid = 201
    for idx, practice in enumerate(PRACTICES):
        col = idx % COLS
        row = idx // COLS
        x = MARGIN_X + col * (CELL_W + COL_GAP)
        y = GRID_Y + row * (CELL_BLOCK_H + ROW_GAP)
        parts.append(label_shape(sid, x, y, practice["label"]))
        sid += 1
        code_y = y + LABEL_H
        parts.append(
            code_box(
                sid,
                x,
                code_y,
                practice["lines"],
                prompt=practice.get("prompt", "apex>"),
            )
        )
        sid += 1
        info_y = code_y + CODE_H + INFO_GAP
        parts.append(info_box(sid, x, info_y, practice["notes"]))
        sid += 1
    return "\n".join(parts)


def title_shape() -> str:
    title_esc = esc(TITLE)
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="116" name="Google Shape;116;p14"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="338327" y="90720"/><a:ext cx="11515500" cy="908100"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr anchorCtr="0" anchor="b" bIns="0" lIns="0" spcFirstLastPara="1" rIns="0" wrap="square" tIns="0"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buClr><a:srgbClr val="891019"/></a:buClr><a:buSzPts val="3200"/><a:buFont typeface="Arial"/><a:buNone/></a:pPr><a:r><a:rPr lang="en-US"/><a:t>{title_esc}</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp>"""


def build_slide() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:mv="urn:schemas-microsoft-com:mac:vml" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:dgm="http://schemas.openxmlformats.org/drawingml/2006/diagram" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:pvml="urn:schemas-microsoft-com:office:powerpoint" xmlns:com="http://schemas.openxmlformats.org/drawingml/2006/compatibility" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" xmlns:p15="http://schemas.microsoft.com/office/powerpoint/2012/main" xmlns:ahyp="http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="114" name="Shape 114"/><p:cNvSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
{grid_xml()}
{title_shape()}
</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr><mc:AlternateContent><mc:Choice Requires="p14"><p:transition spd="slow" p14:dur="700"><p:fade/></p:transition></mc:Choice><mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent></p:sld>
"""


def count_slides() -> int:
    return len(list(SLIDES.glob("slide*.xml")))


def slide_title(num: int) -> str:
    path = SLIDES / f"slide{num}.xml"
    if not path.exists():
        return ""
    m = re.search(r"<p:ph type=\"title\"/>.*?<a:t>([^<]*)</a:t>", path.read_text(), re.DOTALL)
    return m.group(1) if m else ""


def insert_slide_at(position: int) -> None:
    n = count_slides()
    for i in range(n, position - 1, -1):
        for folder, prefix in ((SLIDES, "slide"), (NOTES, "notesSlide")):
            src_f = folder / f"{prefix}{i}.xml"
            dst_f = folder / f"{prefix}{i + 1}.xml"
            if src_f.exists():
                src_f.rename(dst_f)
        sr = SLIDE_RELS / f"slide{i}.xml.rels"
        if sr.exists():
            sr.rename(SLIDE_RELS / f"slide{i + 1}.xml.rels")
        nr = NOTES_RELS / f"notesSlide{i}.xml.rels"
        if nr.exists():
            nr.rename(NOTES_RELS / f"notesSlide{i + 1}.xml.rels")

    notes_tpl = PRES / "templateslides/_notesSlide2.xml"
    if not notes_tpl.exists():
        notes_tpl = NOTES / "notesSlide2.xml"
    shutil.copy(notes_tpl, NOTES / f"notesSlide{position}.xml")
    (SLIDE_RELS / f"slide{position}.xml.rels").write_text(
        SLIDE_RELS_STUB.format(num=position)
    )
    (NOTES_RELS / f"notesSlide{position}.xml.rels").write_text(NOTES_RELS_STUB)

    total = n + 1
    sld_ids = "\n".join(
        f'    <p:sldId id="{255 + i}" r:id="rId{5 + i}"/>'
        for i in range(1, total + 1)
    )
    (SRC / "ppt/presentation.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" autoCompressPictures="0" saveSubsetFonts="1"><p:sldMasterIdLst><p:sldMasterId id="2147483659" r:id="rId4"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rId5"/></p:notesMasterIdLst><p:sldIdLst>
{sld_ids}
</p:sldIdLst><p:sldSz cy="6858000" cx="12188825"/><p:notesSz cx="7010400" cy="9296400"/></p:presentation>
"""
    )
    fixed = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme2.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/><Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/><Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="notesMasters/notesMaster1.xml"/>"""
    slide_rels = "".join(
        f'<Relationship Id="rId{5 + i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, total + 1)
    )
    (SRC / "ppt/_rels/presentation.xml.rels").write_text(fixed + slide_rels + "</Relationships>\n")

    base = (SRC / "[Content_Types].xml").read_text()
    base = re.sub(
        r"<Override ContentType=\"application/vnd\.openxmlformats-officedocument\.presentationml\.slide\+xml\" PartName=\"/ppt/slides/slide\d+\.xml\"/>",
        "",
        base,
    )
    base = re.sub(
        r"<Override ContentType=\"application/vnd\.openxmlformats-officedocument\.presentationml\.notesSlide\+xml\" PartName=\"/ppt/notesSlides/notesSlide\d+\.xml\"/>",
        "",
        base,
    )
    inserts = ""
    for i in range(1, total + 1):
        inserts += f'<Override ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml" PartName="/ppt/slides/slide{i}.xml"/>'
        inserts += f'<Override ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml" PartName="/ppt/notesSlides/notesSlide{i}.xml"/>'
    base = base.replace("</Types>", inserts + "</Types>")
    (SRC / "[Content_Types].xml").write_text(base)
    print(f"Inserted slide slot at {position}; deck now has {total} slides.")


def ensure_slide_slot() -> None:
    path = SLIDES / f"slide{SLIDE_NUM}.xml"
    if path.exists():
        title = slide_title(SLIDE_NUM)
        if title == TITLE:
            return
        if title == "Limits":
            insert_slide_at(SLIDE_NUM)
            return
    raise SystemExit(f"slide{SLIDE_NUM} missing or unexpected title: {slide_title(SLIDE_NUM)!r}")


def main() -> None:
    ensure_slide_slot()
    out = SLIDES / f"slide{SLIDE_NUM}.xml"
    out.write_text(build_slide())
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
