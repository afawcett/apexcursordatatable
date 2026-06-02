#!/usr/bin/env python3
"""Build demo Highlights slides: 3 shadow code boxes + full-width bullet panel."""
from __future__ import annotations

import html
import sys
from pathlib import Path

PRES = Path(__file__).resolve().parent.parent

# EMUs — slide 12188825 × 6858000; title placeholder ends ~999000
SLIDE_CY = 6_858_000
MARGIN_X = 338_325
FULL_W = 11_484_900
TITLE_BOTTOM = 999_000
BOTTOM_MARGIN = 220_000
HEADER_GAP = 90_000
CODE_GAP = 120_000
INFO_GAP = 120_000
CODE_BOX_W = (FULL_W - 2 * CODE_GAP) // 3
# ~10 code lines + apex> prompt at 15pt Consolas (sz 1500)
CODE_BOX_H = 2_450_000
# 4 bullets with room for wrapped lines
INFO_H = 1_950_000
CODE_FONT_SZ = 1500
CODE_PAD_T = 55_000
CODE_PAD_B = 160_000
CODE_PAD_LR = 72_000
INFO_PAD = 120_000
ROUND_ADJ = 6000
BADGE_SIZE = 480_000
BADGE_HANG = 0.44  # fraction of badge outside top-left corner
BADGE_FILL = "891019"
BADGE_SHADOW = (
    '<a:effectLst><a:outerShdw blurRad="57150" dist="38100" dir="2700000" '
    'algn="ctr" rotWithShape="0"><a:srgbClr val="000000">'
    '<a:alpha val="45000"/></a:srgbClr></a:outerShdw></a:effectLst>'
)

_CONTENT_H = CODE_BOX_H + INFO_GAP + INFO_H
_CONTENT_TOP = TITLE_BOTTOM + HEADER_GAP
_CONTENT_BOTTOM = SLIDE_CY - BOTTOM_MARGIN
CODE_Y = _CONTENT_TOP + (_CONTENT_BOTTOM - _CONTENT_TOP - _CONTENT_H) // 2
INFO_Y = CODE_Y + CODE_BOX_H + INFO_GAP

CARD_SHADOW = (
    '<a:effectLst><a:outerShdw blurRad="50800" dist="31750" dir="2700000" '
    'algn="ctr" rotWithShape="0"><a:srgbClr val="000000">'
    '<a:alpha val="28000"/></a:srgbClr></a:outerShdw></a:effectLst>'
)

# Match docs/presentation README code sample color convention
CODE_COLOR_TYPE = "569CD6"
CODE_COLOR_CALL = "DCDCAA"
CODE_COLOR_LITERAL = "CE9178"
CODE_COLOR_TEXT = "D4D4D4"
CODE_COLOR_PROMPT = "6A9955"

