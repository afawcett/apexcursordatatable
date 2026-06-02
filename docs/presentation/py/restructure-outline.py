#!/usr/bin/env python3
"""Rebuild deck: keep title + Q&A + thank-you; insert basic-layout outline slides."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

PRES = Path(__file__).resolve().parent.parent
SRC = PRES / "src"
SLIDES = SRC / "ppt/slides"
SLIDE_RELS = SLIDES / "_rels"
NOTES = SRC / "ppt/notesSlides"
NOTES_RELS = NOTES / "_rels"
TPL_SLIDE = PRES / "templateslides/basic-layout.xml"

SLIDE_RELS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout2.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide{n}.xml"/></Relationships>
"""

NOTES_TEMPLATE = (PRES / "templateslides" / "_notesSlide2.xml")
NOTES_RELS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/></Relationships>
"""

OUTLINE_TITLES = [
    "Accessing and processing datasets today in SOQL",
    "What is a SQL Cursor?",
    "What is a SOQL Cursor?",
    "Usecases for Apex Cursors",
    "Demo 1: Virtual Data Table",
    "Demo 1: Virtual Data Table Summary",
    "Demo 2: Interactive Reporting and Drilldown",
    "Demo 2: Interactive Reporting and Drilldown Summary",
    "Demo 3: Adaptive Async",
    "Demo 3: Adaptive Async Summary",
    "Usage Best Practices",
    "Limits",
    "Other Use Cases",
]

SLIDE_COUNT = 1 + len(OUTLINE_TITLES) + 2  # title + outline + qa + thank-you


def set_slide_title(xml: str, title: str) -> str:
    title_esc = (
        title.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    xml, n = re.subn(
        r"(<p:ph type=\"title\"/>.*?<a:t>)([^<]*)(</a:t>)",
        rf"\1{title_esc}\3",
        xml,
        count=1,
        flags=re.DOTALL,
    )
    if n != 1:
        raise ValueError(f"Could not set title to {title!r}")
    xml = re.sub(
        r"(<p:ph idx=\"1\" type=\"body\"/>.*?<a:t>)([^<]*)(</a:t>)",
        r"\1\3",
        xml,
        count=1,
        flags=re.DOTALL,
    )
    return xml


def write_slide_rels(n: int) -> None:
    (SLIDE_RELS / f"slide{n}.xml.rels").write_text(
        SLIDE_RELS_TEMPLATE.format(n=n)
    )


def write_notes(n: int) -> None:
    shutil.copy(NOTES_TEMPLATE, NOTES / f"notesSlide{n}.xml")
    (NOTES_RELS / f"notesSlide{n}.xml.rels").write_text(NOTES_RELS_TEMPLATE)


def write_presentation_xml() -> None:
    sld_ids = "\n".join(
        f'    <p:sldId id="{255 + i}" r:id="rId{5 + i}"/>'
        for i in range(1, SLIDE_COUNT + 1)
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:mv="urn:schemas-microsoft-com:mac:vml" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:dgm="http://schemas.openxmlformats.org/drawingml/2006/diagram" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:pvml="urn:schemas-microsoft-com:office:powerpoint" xmlns:com="http://schemas.openxmlformats.org/drawingml/2006/compatibility" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" xmlns:p15="http://schemas.microsoft.com/office/powerpoint/2012/main" xmlns:ahyp="http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor" autoCompressPictures="0" strictFirstAndLastChars="0" saveSubsetFonts="1"><p:sldMasterIdLst><p:sldMasterId id="2147483659" r:id="rId4"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rId5"/></p:notesMasterIdLst><p:sldIdLst>
{sld_ids}
</p:sldIdLst><p:sldSz cy="6858000" cx="12188825"/><p:notesSz cx="7010400" cy="9296400"/></p:presentation>
"""
    (SRC / "ppt/presentation.xml").write_text(xml)


