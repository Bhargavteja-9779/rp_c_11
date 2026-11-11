"""Build the anonymised manuscript (DOCX + PDF), the separate title page and the cover letter.

Pipeline: source/*.md  --(citations from verified bibliography, {{VALUES}} from results, {{TABLE:..}} from
generated tables, figures from results)-->  build/manuscript_combined.md  --pandoc (native OMML equations)-->
DOCX  --python-docx (JKSU-CIS / Springer formatting)-->  Final_Manuscript.docx  --LibreOffice-->  PDF.
The build fails if any placeholder or citation key is unresolved.
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MS = os.path.abspath(os.path.join(HERE, ".."))
SRC = os.path.join(MS, "source")
ORDER = ["00_front.md", "01_intro.md", "02_related.md", "03_method.md", "05_setup.md", "06_results.md", "07_discussion.md",
         "08_conclusion.md"]


def load_refs():
    return json.load(open(os.path.join(HERE, "references_formatted.json")))


def cite(text, refs, used):
    def one(k):
        if k not in refs:
            raise KeyError(f"unknown citation key {k}")
        used.add(k)
        return refs[k]

    def par(m):
        ks = [x.strip().lstrip("@") for x in m.group(1).split(";")]
        items = sorted((one(k) for k in ks), key=lambda r: (r["cite"].lower(), r["year"]))
        return "(" + "; ".join(r["cite"] for r in items) + ")"
    text = re.sub(r"\[(@[A-Za-z0-9]+(?:\s*;\s*@[A-Za-z0-9]+)*)\]", par, text)

    def narr(m):
        r = one(m.group(1))
        name, yr = r["cite"].rsplit(" ", 1)
        return f"{name} ({yr})"
    text = re.sub(r"(?<![\w.])@([A-Z][A-Za-z0-9]+)", narr, text)
    return text


def fill(text, values):
    def rep(m):
        k = m.group(1)
        if k.startswith("TABLE:"):
            name = k.split(":", 1)[1]
            if name not in values.get("_tables", {}):
                raise KeyError("missing table " + name)
            return values["_tables"][name]
        if k not in values:
            raise KeyError("missing value " + k)
        return str(values[k])
    return re.sub(r"\{\{([A-Za-z0-9_:\-\.]+)\}\}", rep, text)


def number_floats(text):
    """Number figures/tables in order of first appearance of their labels {#fig:x} / {#tab:x}; replace refs."""
    figs, tabs = {}, {}
    for m in re.finditer(r"\{#(fig|tab):([A-Za-z0-9_\-]+)\}", text):
        d = figs if m.group(1) == "fig" else tabs
        d.setdefault(m.group(2), len(d) + 1)
    text = re.sub(r"\{#fig:([A-Za-z0-9_\-]+)\}", lambda m: f"**Fig. {figs[m.group(1)]}**", text)
    text = re.sub(r"\{#tab:([A-Za-z0-9_\-]+)\}", lambda m: f"**Table {tabs[m.group(1)]}**", text)
    text = re.sub(r"@fig:([A-Za-z0-9_\-]+)", lambda m: f"Fig. {figs[m.group(1)]}", text)
    text = re.sub(r"@tab:([A-Za-z0-9_\-]+)", lambda m: f"Table {tabs[m.group(1)]}", text)
    return text


def equations(text):
    return re.sub(r"\\tag\{(\d+)\}", r"\\qquad (\1)", text)


def reference_list(refs, used):
    items = sorted((refs[k] for k in used), key=lambda r: (r["entry"].lower()))
    return "## References\n\n" + "\n\n".join(r["entry"] for r in items) + "\n"


def postprocess(docx_in, docx_out, font="Times New Roman", size=10):
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, Cm
    doc = Document(docx_in)
    for st in doc.styles:
        try:
            if st.font is not None:
                st.font.name = font
                st.element.rPr.rFonts.set(qn("w:eastAsia"), font) if st.element.rPr is not None and st.element.rPr.rFonts is not None else None
        except Exception:
            pass
    by = {(st.name or "").lower(): st for st in doc.styles}
    for name in ["normal", "body text", "first paragraph", "compact", "bibliography"]:
        if name in by:
            s = by[name]
            s.font.size = Pt(size)
            s.font.name = font
            s.paragraph_format.line_spacing = 1.5
            s.paragraph_format.space_after = Pt(4)
    for lvl, sz in [(1, 14), (2, 12), (3, 11)]:
        n = f"heading {lvl}"
        if n in by:
            h = by[n]
            h.font.size = Pt(sz); h.font.bold = True; h.font.name = font
            h.font.color.rgb = None
    for sec in doc.sections:
        sec.top_margin = sec.bottom_margin = Cm(2.5)
        sec.left_margin = sec.right_margin = Cm(2.5)
        p = sec.footer.paragraphs[0] if sec.footer.paragraphs else sec.footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
            if tag:
                el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), tag); run._r.append(el)
            else:
                el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = txt; run._r.append(el)
    for tbl in doc.tables:
        tblPr = tbl._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for b in ("top", "bottom", "insideH"):
            e = OxmlElement(f"w:{b}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), "000000")
            borders.append(e)
        tblPr.append(borders)
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.line_spacing = 1.0
                    p.paragraph_format.space_after = Pt(0)
                    for r in p.runs:
                        r.font.size = Pt(8)
                        r.font.name = font
    # captions: paragraphs starting with "Fig. n" / "Table n" (bold already) -> keep with next, 9 pt
    for p in doc.paragraphs:
        t = p.text
        if re.match(r"^(Fig\.|Table) \d+ ", t):
            for r in p.runs:
                r.font.size = Pt(9)
            p.paragraph_format.keep_with_next = t.startswith("Table")
            p.paragraph_format.line_spacing = 1.0
    doc.save(docx_out)


def to_pdf(docx, outdir):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, docx], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)


def build(values_path, outdir, sources=ORDER, name="Final_Manuscript"):
    refs = load_refs()
    values = json.load(open(values_path)) if os.path.exists(values_path) else {"_tables": {}}
    used = set()
    parts = []
    for f in sources:
        p = os.path.join(SRC, f)
        if os.path.exists(p):
            parts.append(open(p, encoding="utf-8").read())
    text = "\n\n".join(parts)
    text = fill(text, values)
    text = cite(text, refs, used)
    text = number_floats(text)
    text = equations(text)
    decl = os.path.join(SRC, "09_declarations.md")
    text += "\n\n" + reference_list(refs, used)
    if os.path.exists(decl):
        text += "\n\n" + fill(open(decl, encoding="utf-8").read(), values)
    left = re.findall(r"\{\{[^}]+\}\}|(?<![\w.])@[A-Z][A-Za-z0-9]+", text)
    if left:
        raise RuntimeError(f"unresolved: {left[:10]}")
    os.makedirs(outdir, exist_ok=True)
    md = os.path.join(HERE, f"{name}_combined.md")
    open(md, "w", encoding="utf-8").write(text)
    raw = os.path.join(HERE, f"{name}_raw.docx")
    subprocess.run(["pandoc", md, "-f", "markdown+tex_math_dollars+pipe_tables+implicit_figures", "-o", raw,
                    "--resource-path", ":".join([MS, os.path.join(MS, "..", "code")])], check=True)
    out = os.path.join(outdir, f"{name}.docx")
    postprocess(raw, out)
    to_pdf(out, outdir)
    unused = sorted(set(refs) - used)
    return out, unused


if __name__ == "__main__":
    vals = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "values.json")
    out, unused = build(vals, os.path.join(MS))
    print("built", out)
    print("references in bibliography but not cited (excluded from list):", unused)