DEMOS: dict[int, dict] = {
    1: {
        "title": "Demo 1: Virtual Data Table Summary",
        "slide": 7,
        "code_boxes": [
            {
                "lines": [
                    [("cursor = Database.getCursor(", CODE_COLOR_CALL)],
                    [("    ACCOUNT_SOQL,", CODE_COLOR_LITERAL)],
                    [("    AccessLevel.USER_MODE);", CODE_COLOR_LITERAL)],
                    [
                        ("pageCursor =",
                         CODE_COLOR_TEXT),
                    ],
                    [
                        ("  Database.getPaginationCursor(",
                         CODE_COLOR_CALL),
                    ],
                    [("    ACCOUNT_SOQL,", CODE_COLOR_LITERAL)],
                    [("    AccessLevel.USER_MODE);", CODE_COLOR_LITERAL)],
                ],
            },
            {
                "lines": [
                    [("if (pageCursor == null) {", CODE_COLOR_TEXT)],
                    [
                        ("  pageCursor = Database.getPaginationCursor(",
                         CODE_COLOR_CALL),
                    ],
                    [
                        ("    ACCOUNT_SOQL, AccessLevel.USER_MODE);",
                         CODE_COLOR_LITERAL),
                    ],
                    [("  Cache.Session.put(", CODE_COLOR_CALL)],
                    [
                        ("    SESSION_PAGINATION_CURSOR_KEY,",
                         CODE_COLOR_LITERAL),
                    ],
                    [("    pageCursor);", CODE_COLOR_TEXT)],
                    [("}", CODE_COLOR_TEXT)],
                ],
            },
            {
                "lines": [
                    [
                        ("Integer remaining = totalRecords - start;",
                         CODE_COLOR_TEXT),
                    ],
                    [
                        ("Integer fetchSize = remaining > 0",
                         CODE_COLOR_TEXT),
                    ],
                    [
                        ("    ? ", CODE_COLOR_TEXT),
                        ("Math.min", CODE_COLOR_CALL),
                        ("(pageSize, remaining) : 0;", CODE_COLOR_LITERAL),
                    ],
                    [
                        ("fetchResult = fetchSize > 0",
                         CODE_COLOR_TEXT),
                    ],
                    [
                        ("    ? ", CODE_COLOR_TEXT),
                        ("pageCursor.fetchPage", CODE_COLOR_CALL),
                        ("(start, fetchSize)", CODE_COLOR_LITERAL),
                    ],
                    [("    : null;", CODE_COLOR_LITERAL)],
                ],
            },
        ],
        "bullets": [
            "Standard Cursor or PaginationCursor — same ACCOUNT_SOQL, different paging APIs",
            "Cache.Session keeps the pagination cursor between requests; session cache and cursors are per user",
            "Page size is capped to remaining rows in the result set",
            "Limits panel shows cursor, fetch, and daily governor usage",
        ],
    },
    2: {
        "title": "Demo 2: Interactive Reporting and Drilldown Summary",
        "slide": 9,
        "code_boxes": [
            {
                "prompt": "soql>",
                "lines": [
                    [
                        ("SELECT", CODE_COLOR_TYPE),
                        (" Id, EffectiveDate__c,", CODE_COLOR_TEXT),
                    ],
                    [
                        ("  Value__c, Product__c", CODE_COLOR_TEXT),
                    ],
                    [
                        ("FROM", CODE_COLOR_TYPE),
                        (" UnitPriceObservation__c", CODE_COLOR_TEXT),
                    ],
                    [
                        ("WHERE", CODE_COLOR_TYPE),
                        (" Product__c = :product", CODE_COLOR_TEXT),
                    ],
                    [
                        ("ORDER BY", CODE_COLOR_TYPE),
                        (" EffectiveDate__c ", CODE_COLOR_TEXT),
                        ("ASC", CODE_COLOR_TYPE),
                    ],
                ],
            },
            {
                "lines": [
                    [("Database.CursorFetchResult", CODE_COLOR_TYPE)],
                    [("   midChunk =", CODE_COLOR_TEXT)],
                    [
                        ("      pageCursor.fetchPage(dayIndex, 1);",
                         CODE_COLOR_CALL),
                    ],
                ],
            },
            {
                "lines": [
                    [("Database.CursorFetchResult", CODE_COLOR_TYPE)],
                    [("    drilldownRecords =", CODE_COLOR_TEXT)],
                    [("      pageCursor.fetchPage(", CODE_COLOR_CALL)],
                    [
                        ("          drillStart, drillSize);",
                         CODE_COLOR_LITERAL),
                    ],
                ],
            },
        ],
        "bullets": [
            "PaginationCursor builds the monthly chart with one fetchPage per month",
            "Session cache keeps the cursor for brush-selection drill-down",
            "Index-based fetchPage maps chart range to daily observation rows",
            "fetchPage reports deleted rows when underlying data changes",
        ],
    },
    3: {
        "title": "Demo 3: Adaptive Async Summary",
        "slide": 11,
        "code_boxes": [
            {
                "lines": [
                    [("Database.Cursor cursor =", "D4D4D4")],
                    [("  Database.getCursor(", "DCDCAA")],
                    [("    soql,", "CE9178")],
                    [("    AccessLevel.USER_MODE);", "CE9178")],
                    [("System.enqueueJob(", "DCDCAA")],
                    [("  new AdaptiveOrderWorkerQueueable(", "CE9178")],
                    [("    runId, cursor, 1), options);", "CE9178")],
                ],
            },
            {
                "lines": [
                    [
                        ("Integer ", CODE_COLOR_TYPE),
                        ("rowCalloutsRequired =", CODE_COLOR_TEXT),
                    ],
                    [
                        ("   ", CODE_COLOR_TEXT),
                        ("rowCalloutsFor", CODE_COLOR_CALL),
                        ("(row);", CODE_COLOR_LITERAL),
                    ],
                    [
                        ("Boolean ", CODE_COLOR_TYPE),
                        ("canProcessRow =", CODE_COLOR_TEXT),
                    ],
                    [
                        ("   rowCalloutsRequired == ", CODE_COLOR_TEXT),
                        ("0", CODE_COLOR_LITERAL),
                        (" ||", CODE_COLOR_TEXT),
                    ],
                    [
                        ("       scope.", CODE_COLOR_TEXT),
                        ("predictedCallouts", CODE_COLOR_TEXT),
                        (" +", CODE_COLOR_TEXT),
                    ],
                    [
                        ("      rowCalloutsRequired <= ", CODE_COLOR_TEXT),
                        ("calloutBudget;", CODE_COLOR_TEXT),
                    ],
                ],
            },
            {
                "lines": [
                    [
                        ("if (", CODE_COLOR_TYPE),
                        ("Limits", CODE_COLOR_TYPE),
                        (".getFetchCallsOnApexCursor", CODE_COLOR_CALL),
                        ("() >= ", CODE_COLOR_TEXT),
                    ],
                    [
                        ("    ", CODE_COLOR_TEXT),
                        ("Limits", CODE_COLOR_TYPE),
                        (".getLimitFetchCallsOnApexCursor", CODE_COLOR_CALL),
                        ("()) {", CODE_COLOR_TEXT),
                    ],
                    [
                        ("     ", CODE_COLOR_TEXT),
                        ("return", CODE_COLOR_TYPE),
                        (" scope;", CODE_COLOR_TEXT),
                    ],
                    [("}", CODE_COLOR_TEXT)],
                ],
            },
        ],
        "bullets": [
            "One cursor opened in Apex and passed through chained queueable jobs",
            "Chunk size adapts to remaining HTTP callout budget per transaction",
            "Track fetch limits dynamically via Limits.getFetchCallsOnApexCursor",
            "Cursor position travels on the job state",
        ],
    },
}


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
        f'<a:lnSpc><a:spcPct val="100000"/></a:lnSpc>'
        f'<a:spcBef><a:spcPts val="{before_pts}"/></a:spcBef>'
        f'<a:spcAft><a:spcPts val="{after_pts}"/></a:spcAft><a:buNone/></a:pPr>'
        f"{run_xml}<a:endParaRPr/></a:p>"
    )


