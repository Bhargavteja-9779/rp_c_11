# Selected Target Journal

Decision date: 2026-11-10. Evidence files are in `data/` and the scripts that produced them are in `scripts/`.

| Field | Value | Evidence / verification status |
|---|---|---|
| TARGET JOURNAL | **Journal of King Saud University – Computer and Information Sciences (JKSU-CIS)** | Springer Nature journal page `link.springer.com/journal/44443` (copy: `data/page_home.txt`) |
| PUBLISHER | Springer Nature, on behalf of King Saud University. The journal moved from Elsevier to Springer Nature in 2025. | Journal page, "Societies and partnerships: King Saud University" |
| ISSN | eISSN 2213-1248; print ISSN 1319-1578 ("regulatory purposes") | Journal page |
| JCR STATUS | Indexed in SCIE/JCR. The publisher page shows a Clarivate Journal Impact Factor. | Publisher page shows "Journal Impact Factor 6.4 (2025)". A King Saud University news release lists the journal as WoS-indexed and Q1. |
| JCR QUARTILE | **Q1 (secondary evidence; see note)** | Clarivate JCR needs a subscription and could not be opened from this environment. Q1 is reported by King Saud University (news.ksu.edu.sa, 2024 indexing announcement) and Peeref (2023 JCR). The 2025 JCR quartile was **not opened directly**. With a JIF of 6.4, Q1 in Computer Science, Information Systems is highly likely, but this is an inference. |
| JOURNAL IMPACT FACTOR | 6.4 (2025 JCR, released 2026); 5-year JIF 6.0 | Publisher journal page (verbatim) |
| JCR SUBJECT CATEGORY | Computer Science, Information Systems (secondary sources) | Not opened directly in JCR (no access) |
| VERIFIED REVIEW/DECISION TIMELINE | No submission-to-first-decision figure is shown on the current Springer page. | `data/page_home.txt` |
| VERIFIED ACCEPTANCE TIMELINE | **Median 66 days from received to accepted (IQR 53–91; 57.3% of papers ≤72 d; 38.7% ≤60 d)** for the 300 most recent research articles (published Jan–Nov 2026). The previous window (Jul–Dec 2025, n=299) had a median of 87 d (IQR 69–112). | Computed by us from article-level "received"/"accepted" dates deposited by Springer Nature in Crossref (`scripts/crossref_acceptance_times.py`, `data/jk1.csv`, `data/jk2.csv`). This measures **submission-to-acceptance** time for papers that were accepted. It is not first-decision time and not a guarantee for any single paper: about 43% of recent papers took longer than 72 days. |
| APC | £1590 / US$2090 / €1790 (fully open access, CC BY). Waivers are available case by case. | Springer "how-to-publish-with-us" page (fetched 2026-11-10). A third-party claim that the journal is "diamond OA" was checked and found to be **wrong**. |
| SCOPE FIT | Explicit scope items: Artificial Intelligence, Machine Learning, Data Mining, Data Analysis and Representation, Bioinformatics, **Signal Processing**, **Pattern Recognition**. Time-series classification fits under ML / Signal Processing / Pattern Recognition. | `data/page_aims-and-scope.txt` |
| RESEARCH FIT | Recent articles (Nov 2026 issue list) include deep-learning, multimodal classification, graph and LLM methods, with experimental ML papers dominating. A methodological ML paper with an extensive benchmark and statistical testing matches the journal's article profile. | Journal page "Latest articles" |
| KEY AUTHOR GUIDELINES | Double-anonymous peer review, so the manuscript is anonymised and a separate title page is required. Abstract 150–250 words. 4–6 keywords. Decimal headings, at most 3 levels. Word (.docx) or LaTeX. 10-pt Times-like font. Springer author–year citations, with the reference list alphabetical and DOIs given as links. Figure captions start "**Fig. 1**" with no end punctuation. Tables use Arabic numerals with captions. "Statements and Declarations" (Funding, Competing interests, Author contributions, Data availability, …) goes **after the References**. A Data Availability Statement is mandatory. **LLM use must be documented in the Methods section.** Supplementary files are called "Online Resource". | `data/page_submission-guidelines.txt` |
| KEY REJECTION RISKS | (1) Desk rejection for incremental novelty: the journal receives many "new deep model + benchmark" papers. (2) Weak statistics or single-dataset evidence. (3) Missing comparison with recent SOTA. (4) English or formatting problems. (5) Non-anonymised manuscript. (6) Missing declarations. | Derived from the guidelines plus the reviewer-expectation analysis in `journal_comparison.md` |

## Why this journal (summary)

The user set a hard limit of **≤72 days to final acceptance**. We measured actual received→accepted intervals for 79 candidate journals (PubMed history records and Crossref assertions; see `journal_comparison.md`). **Only three** had a median ≤72 days:

- Frontiers in Physiology (62.5 d): physiology scope, Frontiers publisher, JIF ≈3–4. Poor fit for a computer-science method paper.
- JKSU-CIS (66 d): JIF 6.4, Springer Nature, CS/ML scope.
- International Journal of Information Technology (70.5 d): Q1 JCR status could not be established, so we excluded it.

All Oxford University Press journals we could measure have medians of 117–167 days:

| OUP journal | Median days |
|---|---|
| Bioinformatics | 156 |
| Briefings in Bioinformatics | 120 |
| JAMIA | 118 |
| European Heart Journal – Digital Health | 117.5 |
| Bioinformatics Advances | 127 |
| NAR Genomics & Bioinformatics | 152 |
| GigaScience | 198 |
| Database | 167 |

The OUP *Journal of Computational Design and Engineering* (JIF ≈6.8 per secondary sources) does not deposit history dates and its pages are not machine-readable here, so its timeline is **unverified** and it could not be selected under a verified-≤72-day constraint.

For Elsevier journals, ScienceDirect blocked automated access, so their official "Journal Insights" timelines could **not be verified**. Third-party figures for ESWA (147–187 d) and article-level PubMed medians (Comput Biol Med 113 d; CMPB 195.5 d; Artif Intell Med 287 d) were all well above the limit.

**Constraints that could not be fully verified:** (a) the 2025 JCR quartile, which rests on secondary sources plus the JIF magnitude; (b) any guarantee of a ≤72-day decision for an individual paper. The median is ≤72 d, but the interquartile range extends to 91 d.
