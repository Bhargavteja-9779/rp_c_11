"""Fetch verified metadata for every reference (Crossref / arXiv / PubMed / manual-verified) and format
Springer Basic (author-year) entries. Output: build/references_formatted.json  {key: {cite, entry, ...}}.
Metadata is cached in build/ref_cache.json so the bibliography is reproducible offline."""
import html as _html
import json, os, re, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET

PARTICLES = {"le", "van", "de", "von", "da", "di", "la", "der", "den", "du"}

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "ref_cache.json")


def get(url, js=True):
    for k in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "citation-builder/0.1 (research script)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
                return json.loads(b) if js else b
        except Exception:
            time.sleep(2 ** k)
    raise RuntimeError(url)


def initials(given):
    parts = re.split(r"[\s\-]+", given.strip()) if given else []
    out = "".join(p[0] for p in parts if p and p[0].isalpha())
    return out


def fetch(x):
    if "manual" in x:
        m = dict(x["manual"]); m["source"] = "manual (verified: %s)" % m.get("url", "")
        return m
    if x.get("doi"):
        m = get("https://api.crossref.org/works/" + urllib.parse.quote(x["doi"]))["message"]
        typ = m.get("type")
        title = (m.get("title") or [""])[0]
        if m.get("subtitle"):
            title = f"{title}: {m['subtitle'][0]}"
        year = ((m.get("published-print") or m.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        conts = m.get("container-title") or [""]
        venue = [c for c in conts if c != "Lecture Notes in Computer Science"] or conts
        return dict(authors=[[a.get("family", ""), initials(a.get("given", ""))] for a in m.get("author", [])],
                    editors=[[a.get("family", ""), initials(a.get("given", ""))] for a in m.get("editor", [])],
                    year=year, title=title,
                    venue=venue[-1], volume=m.get("volume", ""), issue=m.get("issue", ""),
                    pages=m.get("page", "") or m.get("article-number", ""), doi=x["doi"], type=typ,
                    publisher=m.get("publisher", ""), source="crossref")
    if x.get("arxiv"):
        b = get("http://export.arxiv.org/api/query?id_list=" + x["arxiv"], js=False)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        e = ET.fromstring(b).find("a:entry", ns)
        names = [a.find("a:name", ns).text for a in e.findall("a:author", ns)]
        auth = []
        for n in names:
            tok = n.split()
            k = len(tok) - 1
            while k > 0 and tok[k - 1].lower() in PARTICLES:
                k -= 1
            auth.append([" ".join(tok[k:]), initials(" ".join(tok[:k]))])
        time.sleep(3)
        return dict(authors=auth, year=int(e.find("a:published", ns).text[:4]), title=" ".join(e.find("a:title", ns).text.split()),
                    arxiv=x["arxiv"], type="arxiv", source="arxiv")
    if x.get("pmid"):
        d = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + x["pmid"])["result"][x["pmid"]]
        auth = [[a["name"].split()[0], a["name"].split()[1] if len(a["name"].split()) > 1 else ""] for a in d["authors"]]
        return dict(authors=auth, year=int(d["pubdate"][:4]), title=d["title"].rstrip("."), venue="Computing in Cardiology",
                    volume=d["volume"], pages=d["pages"], pmid=x["pmid"], type="journal-article", source="pubmed")
    raise ValueError(x["key"])


def _clean(m):
    for k in ("title", "venue", "publisher"):
        if m.get(k):
            m[k] = _html.unescape(m[k])
    m["authors"] = [[f.title() if f.isupper() and len(f) > 2 else f, i] for f, i in m["authors"]]
    return m


def _t(title):
    title = title.strip()
    return title if title[-1] in "?!." else title + "."


def fmt_authors(a, etal=False):
    names = [f"{f} {i}".strip() for f, i in a]
    if len(names) > 10:
        names, etal = names[:3], True
    s = ", ".join(names)
    return s + (" et al" if etal else "")


def cite_name(a, year, suffix=""):
    if len(a) == 1:
        return f"{a[0][0]} {year}{suffix}"
    if len(a) == 2:
        return f"{a[0][0]} and {a[1][0]} {year}{suffix}"
    return f"{a[0][0]} et al. {year}{suffix}"


def entry(m):
    au = fmt_authors(m["authors"], m.get("etal", False))
    y = m["year"]
    t = _t(m["title"])[:-1] if _t(m["title"]).endswith(".") else _t(m["title"])
    if m.get("type") == "arxiv":
        return f"{au} ({y}) {_t(t)} arXiv:{m['arxiv']}. https://doi.org/10.48550/arXiv.{m['arxiv']}"
    if m.get("type") == "book" or m.get("type") == "monograph":
        return f"{au} ({y}) {_t(t)} {m.get('publisher', '')}. https://doi.org/{m['doi']}"
    if m.get("type") in ("proceedings-article", "book-chapter") or m.get("proceedings"):
        s = f"{au} ({y}) {_t(t)} In: {m.get('venue', '')}"
        if m.get("pages"):
            s += f", pp {m['pages'].replace('-', '–')}"
        if m.get("doi"):
            s += f". https://doi.org/{m['doi']}"
        elif m.get("url"):
            s += f". {m['url']}"
        return s
    s = f"{au} ({y}) {_t(t)} {m.get('venue', '')}"
    if m.get("volume"):
        s += f" {m['volume']}"
        if m.get("issue") and not m.get("pages"):
            s += f"({m['issue']})"
    if m.get("pages"):
        s += f":{str(m['pages']).replace('-', '–')}"
    if m.get("doi"):
        s += f". https://doi.org/{m['doi']}"
    elif m.get("url"):
        s += f". {m['url']}"
    elif m.get("pmid"):
        s += f". PMID: {m['pmid']}"
    return s


def main():
    refs = json.load(open(os.path.join(HERE, "..", "references.json")))
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    for x in refs:
        if x["key"] not in cache:
            cache[x["key"]] = fetch(x)
            print("fetched", x["key"], flush=True)
    json.dump(cache, open(CACHE, "w"), indent=1, ensure_ascii=False)
    out = {}
    for x in refs:
        m = _clean(dict(cache[x["key"]]))
        out[x["key"]] = dict(entry=entry(m), first=m["authors"][0][0], year=m["year"], authors=m["authors"])
    # disambiguate identical author-year citations with a/b suffixes (alphabetical by title)
    groups = {}
    for k, v in out.items():
        groups.setdefault(cite_name(v["authors"], v["year"]), []).append(k)
    for c, ks in groups.items():
        ks = sorted(ks, key=lambda k: cache[k]["title"].lower())
        for i, k in enumerate(ks):
            suf = "abcdefgh"[i] if len(ks) > 1 else ""
            out[k]["cite"] = cite_name(out[k]["authors"], out[k]["year"], suf)
            if suf:
                out[k]["entry"] = re.sub(r"\((\d{4})\)", rf"(\g<1>{suf})", out[k]["entry"], count=1)
    json.dump(out, open(os.path.join(HERE, "references_formatted.json"), "w"), indent=1, ensure_ascii=False)
    for k, v in sorted(out.items(), key=lambda kv: kv[1]["entry"].lower()):
        print(f"[{v['cite']}] {v['entry']}")


if __name__ == "__main__":
    main()
