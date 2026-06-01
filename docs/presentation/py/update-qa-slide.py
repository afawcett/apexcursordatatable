#!/usr/bin/env python3
"""Build slide 15: Q&A with session resources QR code."""
from __future__ import annotations

import html
import shutil
import subprocess
from pathlib import Path

PRES = Path(__file__).resolve().parent.parent
SLIDE = PRES / "src/ppt/slides/slide15.xml"
SLIDE_RELS = PRES / "src/ppt/slides/_rels/slide15.xml.rels"
QA_TEMPLATE = PRES / "templateslides/qa.xml"
MEDIA = PRES / "src/ppt/media/qa-github-qrcode.png"
QR_SOURCE = PRES / "screenshots/qa-github-qrcode.png"

QR_URL = "https://afawcett.github.io/landingpages/sessions/apex-cursors-lc26.html"
CAPTION_TEXT = "View Session Resources"

# EMUs — slide 12188825 × 6858000
SLIDE_W = 12_188_825
MARGIN_X = 338_325
FULL_W = 11_484_900
QR_SIZE = 1_750_000
RIGHT_INSET = 2_250_000  # inset from right — clear skyline / sponsor area
QR_X = SLIDE_W - RIGHT_INSET - QR_SIZE
QR_Y = 2_700_000
BADGE_GAP = 90_000
BADGE_W = 3_050_000
BADGE_H = 440_000
BADGE_X = max(MARGIN_X, QR_X + (QR_SIZE - BADGE_W) // 2)
BADGE_Y = QR_Y + QR_SIZE + BADGE_GAP
BADGE_PAD = 70_000
BADGE_FONT_SZ = 1350
ROUND_ADJ = 12000

CARD_SHADOW = (
    '<a:effectLst><a:outerShdw blurRad="50800" dist="31750" dir="2700000" '
    'algn="ctr" rotWithShape="0"><a:srgbClr val="000000">'
    '<a:alpha val="28000"/></a:srgbClr></a:outerShdw></a:effectLst>'
)


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def generate_qr_png() -> None:
    QR_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "qrencode",
            "-o",
            str(QR_SOURCE),
            "-s",
            "12",
            "-m",
            "2",
            "-l",
            "M",
            QR_URL,
        ],
        check=True,
    )
    shutil.copy2(QR_SOURCE, MEDIA)


def qr_pic_xml() -> str:
    return f"""<p:pic><p:nvPicPr><p:cNvPr id="190" name="qa-github-qrcode" title="Session Resources"/><p:cNvPicPr preferRelativeResize="0"/><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="rId4"><a:alphaModFix/></a:blip><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{QR_X}" y="{QR_Y}"/><a:ext cx="{QR_SIZE}" cy="{QR_SIZE}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{CARD_SHADOW}</p:spPr></p:pic>"""


def caption_xml() -> str:
    label = esc(CAPTION_TEXT)
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="191" name="qa-github-caption"/>'
        f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{BADGE_X}" y="{BADGE_Y}"/>'
        f'<a:ext cx="{BADGE_W}" cy="{BADGE_H}"/></a:xfrm>'
        f'<a:prstGeom prst="roundRect"><a:avLst>'
        f'<a:gd name="adj" fmla="val {ROUND_ADJ}"/></a:avLst></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
        f'<a:ln w="12700"><a:solidFill><a:srgbClr val="891019"/></a:solidFill></a:ln>'
        f'{CARD_SHADOW}</p:spPr>'
        f'<p:txBody><a:bodyPr anchor="ctr" anchorCtr="1" wrap="none" '
        f'lIns="{BADGE_PAD}" rIns="{BADGE_PAD}" tIns="0" bIns="0">'
        f'<a:noAutofit/></a:bodyPr><a:lstStyle/>'
        f'<a:p><a:pPr algn="ctr"><a:buNone/></a:pPr>'
        f'<a:r><a:rPr lang="en-US" sz="{BADGE_FONT_SZ}" b="1">'
        f'<a:solidFill><a:srgbClr val="891019"/></a:solidFill>'
        f'<a:hlinkClick r:id="rId5"/></a:rPr>'
        f'<a:t>{label}</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp>'
    )


def title_xml() -> str:
    return (
        '<p:sp><p:nvSpPr><p:cNvPr id="188" name="Google Shape;188;p22"/>'
        '<p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="ctrTitle"/></p:nvPr></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="360362" y="2691891"/>'
        '<a:ext cx="10908300" cy="1210800"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
        '<p:txBody><a:bodyPr anchorCtr="0" anchor="b" bIns="0" lIns="0" spcFirstLastPara="1" '
        'rIns="0" wrap="square" tIns="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
        '<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="ctr">'
        '<a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef>'
        '<a:spcAft><a:spcPts val="0"/></a:spcAft><a:buClr><a:srgbClr val="89050F"/></a:buClr>'
        '<a:buSzPts val="5400"/><a:buFont typeface="Arial"/><a:buNone/></a:pPr>'
        '<a:r><a:rPr lang="en-US"/><a:t>Q&amp;A</a:t></a:r><a:endParaRPr/></a:p></p:txBody></p:sp>'
    )


def ensure_title(slide_xml: str) -> str:
    if "Q&amp;A</a:t>" in slide_xml:
        return slide_xml
    contact = '<p:sp><p:nvSpPr><p:cNvPr id="189"'
    if contact in slide_xml:
        return slide_xml.replace(contact, title_xml() + contact, 1)
    marker = "</p:grpSpPr>"
    return slide_xml.replace(marker, marker + title_xml(), 1)


def inject_qr(slide_xml: str) -> str:
    insert = qr_pic_xml() + caption_xml()
    marker = '<p:sp><p:nvSpPr><p:cNvPr id="188"'
    if "qa-github-qrcode" in slide_xml:
        start = slide_xml.index('<p:pic><p:nvPicPr><p:cNvPr id="190"')
        caption = slide_xml.index('name="qa-github-caption"', start)
        end = slide_xml.index("</p:sp>", caption) + len("</p:sp>")
        slide_xml = slide_xml[:start] + insert + slide_xml[end:]
    else:
        slide_xml = slide_xml.replace(marker, insert + marker, 1)
    return ensure_title(slide_xml)


def write_rels() -> None:
    SLIDE_RELS.write_text(
        """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide15.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="mailto:andy@andyinthecloud.com" TargetMode="External"/><Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/qa-github-qrcode.png"/><Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="https://afawcett.github.io/landingpages/sessions/apex-cursors-lc26.html" TargetMode="External"/></Relationships>
"""
    )


def main() -> None:
    generate_qr_png()
    base = SLIDE.read_text() if SLIDE.exists() else QA_TEMPLATE.read_text()
    slide_xml = inject_qr(base)
    SLIDE.write_text(slide_xml)
    shutil.copy2(SLIDE, QA_TEMPLATE)
    write_rels()
    print(f"Wrote {SLIDE}")
    print(f"QR code -> {MEDIA}")


if __name__ == "__main__":
    main()
