## Statements and Declarations

**Funding.** The authors declare that no funds, grants or other support were received during the preparation of this manuscript. [Authors: replace if applicable.]

**Competing interests.** The authors have no relevant financial or non-financial interests to disclose. [Authors: confirm.]

**Author contributions.** [To be completed by the authors on the separate title page and in the submission system, as required for double-anonymous review.]

**Data availability.** All data analysed in this study are publicly available:

- the UCR Time Series Classification Archive 2018 [@Dau2019], obtained from timeseriesclassification.com;
- the PhysioNet/Computing in Cardiology Challenge 2012 data [@Silva2012; @Goldberger2000], available at https://physionet.org/content/challenge-2012/1.0.0/ under the Open Data Commons Attribution License v1.0.

The simulated missingness masks are fully determined by the published code and seeds. All raw per-run results (one row per dataset, condition, seed and method), the statistics files and the scripts that generate every table and figure are provided as Online Resources and in the code repository [link withheld for double-anonymous review].

**Code availability.** The complete source code, including the method, baselines, experiment scripts, statistical analysis, figure and table generation, and unit tests, is available in the code repository [link withheld for double-anonymous review]. It will be deposited in a public archive with a persistent identifier upon acceptance. `python run_all.py --mode full` reproduces all reported numbers.

**Ethics approval.** Not applicable. The study uses only public, de-identified benchmark data. The PhysioNet 2012 data were de-identified by the data providers and are distributed openly.

**Use of large language models.** The research workflow was carried out with the assistance of an AI agent (Anthropic Claude), as required to be documented by the journal's policy. Its use covered:

- literature and journal searching;
- code implementation;
- experiment orchestration;
- statistical analysis scripting;
- manuscript drafting.

All results reported in the manuscript are produced by the released code from the raw experimental outputs; no number was entered by hand. All references were verified against Crossref, arXiv, PubMed or the publishers' pages. The authors take full responsibility for the content. [Authors: adapt this statement to the actual division of work and to the journal's current policy text.]
