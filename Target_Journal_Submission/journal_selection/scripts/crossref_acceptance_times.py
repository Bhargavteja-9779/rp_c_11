"""Compute received->accepted medians from Crossref 'assertion' metadata
(deposited by Springer Nature, Taylor & Francis and some others).
Usage: python crossref_acceptance_times.py "Title|ISSN;Title|ISSN" from_date out.csv
"""
import sys, json, time, statistics, csv, urllib.request, urllib.parse
from dateutil import parser as dp

def get(url):
    for k in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "journal-timeline-study/0.1 (research script)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception:
            time.sleep(2 ** k)
    raise RuntimeError(url)

def run(title, issn, from_date, until_date, rows=300):
    q = urllib.parse.urlencode({"rows": rows, "filter": f"from-pub-date:{from_date},until-pub-date:{until_date},type:journal-article",
                                "select": "DOI,assertion,title", "sort": "published", "order": "desc"})
    items = get(f"https://api.crossref.org/journals/{issn}/works?{q}")["message"]["items"]
    days = []
    for it in items:
        a = {x.get("name", "").lower(): x.get("value") for x in it.get("assertion", []) if x.get("value")}
        rec = a.get("received") or a.get("received_date") or a.get("submitted")
        acc = a.get("accepted") or a.get("accepted_date")
        if rec and acc:
            try:
                dd = (dp.parse(acc) - dp.parse(rec)).days
                if dd >= 0: days.append(dd)
            except Exception:
                pass
    if len(days) >= 4:
        qq = statistics.quantiles(days, n=4)
        return dict(journal=title, issn=issn, n_sampled=len(items), n_with_dates=len(days), median_days=statistics.median(days),
                    q1=qq[0], q3=qq[2], pct_le60=round(100*sum(x<=60 for x in days)/len(days),1), pct_le72=round(100*sum(x<=72 for x in days)/len(days),1))
    return dict(journal=title, issn=issn, n_sampled=len(items), n_with_dates=len(days), median_days=None, q1=None, q3=None, pct_le60=None, pct_le72=None)

if __name__ == "__main__":
    specs = [s.split("|") for s in sys.argv[1].split(";")]
    out = []
    for t, i in specs:
        r = run(t, i, sys.argv[2], sys.argv[3]); print(r, flush=True); out.append(r)
    with open(sys.argv[4], "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
