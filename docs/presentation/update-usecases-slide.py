#!/usr/bin/env python3
"""Build slide 5: Interactive | Batch, terminal API snippets, shared Architecture."""
from __future__ import annotations

import html
from pathlib import Path

PRES = Path(__file__).resolve().parent
SLIDE = PRES / "src/ppt/slides/slide5.xml"

TITLE = "Usecases for Apex Cursors"

INTERACTIVE = {
    "heading": "Interactive",
    "color": "4A6FA5",
    "bullets": [
        "Analyst large data view",
        "Reporting and drilldown",
        "Preview job records to process",
    ],
}

BATCH = {
    "heading": "Batch",
    "color": "5A7A3A",
    "bullets": [
        "Orchestrate process execution",
        "Look ahead to optimize resource usage",
        "Safer immutable record set",
    ],
}

ARCHITECTURE = [
    "24hr cached large record sets",
    "Scalable replacement to SOQL OFFSET",
    "Bidirectional navigation",
]

PAGINATION_CURSOR_LINES = [
    [("Database.PaginationCursor", "569CD6"), (" c =", "D4D4D4")],
    [("  Database.getPaginationCursor(", "DCDCAA")],
    [("    soql, AccessLevel.USER_MODE);", "CE9178")],
    [("Database.CursorFetchResult r =", "D4D4D4")],
    [("  c.fetchPage(start, pageSize);", "DCDCAA")],
]

STANDARD_CURSOR_LINES = [
    [("Database.Cursor", "4EC9B0"), (" c =", "D4D4D4")],
    [("  Database.getCursor(", "DCDCAA")],
    [("    soql, AccessLevel.USER_MODE);", "CE9178")],
    [("List<Account> batch =", "D4D4D4")],
    [("  c.fetch(offset, pageSize);", "DCDCAA")],
]

# EMUs (slide 12188825 x 6858000; title placeholder ends ~999000)
MARGIN_X = 338_325
FULL_W = 11_484_900
COL_W = 5_400_000
LEFT_X = MARGIN_X
RIGHT_X = MARGIN_X + FULL_W - COL_W
SLIDE_CY = 6_858_000
TITLE_BOTTOM = 999_000
COL_USE_H = 1_580_000
TERM_GAP = 120_000
TERM_H = 1_850_000
CODE_FONT_SZ = 1700  # ~55% larger than 1100
TERM_PAD_T = 50_000
TERM_PAD_B = 190_000
TERM_PAD_LR = 91_440
ARCH_GAP = 300_000
ARCH_H = 980_000
_CONTENT_H = COL_USE_H + TERM_GAP + TERM_H + ARCH_GAP + ARCH_H
TOP_Y = TITLE_BOTTOM + (SLIDE_CY - TITLE_BOTTOM - _CONTENT_H) // 2
TERM_Y = TOP_Y + COL_USE_H + TERM_GAP
ARCH_Y = TERM_Y + TERM_H + ARCH_GAP


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def heading_para(text: str, color: str) -> str:
    return f"""<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="400"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="2400" b="1"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{esc(text)}</a:t></a:r><a:endParaRPr/></a:p>"""


def bullet_para(text: str, before_pts: str = "400") -> str:
    return f"""<a:p><a:pPr indent="-285750" lvl="0" marL="457200" rtl="0" algn="l"><a:lnSpc><a:spcPct val="110000"/></a:lnSpc><a:spcBef><a:spcPts val="{before_pts}"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buClr><a:srgbClr val="891019"/></a:buClr><a:buSzPts val="1600"/><a:buChar char="•"/></a:pPr><a:r><a:rPr lang="en-US" sz="1800"/><a:t>{esc(text)}</a:t></a:r><a:endParaRPr/></a:p>"""


def heading_para_center(text: str, color: str, after_pts: str = "300") -> str:
    return f"""<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="ctr"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="{after_pts}"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="2400" b="1"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{esc(text)}</a:t></a:r><a:endParaRPr/></a:p>"""


def bullet_para_center(text: str, before_pts: str = "200") -> str:
    return f"""<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="ctr"><a:lnSpc><a:spcPct val="110000"/></a:lnSpc><a:spcBef><a:spcPts val="{before_pts}"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buClr><a:srgbClr val="891019"/></a:buClr><a:buSzPts val="1600"/><a:buChar char="•"/></a:pPr><a:r><a:rPr lang="en-US" sz="1800"/><a:t>{esc(text)}</a:t></a:r><a:endParaRPr/></a:p>"""


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
        f'<a:lnSpc><a:spcPct val="100000"/></a:lnSpc>'
        f'<a:spcBef><a:spcPts val="{before_pts}"/></a:spcBef>'
        f'<a:spcAft><a:spcPts val="{after_pts}"/></a:spcAft><a:buNone/></a:pPr>'
        f"{run_xml}<a:endParaRPr/></a:p>"
    )


def use_cases_body(col: dict) -> str:
    parts = [heading_para(col["heading"], col["color"])]
    for i, item in enumerate(col["bullets"]):
        parts.append(bullet_para(item, "200" if i else "400"))
    return "".join(parts)


