"""Compute submission(received)->acceptance medians from PubMed article history.

For each journal (NLM title abbreviation), sample recent journal articles
published in a date window, fetch PubMed XML, and read
<PubMedPubDate PubStatus="received"> and <PubMedPubDate PubStatus="accepted">.
Output: CSV with n, median, IQR, % <=60d, % <=72d.
"""
import csv, sys, time, statistics, datetime as dt, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def get(url):
    for k in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception as e:
            time.sleep(2 ** k)
    raise RuntimeError(url)

def esearch(journal, mindate, maxdate, retmax=200):
    term = f'"{journal}"[ta] AND journal article[pt] NOT review[pt] NOT editorial[pt]'
    q = urllib.parse.urlencode(dict(db="pubmed", term=term, mindate=mindate, maxdate=maxdate,
                                    datetype="pdat", retmax=retmax, retmode="json", sort="pub_date"))
    import json
    return json.loads(get(EUTILS + "esearch.fcgi?" + q))["esearchresult"]["idlist"]

def d(node):
    try:
        return dt.date(int(node.findtext("Year")), int(node.findtext("Month")), int(node.findtext("Day")))
    except Exception:
        return None

def history(ids):
    out = []
    for i in range(0, len(ids), 100):
        q = urllib.parse.urlencode(dict(db="pubmed", id=",".join(ids[i:i+100]), retmode="xml"))
        root = ET.fromstring(get(EUTILS + "efetch.fcgi?" + q))
        for art in root.findall(".//PubmedArticle"):
            pmid = art.findtext(".//PMID")
            rec = acc = None
            for p in art.findall(".//History/PubMedPubDate"):
                if p.get("PubStatus") == "received": rec = d(p)
                if p.get("PubStatus") == "accepted": acc = d(p)
            if rec and acc and acc >= rec:
                out.append((pmid, rec, acc, (acc - rec).days))
        time.sleep(0.4)
    return out

if __name__ == "__main__":
    journals = sys.argv[1].split(";")
    mindate, maxdate, outcsv = sys.argv[2], sys.argv[3], sys.argv[4]
    rows = []
    for j in journals:
        ids = esearch(j, mindate, maxdate)
        h = history(ids)
        days = sorted(x[3] for x in h)
        if days:
            q = statistics.quantiles(days, n=4)
            row = dict(journal=j, n_sampled=len(ids), n_with_dates=len(days), median_days=statistics.median(days),
                       q1=q[0], q3=q[2], pct_le60=round(100*sum(x<=60 for x in days)/len(days),1),
                       pct_le72=round(100*sum(x<=72 for x in days)/len(days),1))
        else:
            row = dict(journal=j, n_sampled=len(ids), n_with_dates=0, median_days=None, q1=None, q3=None, pct_le60=None, pct_le72=None)
        print(row, flush=True)
        rows.append(row)
    with open(outcsv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