def terminal_body(
    lines: list[list[tuple[str, str]]], *, prompt: str = "apex>"
) -> str:
    parts = [code_line_para([(prompt, CODE_COLOR_PROMPT)], "80")]
    for i, runs in enumerate(lines):
        is_last = i == len(lines) - 1
        parts.append(
            code_line_para(runs, "60" if i == 0 else "40", after_pts="160" if is_last else "0")
        )
    return "".join(parts)


def bullet_para(text: str, before_pts: str = "280", after_pts: str = "0") -> str:
    return f"""<a:p><a:pPr indent="-285750" lvl="0" marL="457200" rtl="0" algn="l"><a:lnSpc><a:spcPct val="115000"/></a:lnSpc><a:spcBef><a:spcPts val="{before_pts}"/></a:spcBef><a:spcAft><a:spcPts val="{after_pts}"/></a:spcAft><a:buClr><a:srgbClr val="891019"/></a:buClr><a:buSzPts val="1600"/><a:buChar char="•"/></a:pPr><a:r><a:rPr lang="en-US" sz="1800"/><a:t>{esc(text)}</a:t></a:r><a:endParaRPr/></a:p>"""


def info_body(bullets: list[str]) -> str:
    parts = []
    for i, item in enumerate(bullets):
        is_last = i == len(bullets) - 1
        parts.append(
            bullet_para(
                item,
                "360" if i == 0 else "220",
                after_pts="120" if is_last else "0",
            )
        )
    return "".join(parts)


def code_body_pr(
    *,
    anchor: str,
    anchor_ctr: str,
    t_ins: int,
    b_ins: int,
    l_ins: int,
    r_ins: int,
    wrap: str,
    clip_overflow: bool,
) -> str:
    overflow = (
        ' horzOverflow="clip" vertOverflow="clip"' if clip_overflow else ""
    )
    return (
        f'anchorCtr="{anchor_ctr}" anchor="{anchor}" bIns="{b_ins}" '
        f'lIns="{l_ins}" rIns="{r_ins}" tIns="{t_ins}" wrap="{wrap}"{overflow}'
    )