def write_presentation_rels() -> None:
    fixed = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme2.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/><Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/><Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="notesMasters/notesMaster1.xml"/>"""
    slide_rels = "".join(
        f'<Relationship Id="rId{5 + i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, SLIDE_COUNT + 1)
    )
    (SRC / "ppt/_rels/presentation.xml.rels").write_text(
        fixed + slide_rels + "</Relationships>\n"
    )


def write_content_types() -> None:
    base = Path(SRC / "[Content_Types].xml").read_text()
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
    for i in range(1, SLIDE_COUNT + 1):
        inserts += f'<Override ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml" PartName="/ppt/slides/slide{i}.xml"/>'
        inserts += f'<Override ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml" PartName="/ppt/notesSlides/notesSlide{i}.xml"/>'
    base = base.replace("</Types>", inserts + "</Types>")
    Path(SRC / "[Content_Types].xml").write_text(base)


def main() -> None:
    global NOTES_TEMPLATE
    if not NOTES_TEMPLATE.exists():
        NOTES_TEMPLATE = NOTES / "notesSlide2.xml"
    if not NOTES_TEMPLATE.exists():
        raise SystemExit("Run unpack first, or add templateslides/_notesSlide2.xml")

    qa_src = PRES / "templateslides/qa.xml"
    thank_src = PRES / "templateslides/thank-you.xml"
    qa_rels_text = (SLIDE_RELS / "slide10.xml.rels").read_text()
    thank_rels_text = (SLIDE_RELS / "slide11.xml.rels").read_text()
    qa_notes_bytes = (NOTES / "notesSlide10.xml").read_bytes()
    qa_notes_rels_bytes = (NOTES_RELS / "notesSlide10.xml.rels").read_bytes()
    thank_notes_bytes = (NOTES / "notesSlide11.xml").read_bytes()
    thank_notes_rels_bytes = (NOTES_RELS / "notesSlide11.xml.rels").read_bytes()

    # Remove old slide parts (keep slide1 for now)
    for path in list(SLIDES.glob("slide*.xml")):
        if path.name != "slide1.xml":
            path.unlink()
    for path in list(SLIDE_RELS.glob("slide*.xml.rels")):
        if path.name != "slide1.xml.rels":
            path.unlink()
    for path in list(NOTES.glob("notesSlide*.xml")):
        if path.name != "notesSlide1.xml":
            path.unlink()
    for path in list(NOTES_RELS.glob("notesSlide*.xml.rels")):
        if path.name != "notesSlide1.xml.rels":
            path.unlink()

    tpl = TPL_SLIDE.read_text()
    for idx, title in enumerate(OUTLINE_TITLES, start=2):
        (SLIDES / f"slide{idx}.xml").write_text(set_slide_title(tpl, title))
        write_slide_rels(idx)
        write_notes(idx)

    qa_num = SLIDE_COUNT - 1
    thank_num = SLIDE_COUNT
    shutil.copy(qa_src, SLIDES / f"slide{qa_num}.xml")
    shutil.copy(thank_src, SLIDES / f"slide{thank_num}.xml")
    qa_rel = re.sub(r"notesSlide\d+\.xml", f"notesSlide{qa_num}.xml", qa_rels_text)
    thank_rel = re.sub(
        r"notesSlide\d+\.xml", f"notesSlide{thank_num}.xml", thank_rels_text
    )
    (SLIDE_RELS / f"slide{qa_num}.xml.rels").write_text(qa_rel)
    (SLIDE_RELS / f"slide{thank_num}.xml.rels").write_text(thank_rel)
    (NOTES / f"notesSlide{qa_num}.xml").write_bytes(qa_notes_bytes)
    (NOTES_RELS / f"notesSlide{qa_num}.xml.rels").write_bytes(qa_notes_rels_bytes)
    (NOTES / f"notesSlide{thank_num}.xml").write_bytes(thank_notes_bytes)
    (NOTES_RELS / f"notesSlide{thank_num}.xml.rels").write_bytes(
        thank_notes_rels_bytes
    )

    write_presentation_xml()
    write_presentation_rels()
    write_content_types()

    print(f"Deck restructured: {SLIDE_COUNT} slides")
    print("  slide1: title (unchanged)")
    for i, t in enumerate(OUTLINE_TITLES, start=2):
        print(f"  slide{i}: {t}")
    print(f"  slide{qa_num}: Q&A")
    print(f"  slide{thank_num}: Thank You")


if __name__ == "__main__":
    main()
