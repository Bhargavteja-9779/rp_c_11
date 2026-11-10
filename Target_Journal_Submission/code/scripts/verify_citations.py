"""Verify every DOI reference against Crossref and every arXiv reference against the arXiv API.

Input: manuscript/references.json  (list of {key, doi | arxiv, expected_title_fragment})
Output: supplementary/citation_audit.csv with retrieved title/authors/year/venue.
"""
import json, sys, time, csv, urllib.request, urllib.parse, re, xml.etree.ElementTree as ET

def get(url, as_json=True):
    for k in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "citation-audit/0.1 (research script)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
                return json.loads(b) if as_json else b
        except Exception as e:
            err = e; time.sleep(2 ** k)
    return {"error": str(err)}

def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())

refs = json.load(open(sys.argv[1]))
out = []
for r in refs:
    row = dict(key=r["key"], id=r.get("doi") or r.get("arxiv"), expected=r["title"])
    if r.get("doi"):
        d = get("https://api.crossref.org/works/" + urllib.parse.quote(r["doi"]))
        if "message" in d:
            m = d["message"]
            row.update(found_title=(m.get("title") or [""])[0], year=(m.get("issued", {}).get("date-parts") or [[None]])[0][0],
                       venue=(m.get("container-title") or [""])[0] or m.get("publisher", ""),
                       first_author=(m.get("author") or [{}])[0].get("family", ""),
                       authors="; ".join(f"{a.get('family','')} {a.get('given','')}".strip() for a in m.get("author", [])),
                       volume=m.get("volume", ""), issue=m.get("issue", ""), pages=m.get("page", "") or m.get("article-number", ""))
        else:
            row.update(found_title="NOT FOUND", error=d.get("error"))
    else:
        b = get("http://export.arxiv.org/api/query?id_list=" + r["arxiv"], as_json=False)
        try:
            ns = {"a": "http://www.w3.org/2005/Atom"}
            e = ET.fromstring(b).find("a:entry", ns)
            row.update(found_title=" ".join(e.find("a:title", ns).text.split()), year=e.find("a:published", ns).text[:4],
                       venue="arXiv", first_author=e.find("a:author/a:name", ns).text.split()[-1],
                       authors="; ".join(a.find("a:name", ns).text for a in e.findall("a:author", ns)))
        except Exception as ex:
            row.update(found_title="NOT FOUND", error=str(ex))
        time.sleep(3)
    row["title_match"] = norm(r["title"])[:40] in norm(row.get("found_title", "")) or norm(row.get("found_title", ""))[:40] in norm(r["title"])
    out.append(row); print(row["key"], row["title_match"], "|", row.get("found_title", "")[:90], "|", row.get("year"), row.get("venue", "")[:40], flush=True)
keys = sorted({k for r in out for k in r})
with open(sys.argv[2], "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(out)
