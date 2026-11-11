"""Separate title page (required for double-anonymous review) and cover letter, as DOCX (+PDF)."""
import json
import os
import subprocess
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))
MS = os.path.abspath(os.path.join(HERE, ".."))


def base(doc):
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(11)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.15


def title_page(v):
    d = Document(); base(d)
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(v["TITLE"]); r.bold = True; r.font.size = Pt(14)
    d.add_paragraph("Title page (not anonymised; submitted separately as required for double-anonymous peer review)").italic = True
    for k, t in [("Authors", "[Author 1 full name]¹*, [Author 2 full name]², …"),
                 ("Affiliations", "¹ [Department, Institution, City, Country]\n² [Department, Institution, City, Country]"),
                 ("Corresponding author", "* [Name], [e-mail address], ORCID: [16-digit ORCID]"),
                 ("Acknowledgements", "[To be completed by the authors, or 'Not applicable'.]"),
                 ("Funding", "The authors declare that no funds, grants or other support were received during the preparation of this manuscript. [Replace if applicable.]"),
                 ("Competing interests", "The authors have no relevant financial or non-financial interests to disclose. [Confirm.]"),
                 ("Author contributions", "[e.g. Conceptualisation: …; Methodology: …; Software: …; Formal analysis: …; Writing – original draft: …; Writing – review & editing: …]"),
                 ("Word count (main text)", v.get("WORD_COUNT", "")),
                 ("Number of figures / tables", f"{v.get('N_FIGS', '')} / {v.get('N_TABLES', '')}")]:
        p = d.add_paragraph(); p.add_run(k + ": ").bold = True; p.add_run(t)
    out = os.path.join(MS, "title_page.docx"); d.save(out); return out


def cover_letter(v):
    d = Document(); base(d)
    for line in ["[Date]", "", "The Editor-in-Chief", "Journal of King Saud University – Computer and Information Sciences",
                 "Springer Nature", ""]:
        d.add_paragraph(line)
    d.add_paragraph("Dear Editor,")
    for para in v["COVER_LETTER_PARAGRAPHS"]:
        d.add_paragraph(para)
    for line in ["", "Sincerely,", "", "[Corresponding author name]", "[Affiliation]", "[E-mail]", "[ORCID]"]:
        d.add_paragraph(line)
    out = os.path.join(MS, "cover_letter.docx"); d.save(out); return out


if __name__ == "__main__":
    v = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "values.json")))
    for f in (title_page(v), cover_letter(v)):
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", MS, f], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("built", f)
