# Citation Audit (Phase 23)

## 1. Bibliographic verification

| Group | Method | Result |
|---|---|---|
| 39 references with a DOI or arXiv ID | Retrieved from Crossref / arXiv API; title matched (`code/scripts/verify_citations.py` → `citation_audit_round1.csv`) | 39/39 match |
| Silva et al. 2012 | PubMed E-utilities (PMID 24678516): title, journal, volume 39, pages 245–248, authors | Verified |
| Holm 1979 | JSTOR stable record (URL resolves); volume/issue/pages confirmed by the JSTOR citation line reproduced in a copy of the paper and by BibBase (JSTOR blocks automated access) | Verified (secondary confirmation of pages) |
| Demšar 2006; Benavoli et al. 2016; Pedregosa et al. 2011; Middlehurst et al. 2024a (aeon) | jmlr.org pages: title, authors, volume(issue):pages, year | Verified |
| Ke et al. 2017 (LightGBM) | papers.nips.cc page: title, authors, proceedings volume (pages not shown, so none given) | Verified |

Errors found and corrected during the audit:
- Lipton et al. 2016: title corrected to the arXiv title.
- Twala et al. 2008: a wrong DOI was replaced with 10.1016/j.patrec.2008.01.010.
- Silva et al. 2012: an invalid DOI was replaced with the PMID.
- Holm 1979: no Crossref DOI exists; the JSTOR URL is used.
- Unverified page numbers for Ke et al. 2017 were removed.
- MiniRocket and Numba: truncated titles fixed (subtitle joined).
- Bagnall et al. and Ruiz et al.: online-first years replaced by print years.

## 2. Are claims attributed to papers supported by them?

| Claim in manuscript | Source checked | Status |
|---|---|---|
| MiniRocket is up to 75× faster than ROCKET on larger datasets | MiniRocket abstract (arXiv 2012.08791) | Supported (an earlier draft wrongly said "two orders of magnitude"; corrected) |
| Hydra+MultiRocket and HIVE-COTE 2 are significantly better than other approaches | Bake-off redux abstract (arXiv 2304.13029) | Supported (earlier "best accuracy-to-cost" paraphrase removed) |
| MultiRocket adds three pooling operators and the first-difference series | MultiRocket descriptions (search results quoting the paper) | Supported |
| PYRREGULAR passes NaNs through sktime MiniRocket to LightGBM; MiniRocket ranked first | PYRREGULAR HTML, Sect. 5 and 5.1 (verbatim quotes obtained) | Supported |
| Yao et al.: 68 UCR datasets, MCAR, comparisons without ROCKET-family methods | Full preprint text (pdftotext): "68 public univariate", MCAR, the string "rocket" absent | Supported |
| Rhodes et al.: label-guided imputation with forest proximities incl. ROCKET; 85 UCR datasets; MCAR/MAR/MNAR; RF/kNN downstream; transform not modified | arXiv HTML (2509.22919), read in full by the fetch agent with quotes | Supported |
| POCKET zero-fills missing values | Search snippet of the POCKET paper ("fills them with zeros") | Mentioned only in internal design documents, not cited in the manuscript |
| Impute-then-predict consistency with powerful learners | Josse et al. (2019), Le Morvan et al. (2021) abstracts | Supported |
| Partial convolutions renormalise by the fraction of valid inputs | Liu et al. (2018) | Supported |
| GRU-D decays inputs and hidden states | Che et al. (2018) | Supported |

## 3. Uncited entries

Ismail Fawaz et al. (2020), Ringel et al. (2024), Ruiz et al. (2021) and Wang et al. (2017) are in the verified bibliography but not cited in the final text. They are therefore excluded automatically from the reference list.