def terminal_body(lines: list[list[tuple[str, str]]]) -> str:
    parts = [code_line_para([("apex>", "6A9955")], "100")]
    for i, runs in enumerate(lines):
        is_last = i == len(lines) - 1
        parts.append(
            code_line_para(runs, "80" if i == 0 else "50", after_pts="200" if is_last else "0")
        )
    return "".join(parts)


def architecture_body() -> str:
    line = " | ".join(ARCHITECTURE)
    return (
        heading_para_center("Architecture", "891019", "200")
        + f"""<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="ctr"><a:lnSpc><a:spcPct val="110000"/></a:lnSpc><a:spcBef><a:spcPts val="180"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="1800"/><a:t>{esc(line)}</a:t></a:r><a:endParaRPr/></a:p>"""
    )


def text_shape(
    shape_id: int,
    name: str,
    x: int,
    y: int,
    cx: int,
    cy: int,
    body: str,
    *,
    anchor: str = "t",
    anchor_ctr: str = "0",
    fill: str | None = None,
    border: str | None = None,
    t_ins: int | None = None,
    b_ins: int | None = None,
    l_ins: int | None = None,
    r_ins: int | None = None,
) -> str:
    if t_ins is None:
        t_ins = 36_576
    if b_ins is None:
        b_ins = 54_864
    if l_ins is None:
        l_ins = 91_440
    if r_ins is None:
        r_ins = 91_440
    if fill:
        fill_xml = f"<a:solidFill><a:srgbClr val=\"{fill}\"/></a:solidFill>"
    else:
        fill_xml = "<a:noFill/>"
    if border:
        ln_xml = (
            f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{border}"/>'
            f"</a:solidFill></a:ln>"
        )
    else:
        ln_xml = "<a:ln><a:noFill/></a:ln>"
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{name}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill_xml}{ln_xml}</p:spPr><p:txBody><a:bodyPr anchorCtr="{anchor_ctr}" anchor="{anchor}" bIns="{b_ins}" lIns="{l_ins}" rIns="{r_ins}" tIns="{t_ins}" wrap="square"><a:noAutofit/></a:bodyPr><a:lstStyle/>{body}</p:txBody></p:sp>"""


def arch_band_rect(shape_id: int) -> str:
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="architecture-band"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{MARGIN_X}" y="{ARCH_Y}"/><a:ext cx="{FULL_W}" cy="{ARCH_H}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="F7F7F7"/></a:solidFill><a:ln><a:solidFill><a:srgbClr val="CCCCCC"/></a:solidFill></a:ln></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody></p:sp>"""


def build_slide() -> str:
    title_esc = esc(TITLE)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:mv="urn:schemas-microsoft-com:mac:vml" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:dgm="http://schemas.openxmlformats.org/drawingml/2006/diagram" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:pvml="urn:schemas-microsoft-com:office:powerpoint" xmlns:com="http://schemas.openxmlformats.org/drawingml/2006/compatibility" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" xmlns:p15="http://schemas.microsoft.com/office/powerpoint/2012/main" xmlns:ahyp="http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="114" name="Shape 114"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
{text_shape(115, "usecases-interactive", LEFT_X, TOP_Y, COL_W, COL_USE_H, use_cases_body(INTERACTIVE))}
{text_shape(117, "usecases-batch", RIGHT_X, TOP_Y, COL_W, COL_USE_H, use_cases_body(BATCH))}
{text_shape(120, "terminal-pagination", LEFT_X, TERM_Y, COL_W, TERM_H, terminal_body(PAGINATION_CURSOR_LINES), anchor="t", fill="1E1E1E", border="4A6FA5", t_ins=TERM_PAD_T, b_ins=TERM_PAD_B, l_ins=TERM_PAD_LR, r_ins=TERM_PAD_LR)}
{text_shape(121, "terminal-standard", RIGHT_X, TERM_Y, COL_W, TERM_H, terminal_body(STANDARD_CURSOR_LINES), anchor="t", fill="1E1E1E", border="5A7A3A", t_ins=TERM_PAD_T, b_ins=TERM_PAD_B, l_ins=TERM_PAD_LR, r_ins=TERM_PAD_LR)}
{arch_band_rect(118)}
{text_shape(119, "usecases-architecture", MARGIN_X, ARCH_Y, FULL_W, ARCH_H, architecture_body(), anchor="ctr", anchor_ctr="1")}
<p:sp><p:nvSpPr><p:cNvPr id="116" name="Google Shape;116;p14"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="338327" y="90720"/><a:ext cx="11515500" cy="908100"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr anchorCtr="0" anchor="b" bIns="0" lIns="0" spcFirstLastPara="1" rIns="0" wrap="square" tIns="0"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buClr><a:srgbClr val="891019"/></a:buClr><a:buSzPts val="3200"/><a:buFont typeface="Arial"/><a:buNone/></a:pPr><a:r><a:rPr lang="en-US"/><a:t>{title_esc}</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr><mc:AlternateContent><mc:Choice Requires="p14"><p:transition spd="slow" p14:dur="700"><p:fade/></p:transition></mc:Choice><mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent></p:sld>
"""


def main() -> None:
    SLIDE.write_text(build_slide())
    print(f"Wrote {SLIDE}")


if __name__ == "__main__":
    main()
