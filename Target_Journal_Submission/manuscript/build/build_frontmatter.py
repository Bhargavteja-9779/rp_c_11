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
    for k, t in [("Authors", "P N Bhargav Teja¹ and [Second Author Full Name]²*"),
                 ("Affiliations", "¹ [Department, Institution, City, Country]\n² [Department, Institution, City, Country]"),
                 ("Corresponding author", "* [Second Author Full Name], [Department, Institution, City, Country], "
                                          "e-mail: [corresponding.author@institution], ORCID: [0000-0000-0000-0000]"),
                 ("ORCID", "P N Bhargav Teja: [ORCID]; [Second Author Full Name]: [ORCID]"),
                 ("Acknowledgements", "Not applicable."),
                 ("Funding", "The authors declare that no funds, grants or other support were received during the preparation of this manuscript."),
                 ("Competing interests", "The authors have no relevant financial or non-financial interests to disclose."),
                 ("Author contributions", "P N Bhargav Teja: Conceptualisation, Methodology, Software, Investigation, Formal analysis, "
                                          "Data curation, Visualisation, Writing – original draft. [Second Author Full Name]: Supervision, "
                                          "Writing – review & editing. All authors read and approved the final manuscript."),
                 ("Data availability", "All datasets are public: UCR Time Series Classification Archive "
                                       "(https://www.cs.ucr.edu/~eamonn/time_series_data_2018/; https://www.timeseriesclassification.com/), "
                                       "PhysioNet/CinC Challenge 2012 (https://physionet.org/content/challenge-2012/1.0.0/) and the Case Western "
                                       "Reserve University Bearing Data Center (https://engineering.case.edu/bearingdatacenter)."),
                 ("Code availability", "The code, raw per-run results and analysis scripts are available from the corresponding author on reasonable request."),
                 ("Word count (main text)", v.get("WORD_COUNT", "")),
                 ("Number of figures / tables", f"{v.get('N_FIGS', '')} / {v.get('N_TABLES', '')}")]:
        p = d.add_paragraph(); p.add_run(k + ": ").bold = True; p.add_run(t)
    out = os.path.join(MS, "title_page.docx"); d.save(out); return out


def cover_letter(v):
    d = Document(); base(d)
    for line in [v.get("COVER_DATE", "[Date]"), "", "The Editor-in-Chief", "Journal of King Saud University – Computer and Information Sciences",
                 "Springer Nature", ""]:
        d.add_paragraph(line)
    d.add_paragraph("Dear Editor,")
    for para in v["COVER_LETTER_PARAGRAPHS"]:
        d.add_paragraph(para)
    for line in ["", "Sincerely, on behalf of all authors,", "", "[Second Author Full Name] (corresponding author)",
                 "[Department, Institution, City, Country]", "[corresponding.author@institution]", "ORCID: [0000-0000-0000-0000]"]:
        d.add_paragraph(line)
    out = os.path.join(MS, "cover_letter.docx"); d.save(out); return out


if __name__ == "__main__":
    v = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "values.json")))
    for f in (title_page(v), cover_letter(v)):
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", MS, f], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("built", f)
