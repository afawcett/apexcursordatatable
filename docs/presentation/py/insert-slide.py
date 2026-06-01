#!/usr/bin/env python3
"""Insert a new slide at position N, renumbering later slides."""
from __future__ import annotations

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


def count_slides() -> int:
    return len(list(SLIDES.glob("slide*.xml")))


def renumber_slides(from_idx: int, delta: int) -> None:
    """Move slideN and notesSlideN for N >= from_idx by delta (+1 insert)."""
    if delta == 0:
        return
    n = count_slides()
    order = range(n, from_idx - 1, -1) if delta > 0 else range(from_idx, n + 1)
    for i in order:
        src = i + delta if delta < 0 else i
        dst = i
        for folder, prefix in ((SLIDES, "slide"), (SLIDE_RELS, "slide"), (NOTES, "notesSlide"), (NOTES_RELS, "notesSlide")):
            old = folder / f"{prefix}{src}.xml"
            new = folder / f"{prefix}{dst}.xml"
            rel_old = folder / f"{prefix}{src}.xml.rels" if prefix == "slide" or "notes" in prefix else None
            if prefix in ("slide", "notesSlide") and (folder / f"{prefix}{src}.xml.rels").exists():
                rel_old = folder / f"{prefix}{src}.xml.rels"
            if old.exists():
                if new.exists():
                    raise SystemExit(f"collision: {new}")
                old.rename(new)
            rel_old_path = SLIDE_RELS / f"slide{src}.xml.rels"
            rel_new_path = SLIDE_RELS / f"slide{dst}.xml.rels"
            if rel_old_path.exists():
                rel_old_path.rename(rel_new_path)
            nrel_old = NOTES_RELS / f"notesSlide{src}.xml.rels"
            nrel_new = NOTES_RELS / f"notesSlide{dst}.xml.rels"
            if nrel_old.exists():
                nrel_old.rename(nrel_new)


def fix_notes_refs_in_slide_rels(slide_num: int) -> None:
    rel_path = SLIDE_RELS / f"slide{slide_num}.xml.rels"
    if rel_path.exists():
        text = rel_path.read_text()
        text = re.sub(r"notesSlide\d+\.xml", f"notesSlide{slide_num}.xml", text)
        rel_path.write_text(text)


def write_presentation_xml(slide_count: int) -> None:
    sld_ids = "\n".join(
        f'    <p:sldId id="{255 + i}" r:id="rId{5 + i}"/>'
        for i in range(1, slide_count + 1)
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" autoCompressPictures="0" saveSubsetFonts="1"><p:sldMasterIdLst><p:sldMasterId id="2147483659" r:id="rId4"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rId5"/></p:notesMasterIdLst><p:sldIdLst>
{sld_ids}
</p:sldIdLst><p:sldSz cy="6858000" cx="12188825"/><p:notesSz cx="7010400" cy="9296400"/></p:presentation>
"""
    (SRC / "ppt/presentation.xml").write_text(xml)


def write_presentation_rels(slide_count: int) -> None:
    fixed = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme2.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/><Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/><Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="notesMasters/notesMaster1.xml"/>"""
    slide_rels = "".join(
        f'<Relationship Id="rId{5 + i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, slide_count + 1)
    )
    (SRC / "ppt/_rels/presentation.xml.rels").write_text(
        fixed + slide_rels + "</Relationships>\n"
    )


def write_content_types(slide_count: int) -> None:
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
    for i in range(1, slide_count + 1):
        inserts += f'<Override ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml" PartName="/ppt/slides/slide{i}.xml"/>'
        inserts += f'<Override ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml" PartName="/ppt/notesSlides/notesSlide{i}.xml"/>'
    base = base.replace("</Types>", inserts + "</Types>")
    (SRC / "[Content_Types].xml").write_text(base)


def insert_at(position: int, slide_xml: Path, slide_rels_xml: Path, notes_xml: Path, notes_rels_xml: Path) -> None:
    n = count_slides()
    if position < 1 or position > n + 1:
        raise SystemExit(f"position must be 1..{n + 1}")
    # Rename slide14->15, ... slide2->3
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

    shutil.copy(slide_xml, SLIDES / f"slide{position}.xml")
    shutil.copy(slide_rels_xml, SLIDE_RELS / f"slide{position}.xml.rels")
    shutil.copy(notes_xml, NOTES / f"notesSlide{position}.xml")
    shutil.copy(notes_rels_xml, NOTES_RELS / f"notesSlide{position}.xml.rels")
    fix_notes_refs_in_slide_rels(position)

    total = n + 1
    write_presentation_xml(total)
    write_presentation_rels(total)
    write_content_types(total)
    print(f"Inserted slide at position {position}; deck now has {total} slides.")


if __name__ == "__main__":
    insert_at(int(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
