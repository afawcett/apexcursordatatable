#!/usr/bin/env python3
"""Build slide 12: Limits — scoped 3-column table (Limit | Pagination | Standard)."""
from __future__ import annotations

import html
from pathlib import Path

PRES = Path(__file__).resolve().parent.parent
SLIDE = PRES / "src/ppt/slides/slide13.xml"

TITLE = "Limits"

# Scopes and max values from Salesforce Apex Cursor / Execution Governor docs:
# https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_cursors.htm
# https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_gov_limits.htm
LIMIT_SECTIONS: list[dict] = [
    {
        "title": "Per transaction (each Apex request)",
        "rows": [
            ("Cursor instances open", "50", "50"),
            ("Rows across all cursors in txn", "100,000", "50,000,000"),
            ("Fetch calls (shared)", "100", "100"),
        ],
    },
    {
        "title": "Per pagination fetchPage call",
        "rows": [
            ("Max rows per page", "2,000", "—"),
        ],
    },
    {
        "title": "Per org (rolling 24 hours)",
        "rows": [
            ("Cursor instances opened", "200,000", "10,000"),
            ("New rows fetched (shared)", "100,000,000", "100,000,000"),
        ],
    },
]

HEADERS = ("Limit", "Pagination", "Standard")

INFO_NOTES = [
    "Transaction limits apply to each Apex request; daily limits roll per org over 24 hours.",
    "Fetch calls and daily row counts are shared across standard and pagination cursors.",
    "Cursors expire like API query cursors — see API Query Cursor Limits in Salesforce Help.",
    "Aggregate, subselect and virtual object queries are not supported.",
]

SLIDE_CY = 6_858_000
MARGIN_X = 338_325
FULL_W = 11_484_900
TITLE_BOTTOM = 999_000
BOTTOM_MARGIN = 220_000
HEADER_GAP = 90_000
INFO_GAP = 100_000
INFO_H = 1_650_000
INFO_PAD = 95_000
ROUND_ADJ = 6000
DATA_ROW_H = 335_000
SECTION_ROW_H = 285_000
HEADER_H = 420_000
COL_LABEL_W = int(FULL_W * 0.52)
COL_VAL_W = (FULL_W - COL_LABEL_W) // 2

TABLE_H = HEADER_H + sum(
    SECTION_ROW_H + len(section["rows"]) * DATA_ROW_H for section in LIMIT_SECTIONS
)
_CONTENT_H = TABLE_H + INFO_GAP + INFO_H
_CONTENT_TOP = TITLE_BOTTOM + HEADER_GAP
_CONTENT_BOTTOM = SLIDE_CY - BOTTOM_MARGIN
TABLE_Y = _CONTENT_TOP + (_CONTENT_BOTTOM - _CONTENT_TOP - _CONTENT_H) // 2
INFO_Y = TABLE_Y + TABLE_H + INFO_GAP

CARD_SHADOW = (
    '<a:effectLst><a:outerShdw blurRad="50800" dist="31750" dir="2700000" '
    'algn="ctr" rotWithShape="0"><a:srgbClr val="000000">'
    '<a:alpha val="28000"/></a:srgbClr></a:outerShdw></a:effectLst>'
)


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def cell_para(
    text: str,
    *,
    align: str = "l",
    bold: bool = False,
    color: str = "333333",
    size: int = 1700,
    before_pts: str = "0",
) -> str:
    weight = ' b="1"' if bold else ""
    return f"""<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="{align}"><a:lnSpc><a:spcPct val="105000"/></a:lnSpc><a:spcBef><a:spcPts val="{before_pts}"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="{size}"{weight}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{esc(text)}</a:t></a:r><a:endParaRPr/></a:p>"""


def bullet_para(text: str, before_pts: str = "200", after_pts: str = "0") -> str:
    return f"""<a:p><a:pPr indent="-285750" lvl="0" marL="457200" rtl="0" algn="l"><a:lnSpc><a:spcPct val="112000"/></a:lnSpc><a:spcBef><a:spcPts val="{before_pts}"/></a:spcBef><a:spcAft><a:spcPts val="{after_pts}"/></a:spcAft><a:buClr><a:srgbClr val="891019"/></a:buClr><a:buSzPts val="1500"/><a:buChar char="•"/></a:pPr><a:r><a:rPr lang="en-US" sz="1650"/><a:t>{esc(text)}</a:t></a:r><a:endParaRPr/></a:p>"""


def info_body(notes: list[str]) -> str:
    parts = []
    for i, note in enumerate(notes):
        is_last = i == len(notes) - 1
        parts.append(
            bullet_para(
                note,
                "260" if i == 0 else "150",
                after_pts="100" if is_last else "0",
            )
        )
    return "".join(parts)


def rect_shape(
    shape_id: int,
    name: str,
    x: int,
    y: int,
    cx: int,
    cy: int,
    fill: str,
    *,
    shadow: bool = False,
    border: bool = True,
) -> str:
    shadow_xml = CARD_SHADOW if shadow else ""
    border_xml = (
        '<a:ln w="9525"><a:solidFill><a:srgbClr val="E8E8E8"/></a:solidFill></a:ln>'
        if border
        else "<a:ln><a:noFill/></a:ln>"
    )
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>{border_xml}{shadow_xml}</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody></p:sp>"""


def text_cell(
    shape_id: int,
    name: str,
    x: int,
    y: int,
    cx: int,
    cy: int,
    body: str,
    *,
    pad_l: int = 110_000,
    pad_r: int = 80_000,
    anchor: str = "ctr",
    wrap: str = "square",
) -> str:
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{name}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr anchor="{anchor}" anchorCtr="1" wrap="{wrap}" lIns="{pad_l}" rIns="{pad_r}" tIns="0" bIns="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>{body}</p:txBody></p:sp>"""