def shadow_box(
    shape_id: int,
    name: str,
    x: int,
    y: int,
    cx: int,
    cy: int,
    bg: str,
    body: str,
    *,
    anchor: str = "t",
    anchor_ctr: str = "0",
    t_ins: int = CODE_PAD_T,
    b_ins: int = CODE_PAD_B,
    l_ins: int = CODE_PAD_LR,
    r_ins: int = CODE_PAD_LR,
    wrap: str = "square",
    clip_overflow: bool = False,
) -> str:
    body_pr = code_body_pr(
        anchor=anchor,
        anchor_ctr=anchor_ctr,
        t_ins=t_ins,
        b_ins=b_ins,
        l_ins=l_ins,
        r_ins=r_ins,
        wrap=wrap,
        clip_overflow=clip_overflow,
    )
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{name}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {ROUND_ADJ}"/></a:avLst></a:prstGeom><a:solidFill><a:srgbClr val="{bg}"/></a:solidFill><a:ln><a:noFill/></a:ln>{CARD_SHADOW}</p:spPr><p:txBody><a:bodyPr {body_pr}><a:noAutofit/></a:bodyPr><a:lstStyle/>{body}</p:txBody></p:sp>"""


def number_badge(shape_id: int, box_x: int, box_y: int, number: int) -> str:
    hang = int(BADGE_SIZE * BADGE_HANG)
    bx = box_x - hang
    by = box_y - hang
    num = esc(str(number))
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="highlight-badge-{number}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{bx}" y="{by}"/><a:ext cx="{BADGE_SIZE}" cy="{BADGE_SIZE}"/></a:xfrm><a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{BADGE_FILL}"/></a:solidFill><a:ln><a:noFill/></a:ln>{BADGE_SHADOW}</p:spPr><p:txBody><a:bodyPr anchor="ctr" anchorCtr="1" wrap="none" lIns="0" rIns="0" tIns="0" bIns="0"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="ctr"><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="2400" b="1"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:rPr><a:t>{num}</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp>"""


def title_shape(title: str) -> str:
    title_esc = esc(title)
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="116" name="Google Shape;116;p14"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="338327" y="90720"/><a:ext cx="11515500" cy="908100"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr anchorCtr="0" anchor="b" bIns="0" lIns="0" spcFirstLastPara="1" rIns="0" wrap="square" tIns="0"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft><a:buClr><a:srgbClr val="891019"/></a:buClr><a:buSzPts val="3200"/><a:buFont typeface="Arial"/><a:buNone/></a:pPr><a:r><a:rPr lang="en-US"/><a:t>{title_esc}</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp>"""


def build_slide(demo: dict) -> str:
    parts: list[str] = []
    sid = 201
    for i, box in enumerate(demo["code_boxes"]):
        x = MARGIN_X + i * (CODE_BOX_W + CODE_GAP)
        parts.append(
            shadow_box(
                sid,
                f"highlight-code-{i + 1}",
                x,
                CODE_Y,
                CODE_BOX_W,
                CODE_BOX_H,
                "1E1E1E",
                terminal_body(box["lines"], prompt=box.get("prompt", "apex>")),
                wrap="none",
                clip_overflow=True,
            )
        )
        sid += 1
        parts.append(number_badge(sid, x, CODE_Y, i + 1))
        sid += 1

    parts.append(
        shadow_box(
            sid,
            "highlight-info-panel",
            MARGIN_X,
            INFO_Y,
            FULL_W,
            INFO_H,
            "F4F7FC",
            info_body(demo["bullets"]),
            t_ins=INFO_PAD,
            b_ins=INFO_PAD,
            l_ins=INFO_PAD + 20_000,
            r_ins=INFO_PAD,
        )
    )

    content = "\n".join(parts)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:mv="urn:schemas-microsoft-com:mac:vml" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:dgm="http://schemas.openxmlformats.org/drawingml/2006/diagram" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:pvml="urn:schemas-microsoft-com:office:powerpoint" xmlns:com="http://schemas.openxmlformats.org/drawingml/2006/compatibility" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" xmlns:p15="http://schemas.microsoft.com/office/powerpoint/2012/main" xmlns:ahyp="http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="114" name="Shape 114"/><p:cNvSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
{content}
{title_shape(demo["title"])}
</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr><mc:AlternateContent><mc:Choice Requires="p14"><p:transition spd="slow" p14:dur="700"><p:fade/></p:transition></mc:Choice><mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent></p:sld>
"""


def write_demo(demo_num: int) -> None:
    demo = DEMOS[demo_num]
    slide_path = PRES / f"src/ppt/slides/slide{demo['slide']}.xml"
    slide_path.write_text(build_slide(demo))
    print(f"Wrote slide {demo['slide']}: {demo['title']}")


def main() -> None:
    if len(sys.argv) > 1:
        nums = [int(n) for n in sys.argv[1:]]
    else:
        nums = sorted(DEMOS)
    for n in nums:
        if n not in DEMOS:
            raise SystemExit(f"Unknown demo {n}; defined: {sorted(DEMOS)}")
        write_demo(n)


if __name__ == "__main__":
    main()
