#!/usr/bin/env python3
"""Insert slide 2: Accessing and processing datasets today in SOQL."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

PRES = Path(__file__).resolve().parent
SRC = PRES / "src"
SLIDES = SRC / "ppt/slides"
SLIDE_RELS = SLIDES / "_rels"
NOTES = SRC / "ppt/notesSlides"
NOTES_RELS = NOTES / "_rels"
TPL = PRES / "templateslides/basic-layout.xml"
NOTES_TPL = PRES / "templateslides/_notesSlide2.xml"
SLIDE_RELS_TPL = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout2.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide2.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/diagram-soql-dataset-access-today.png"/></Relationships>
"""
NOTES_RELS_TPL = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/></Relationships>
"""

TITLE = "Accessing and processing datasets today in SOQL"
SUBTITLE = "UI paging with OFFSET/LIMIT vs async processing in fixed-size chunks."
PIC_CY = 5425455  # 11484900 * 520/1100


def set_title(xml: str, title: str) -> str:
    esc = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(
        r"(<p:ph type=\"title\"/>.*?<a:t>)([^<]*)(</a:t>)",
        rf"\1{esc}\3",
        xml,
        count=1,
        flags=re.DOTALL,
    )


def build_slide_xml() -> str:
    xml = TPL.read_text()
    xml = set_title(xml, TITLE)
    xml = re.sub(
        r"(<p:ph idx=\"1\" type=\"body\"/>.*?<a:t>)([^<]*)(</a:t>)",
        rf"\1{SUBTITLE.replace('&', '&amp;')}\3",
        xml,
        count=1,
        flags=re.DOTALL,
    )
    xml = re.sub(
        r"<p:spPr><a:xfrm><a:off x=\"338325\" y=\"1020943\"/><a:ext cx=\"11484900\" cy=\"5257200\"/>",
        '<p:spPr><a:xfrm><a:off x="338325" y="1050000"/><a:ext cx="11484900" cy="320000"/>',
        xml,
        count=1,
    )
    pic = (
        f'<p:pic><p:nvPicPr><p:cNvPr id="117" name="diagram-soql-dataset-access-today"/>'
        f'<p:cNvPicPr preferRelativeResize="0"/><p:nvPr/></p:nvPicPr>'
        f'<p:blipFill><a:blip r:embed="rId3"><a:alphaModFix/></a:blip>'
        f'<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
        f'<p:spPr><a:xfrm><a:off x="338325" y="1450000"/>'
        f'<a:ext cx="11484900" cy="{PIC_CY}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/>'
        f"<a:ln><a:noFill/></a:ln></p:spPr></p:pic>"
    )
    xml = xml.replace(
        "</p:txBody></p:sp><p:sp><p:nvSpPr><p:cNvPr id=\"116\"",
        f"</p:txBody></p:sp>{pic}<p:sp><p:nvSpPr><p:cNvPr id=\"116\"",
    )
    return xml


def renumber_up(from_n: int, to_n: int) -> None:
    for i in range(from_n, to_n - 1, -1):
        j = i + 1
        for src, dst in [
            (SLIDES / f"slide{i}.xml", SLIDES / f"slide{j}.xml"),
            (SLIDE_RELS / f"slide{i}.xml.rels", SLIDE_RELS / f"slide{j}.xml.rels"),
            (NOTES / f"notesSlide{i}.xml", NOTES / f"notesSlide{j}.xml"),
            (NOTES_RELS / f"notesSlide{i}.xml.rels", NOTES_RELS / f"notesSlide{j}.xml.rels"),
        ]:
            if src.exists():
                src.rename(dst)


def write_presentation(slide_count: int) -> None:
    sld_ids = "\n".join(
        f'    <p:sldId id="{255 + k}" r:id="rId{5 + k}"/>'
        for k in range(1, slide_count + 1)
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
    (SRC / "ppt/_rels/presentation.xml.rels").write_text(
        fixed
        + "".join(
            f'<Relationship Id="rId{5 + k}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{k}.xml"/>'
            for k in range(1, slide_count + 1)
        )
        + "</Relationships>\n"
    )
    base = (SRC / "[Content_Types].xml").read_text()
    base = re.sub(
        r"<Override ContentType=\"application/vnd\.openxmlformats-officedocument\.presentationml\.(slide|notesSlide)\+xml\" PartName=\"/ppt/(slides/slide|notesSlides/notesSlide)\d+\.xml\"/>",
        "",
        base,
    )
    ins = ""
    for k in range(1, slide_count + 1):
        ins += f'<Override ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml" PartName="/ppt/slides/slide{k}.xml"/>'
        ins += f'<Override ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml" PartName="/ppt/notesSlides/notesSlide{k}.xml"/>'
    (SRC / "[Content_Types].xml").write_text(base.replace("</Types>", ins + "</Types>"))


def main() -> None:
    if not NOTES_TPL.exists():
        raise SystemExit("Missing templateslides/_notesSlide2.xml - run unpack first")
    n = len(list(SLIDES.glob("slide*.xml")))
    renumber_up(n, 2)
    (SLIDES / "slide2.xml").write_text(build_slide_xml())
    (SLIDE_RELS / "slide2.xml.rels").write_text(SLIDE_RELS_TPL)
    shutil.copy(NOTES_TPL, NOTES / "notesSlide2.xml")
    (NOTES_RELS / "notesSlide2.xml.rels").write_text(NOTES_RELS_TPL)
    write_presentation(n + 1)
    print(f"Inserted slide 2: {TITLE!r}")
    print(f"Deck now has {n + 1} slides.")


if __name__ == "__main__":
    main()
