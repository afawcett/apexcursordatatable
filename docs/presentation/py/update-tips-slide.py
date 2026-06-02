#!/usr/bin/env python3
"""Build slide 14: Other Use Cases — compact 2-column card grid with soft shadows."""
from __future__ import annotations

import html
import math
from pathlib import Path

PRES = Path(__file__).resolve().parent.parent
SLIDE = PRES / "src/ppt/slides/slide14.xml"

TITLE = "Other Use Cases"
SUBTITLE = "Cursor patterns beyond the three demos"

USE_CASES = [
    {
        "emoji": "☑️",
        "title": "Records to Process Adjustment",
        "body": (
            "Present records to process and let users deselect rows. "
            "Pass the cursor and row indexes to ignore into the job."
        ),
        "bg": "F4F7FC",
        "accent": "4A6FA5",
    },
    {
        "emoji": "🔁",
        "title": "Repeatable Datasets",
        "body": "Retry processing against the exact original record set.",
        "bg": "F3FAF4",
        "accent": "5A7A3A",
    },
    {
        "emoji": "📸",
        "title": "Point in Time Reporting",
        "body": "Snapshot a record-set selection for the user session.",
        "bg": "FFF9F2",
        "accent": "C47A20",
    },
    {
        "emoji": "📋",
        "title": "Simple Queue",
        "body": (
            "Create task records and delete when complete — "
            "until cursor rows reach zero."
        ),
        "bg": "F0F6FF",
        "accent": "2E6DB4",
    },
]

SLIDE_CY = 6_858_000
MARGIN_X = 338_325
GRID_W = 11_484_900
SUBTITLE_Y = 995_000
SUBTITLE_H = 150_000
HEADER_GAP = 100_000
BOTTOM_MARGIN = 250_000
COL_GAP = 160_000
ROW_GAP = 130_000
CARD_W = (GRID_W - COL_GAP) // 2
CARD_H = 1_120_000
GRID_ROWS = math.ceil(len(USE_CASES) / 2)
GRID_H = GRID_ROWS * CARD_H + (GRID_ROWS - 1) * ROW_GAP
CONTENT_TOP = SUBTITLE_Y + SUBTITLE_H + HEADER_GAP
CONTENT_BOTTOM = SLIDE_CY - BOTTOM_MARGIN
GRID_Y = CONTENT_TOP + (CONTENT_BOTTOM - CONTENT_TOP - GRID_H) // 2
PAD = 85_000
EMOJI_COL_W = 520_000
EMOJI_SIZE = 340_000
CONTENT_W = CARD_W - EMOJI_COL_W - PAD
CONTENT_H = CARD_H - 2 * PAD
ROUND_ADJ = 8000

CARD_SHADOW = (
    '<a:effectLst><a:outerShdw blurRad="50800" dist="31750" dir="2700000" '
    'algn="ctr" rotWithShape="0"><a:srgbClr val="000000">'
    "<a:alpha val=\"28000\"/></a:srgbClr></a:outerShdw></a:effectLst>"
)


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def card_bg(shape_id: int, x: int, y: int, bg: str) -> str:
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="usecase-card-bg-{shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{CARD_W}" cy="{CARD_H}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {ROUND_ADJ}"/></a:avLst></a:prstGeom><a:solidFill><a:srgbClr val="{bg}"/></a:solidFill><a:ln><a:noFill/></a:ln>{CARD_SHADOW}</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody></p:sp>"""


def card_emoji(shape_id: int, x: int, y: int, emoji: str) -> str:
    ex = x + (EMOJI_COL_W - EMOJI_SIZE) // 2
    ey = y + (CARD_H - EMOJI_SIZE) // 2
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="usecase-emoji-{shape_id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{ex}" y="{ey}"/><a:ext cx="{EMOJI_SIZE}" cy="{EMOJI_SIZE}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr anchor="ctr" anchorCtr="1" wrap="none"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="ctr"><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="3200"/><a:t>{esc(emoji)}</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp>"""


def card_content(shape_id: int, x: int, y: int, item: dict) -> str:
    cx = x + EMOJI_COL_W
    cy = y + PAD
    t = esc(item["title"])
    b = esc(item["body"])
    accent = item["accent"]
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="usecase-content-{shape_id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{cx}" y="{cy}"/><a:ext cx="{CONTENT_W}" cy="{CONTENT_H}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr anchor="t" anchorCtr="0" wrap="square" lIns="27432" rIns="27432" tIns="0" bIns="0"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr marL="0" indent="0" algn="l"><a:lnSpc><a:spcPct val="105000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="80"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="1650" b="1"><a:solidFill><a:srgbClr val="{accent}"/></a:solidFill></a:rPr><a:t>{t}</a:t></a:r><a:endParaRPr/></a:p><a:p><a:pPr marL="0" indent="0" algn="l"><a:lnSpc><a:spcPct val="115000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="1500"><a:solidFill><a:srgbClr val="444444"/></a:solidFill></a:rPr><a:t>{b}</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp>"""


def use_case_cards_xml() -> str:
    parts: list[str] = []
    sid = 201
    for i, item in enumerate(USE_CASES):
        col = i % 2
        row = i // 2
        x = MARGIN_X + col * (CARD_W + COL_GAP)
        y = GRID_Y + row * (CARD_H + ROW_GAP)
        parts.append(card_bg(sid, x, y, item["bg"]))
        sid += 1
        parts.append(card_emoji(sid, x, y, item["emoji"]))
        sid += 1
        parts.append(card_content(sid, x, y, item))
        sid += 1
    return "\n".join(parts)


def build_slide() -> str:
    title_esc = esc(TITLE)
    sub_esc = esc(SUBTITLE)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:mv="urn:schemas-microsoft-com:mac:vml" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:dgm="http://schemas.openxmlformats.org/drawingml/2006/diagram" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:pvml="urn:schemas-microsoft-com:office:powerpoint" xmlns:com="http://schemas.openxmlformats.org/drawingml/2006/compatibility" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" xmlns:p15="http://schemas.microsoft.com/office/powerpoint/2012/main" xmlns:ahyp="http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="114" name="Shape 114"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
{use_case_cards_xml()}
<p:sp><p:nvSpPr><p:cNvPr id="118" name="usecases-subtitle"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="338325" y="{SUBTITLE_Y}"/><a:ext cx="11484900" cy="150000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr anchor="t" wrap="square"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="l"><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="1500" i="1"><a:solidFill><a:srgbClr val="666666"/></a:solidFill></a:rPr><a:t>{sub_esc}</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="116" name="Google Shape;116;p14"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="338327" y="90720"/><a:ext cx="11515500" cy="908100"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr anchorCtr="0" anchor="b" bIns="0" lIns="0" spcFirstLastPara="1" rIns="0" wrap="square" tIns="0"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buClr><a:srgbClr val="891019"/></a:buClr><a:buSzPts val="3200"/><a:buFont typeface="Arial"/><a:buNone/></a:pPr><a:r><a:rPr lang="en-US"/><a:t>{title_esc}</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr><mc:AlternateContent><mc:Choice Requires="p14"><p:transition spd="slow" p14:dur="700"><p:fade/></p:transition></mc:Choice><mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent></p:sld>
"""


def main() -> None:
    SLIDE.write_text(build_slide())
    print(f"Wrote {SLIDE} ({len(USE_CASES)} cards, {GRID_ROWS} rows)")


if __name__ == "__main__":
    main()
