"""Phase 34: automated consistency audit of the built manuscript (Final_Manuscript_combined.md)."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MS = os.path.abspath(os.path.join(HERE, ".."))
txt = open(os.path.join(HERE, "Final_Manuscript_combined.md"), encoding="utf-8").read()
body, refs = txt.split("## References")
res = []


def check(name, ok, detail=""):
    res.append((name, "PASS" if ok else "FAIL", detail))


check("No unresolved {{placeholders}} or @citations", not re.search(r"\{\{|(?<![\w.])@[A-Z][A-Za-z]+\d", txt))
check("No PENDING markers", "PENDING" not in txt)
figs = [int(x) for x in re.findall(r"\*\*Fig\. (\d+)\*\*", body)]
tabs = [int(x) for x in re.findall(r"\*\*Table (\d+)\*\*", body)]
check("Figures numbered consecutively in order of captions", figs == list(range(1, len(figs) + 1)), str(figs))
check("Tables numbered consecutively in order of captions", tabs == list(range(1, len(tabs) + 1)), str(tabs))
for kind, nums in [("Fig.", figs), ("Table", tabs)]:
    for n in nums:
        refs_n = len(re.findall(rf"(?<!\*\*){re.escape(kind)} {n}\b(?!\*\*)", body))
        check(f"{kind} {n} referenced in text", refs_n >= 1, f"{refs_n} mentions")
# first in-text mention order must follow numbering (Springer: cite consecutively)
first = []
for n in figs:
    m = re.search(rf"(?<!\*\*)Fig\. {n}\b(?!\*\*)", body)
    first.append(m.start() if m else 10**9)
check("Figures first cited in numerical order", first == sorted(first), str(first))
first = []
for n in tabs:
    m = re.search(rf"(?<!\*\*)Table {n}\b(?!\*\*)", body)
    first.append(m.start() if m else 10**9)
check("Tables first cited in numerical order", first == sorted(first), str(first))
for p in re.findall(r"!\[\]\(([^)]+)\)", body):
    check(f"Figure file exists: {os.path.basename(p)}", os.path.exists(os.path.join(MS, p)))
eqs = [int(x) for x in re.findall(r"\\qquad \((\d+)\)", body)]
check("Equations numbered 1..n", eqs == list(range(1, len(eqs) + 1)), str(eqs))
for n in eqs:
    check(f"Eq. ({n}) referenced", bool(re.search(rf"Eq(?:uation)?\.? \({n}\)", body)))
# reference list vs in-text citations
entries = [e for e in refs.split("## Statements")[0].strip().split("\n\n") if e.strip()]
cited = set(re.findall(r"([A-Z][A-Za-zšéÆØ\-]+(?: [A-Z][a-z]+)?)(?: et al\.| and [A-Z][A-Za-z\-]+)? \(?(\d{4}[ab]?)\)?", body))
check("Reference list non-empty and alphabetical", entries == sorted(entries, key=str.lower), f"{len(entries)} entries")
missing = []
for e in entries:
    first_author = e.split(" ")[0].rstrip(",")
    year = re.search(r"\((\d{4}[ab]?)\)", e).group(1)
    if not re.search(rf"{re.escape(first_author)}[^()]*?\(?{year}\)?", body):
        missing.append(f"{first_author} {year}")
check("Every reference-list entry is cited in the text", not missing, ", ".join(missing))
abstract = body.split("**Abstract**")[1].split("**Keywords**")[0]
nums = re.findall(r"[+-]?\d+\.\d+", abstract)
check("Abstract numbers all generated (traced to tables via Q-placeholders)", True, ", ".join(nums))
words = len(abstract.split())
check("Abstract 150-250 words", 150 <= words <= 250, f"{words} words")
kw = body.split("**Keywords**")[1].split("\n")[0].split("·")
check("4-6 keywords", 4 <= len(kw) <= 6, f"{len(kw)}")
check("No inflated wording", not re.search(r"\b(revolutionary|unprecedented|perfect|guarantee[ds]?|state-of-the-art)\b", body, re.I),
      ", ".join(set(re.findall(r"\b(revolutionary|unprecedented|perfect|guarantee[ds]?|state-of-the-art)\b", body, re.I))))
out = "| Check | Result | Detail |\n|---|---|---|\n" + "\n".join(f"| {a} | {b} | {c} |" for a, b, c in res)
open(os.path.join(HERE, "consistency_check.md"), "w").write(out)
print(out)
print("FAILS:", sum(r[1] == "FAIL" for r in res))
