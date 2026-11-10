# Journal Comparison (Phase 0)

## Method
Time to acceptance was **measured**, not taken from marketing pages or aggregators:

* **PubMed** (`scripts/pubmed_acceptance_times.py`): we took up to 200 journal articles (excluding reviews and editorials) published from 2025-07-01 to 2026-10-31. For each, we parsed `<PubMedPubDate PubStatus="received">` and `PubStatus="accepted"`.
* **Crossref** (`scripts/crossref_acceptance_times.py`): we took up to 300 most-recent journal articles over the same window and parsed the publisher-deposited `received` and `accepted` assertions. Springer Nature, Taylor & Francis and Wiley deposit these; Elsevier, IOP and OUP do not.

Outputs are **submission (received) → acceptance** intervals for *accepted* papers. These are neither first-decision times nor acceptance rates.

Full sorted table (79 journals with ≥20 dated articles): `data/combined_sorted.md`.

## Shortlist evaluated in depth (≥10 candidates)

| # | Journal | Publisher | JIF (source) | Median rec→acc (d) | ≤72 d share | Scope fit for an ML/TSC method paper | Decision |
|---|---|---|---|---|---|---|---|
| 1 | **JKSU-CIS** | Springer Nature | 6.4 (publisher page, 2025) | **66** (IQR 53–91) | 57% | Strong: ML, signal processing, pattern recognition listed | **SELECTED** |
| 2 | Frontiers in Physiology | Frontiers | not verified | 62.5 | 62% | Weak: physiology journal | Rejected (scope) |
| 3 | Int. J. Information Technology | Springer | not verified; Q1 JCR not established | 70.5 | 58% | Moderate | Rejected (JCR Q1 unverified) |
| 4 | Bioinformatics | OUP | not verified here | 156 | 0.5% | Weak (no biology) | Rejected (timeline) |
| 5 | Briefings in Bioinformatics | OUP | not verified here | 120 | 14% | Weak | Rejected (timeline) |
| 6 | JAMIA | OUP | not verified here | 118 | 19% | Weak | Rejected (timeline) |
| 7 | Eur. Heart J. – Digital Health | OUP | not verified here | 117.5 | 11% | Weak | Rejected (timeline) |
| 8 | J. Computational Design & Engineering | OUP | ≈6.8 (secondary) | **unverifiable** (no deposited dates; pages blocked) | — | Moderate | Rejected (timeline unverifiable) |
| 9 | Computers in Biology and Medicine | Elsevier | not verified here | 113 | 21% | Moderate | Rejected (timeline) |
| 10 | Scientific Reports | Springer Nature | not verified here | 131–136.5 | 14% | Moderate | Rejected (timeline) |
| 11 | Expert Systems with Applications | Elsevier | not verified here | 147–187 (third-party) | — | Strong | Rejected (timeline) |
| 12 | Engineering Applications of AI / Results in Engineering / Knowledge-Based Systems | Elsevier | not verified here | **unverifiable** (ScienceDirect blocked automated access) | — | Strong | Rejected (timeline unverifiable) |
| 13 | Complex & Intelligent Systems | Springer | not verified here | 152 | 7% | Strong | Rejected (timeline) |
| 14 | Journal of Big Data | Springer | not verified here | 238 | 2% | Strong | Rejected (timeline) |
| 15 | Neural Computing & Applications / Applied Intelligence | Springer | not verified here | 239 / 230 | ≈1% | Strong | Rejected (timeline) |
| 16 | Data Mining & Knowledge Discovery / Machine Learning | Springer | not verified here | 253 / 204 | ≈2–8% | Very strong (TSC venue) | Rejected (timeline) |
| 17 | Int. J. Medical Informatics | Elsevier | not verified here | 84.5 | 40% | Weak | Rejected (timeline > 72) |
| 18 | Expert Systems; Int. J. Intelligent Systems | Wiley | not verified here | 168 / 161.5 | ≈6–11% | Strong | Rejected (timeline) |

"not verified here": we did not open a primary JIF source for that journal because it was already excluded on timeline or scope. We report no JIF that we did not read from a primary source.

## Reviewer expectations at JKSU-CIS (inferred from guidelines and recent articles)
* A clear methodological contribution beyond an applied pipeline.
* Comparison with recent, strong baselines.
* Multiple datasets.
* Ablations.
* Statistical significance across datasets.
* Complexity and runtime analysis.
* Code and data availability.

Review is double-anonymous with two referees plus an Associate Editor.