def col_x(col: int) -> int:
    if col == 0:
        return MARGIN_X
    if col == 1:
        return MARGIN_X + COL_LABEL_W
    return MARGIN_X + COL_LABEL_W + COL_VAL_W


def col_w(col: int) -> int:
    return COL_LABEL_W if col == 0 else COL_VAL_W


def section_header(parts: list[str], sid: int, y: int, title: str) -> tuple[int, int]:
    parts.append(
        rect_shape(sid, f"limits-section-{sid}", MARGIN_X, y, FULL_W, SECTION_ROW_H, "E8ECF4")
    )
    sid += 1
    parts.append(
        text_cell(
            sid,
            f"limits-section-text-{sid}",
            MARGIN_X,
            y,
            FULL_W,
            SECTION_ROW_H,
            cell_para(title, bold=True, color="891019", size=1650),
            pad_l=110_000,
            anchor="ctr",
        )
    )
    sid += 1
    return sid, y + SECTION_ROW_H


def data_row(parts: list[str], sid: int, y: int, row_idx: int, label: str, pag: str, std: str) -> tuple[int, int]:
    fill = "F9FAFC" if row_idx % 2 == 0 else "FFFFFF"
    values = (label, pag, std)
    aligns = ("l", "ctr", "ctr")
    for col in range(3):
        cx = col_w(col)
        x = col_x(col)
        parts.append(rect_shape(sid, f"limits-row-{row_idx}-bg-{col}", x, y, cx, DATA_ROW_H, fill))
        sid += 1
        parts.append(
            text_cell(
                sid,
                f"limits-row-{row_idx}-{col}",
                x,
                y,
                cx,
                DATA_ROW_H,
                cell_para(
                    values[col],
                    align=aligns[col],
                    bold=col == 0,
                    color="333333" if col == 0 else "444444",
                    size=1620 if col == 0 else 1700,
                ),
                pad_l=110_000 if col == 0 else 40_000,
                pad_r=40_000,
            )
        )
        sid += 1
    return sid, y + DATA_ROW_H


def table_xml() -> str:
    parts: list[str] = []
    sid = 201
    parts.append(
        rect_shape(
            sid, "limits-table-shadow", MARGIN_X, TABLE_Y, FULL_W, TABLE_H, "FFFFFF", shadow=True
        )
    )
    sid += 1

    y = TABLE_Y
    header_fills = ("891019", "4A6FA5", "5A7A3A")
    for col, (label, fill) in enumerate(zip(HEADERS, header_fills)):
        cx = col_w(col)
        x = col_x(col)
        parts.append(rect_shape(sid, f"limits-hdr-bg-{col}", x, y, cx, HEADER_H, fill, border=False))
        sid += 1
        parts.append(
            text_cell(
                sid,
                f"limits-hdr-{col}",
                x,
                y,
                cx,
                HEADER_H,
                cell_para(label, align="ctr" if col else "l", bold=True, color="FFFFFF", size=1850),
                pad_l=110_000 if col == 0 else 40_000,
                pad_r=40_000,
            )
        )
        sid += 1
    y += HEADER_H

    row_idx = 0
    for section in LIMIT_SECTIONS:
        sid, y = section_header(parts, sid, y, section["title"])
        for label, pag, std in section["rows"]:
            sid, y = data_row(parts, sid, y, row_idx, label, pag, std)
            row_idx += 1

    return "\n".join(parts)


def info_panel_xml(shape_id: int) -> str:
    body = info_body(INFO_NOTES)
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="limits-info-panel"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{MARGIN_X}" y="{INFO_Y}"/><a:ext cx="{FULL_W}" cy="{INFO_H}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {ROUND_ADJ}"/></a:avLst></a:prstGeom><a:solidFill><a:srgbClr val="F4F7FC"/></a:solidFill><a:ln><a:noFill/></a:ln>{CARD_SHADOW}</p:spPr><p:txBody><a:bodyPr anchor="t" anchorCtr="0" wrap="square" lIns="{INFO_PAD + 20_000}" rIns="{INFO_PAD}" tIns="{INFO_PAD}" bIns="{INFO_PAD}"><a:noAutofit/></a:bodyPr><a:lstStyle/>{body}</p:txBody></p:sp>"""


def title_shape() -> str:
    title_esc = esc(TITLE)
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="116" name="Google Shape;116;p14"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="338327" y="90720"/><a:ext cx="11515500" cy="908100"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr anchorCtr="0" anchor="b" bIns="0" lIns="0" spcFirstLastPara="1" rIns="0" wrap="square" tIns="0"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buClr><a:srgbClr val="891019"/></a:buClr><a:buSzPts val="3200"/><a:buFont typeface="Arial"/><a:buNone/></a:pPr><a:r><a:rPr lang="en-US"/><a:t>{title_esc}</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp>"""


def build_slide() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:mv="urn:schemas-microsoft-com:mac:vml" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:dgm="http://schemas.openxmlformats.org/drawingml/2006/diagram" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:pvml="urn:schemas-microsoft-com:office:powerpoint" xmlns:com="http://schemas.openxmlformats.org/drawingml/2006/compatibility" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" xmlns:p15="http://schemas.microsoft.com/office/powerpoint/2012/main" xmlns:ahyp="http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="114" name="Shape 114"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
{table_xml()}
{info_panel_xml(239)}
{title_shape()}
</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr><mc:AlternateContent><mc:Choice Requires="p14"><p:transition spd="slow" p14:dur="700"><p:fade/></p:transition></mc:Choice><mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent></p:sld>
"""


def main() -> None:
    SLIDE.write_text(build_slide())
    print(f"Wrote {SLIDE}")


if __name__ == "__main__":
    main()
