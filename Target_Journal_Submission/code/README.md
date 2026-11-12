# MissRocket: missingness-aware MiniRocket for time series classification with missing values

Code, configuration and raw results for the study **"Missing values in random-convolution time series classification: observed-tap weighting for MiniRocket and a pre-specified evaluation"** (submitted to the *Journal of King Saud University – Computer and Information Sciences*).

Every number, table and figure in the manuscript is produced by the code in this directory from the raw result files under `results/full/`.

## 1. Installation

Tested with Python 3.13.18 on Linux x86_64, CPU only (4 cores, 15 GB RAM). No GPU is needed.

Run each command separately:

```bash
python -m venv .venv && source .venv/bin/activate
```

```bash
pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu
```

```bash
pip install -r requirements.txt
```

`environment.yml` is provided for conda users.

Hardware is detected automatically:
- numba and aeon use all CPU cores;
- PyTorch (GRU-D only) runs on CPU.

CUDA and Apple-Silicon MPS are not required. The deep baseline is small and was run on CPU for comparability.

## 2. Data

Both datasets are public and need no registration:

| Dataset | Source | Licence | Use |
|---|---|---|---|
| UCR Time Series Classification Archive 2018 (128 univariate datasets) | Dau et al. (2019); `.ts` files from timeseriesclassification.com | archive terms of use | E1–E5a, E7 |
| PhysioNet/CinC Challenge 2012 (12,000 ICU stays) | Silva et al. (2012); physionet.org/content/challenge-2012/1.0.0 | Open Data Commons Attribution v1.0 | E5b |

```bash
bash scripts/download_data.sh
```

```bash
python scripts/build_registry.py
```

`data/registry.csv` lists every UCR dataset with its size, its kind (complete / native-missing / variable-length) and its role:
- **development:** 10 datasets used for all design decisions;
- **confirmatory:** 103 datasets; 91 satisfy the pre-specified compute rule;
- **natural:** 15 datasets that are incomplete by nature.

## 3. Reproducing the study

```bash
python run_all.py --mode quick
```

Quick mode is a pipeline check on 3 development datasets with 1 seed. It takes about 5–10 minutes.

```bash
python run_all.py --mode full
```

Full mode runs every pre-specified experiment. It takes roughly 15–20 hours of wall time on 4 cores. It is resumable: rerun the same command after an interruption.

Useful options:
- `--only E1,E5_p12` runs a subset of experiments.
- `--skip-experiments` regenerates statistics, tables and figures only.

| Exp. | Script | What it does |
|---|---|---|
| E1 | `experiments/e1_main.py` | 91 datasets × {MCAR, block, MNAR} × {0.2, 0.5, 0.8}, seed 0 (seeds 1–2 on a 30-dataset subset); proposed method + 10 baselines + γ=0 ablation |
| E3 | `experiments/e3_ablation.py` | Ablations and variants (γ, mask features, training-set selection, gap filler), seed 0 |
| E4 | `experiments/e4_shift.py` | Train/test missing-rate shift |
| E5a | `experiments/e5_natural.py` | 15 naturally incomplete / variable-length UCR datasets |
| E5b | `experiments/e5_p12.py` | PhysioNet 2012 mortality (sets a+b train, set c test), multivariate channel-wise |
| E7 | `experiments/e7_sensitivity.py` | Feature budget and γ sensitivity |
| E2 | `experiments/e2_deep.py` | GRU-D on a pre-specified small/short UCR subset |
| E4b | `experiments/e4b_mechanism_shift.py` | Train/test *mechanism* shift (added during internal review; post hoc) |
| E8 | `scripts/error_analysis.py` | Gains vs dataset properties, extremes, confusion matrices |
| — | `scripts/benchmark_scaling.py` | Controlled transform-time and memory benchmark (run on an idle machine) |
| — | `scripts/reproducibility_check.py` | Re-runs a sample of stored runs and checks exact equality |

Outputs are written under `results/<mode>/`:
- `<EXP>/raw_results.csv`: one row per dataset × condition × seed × method;
- `raw_results.csv`: all experiments concatenated;
- `metrics.json` and `statistics/statistics.json`: every test statistic used in the paper;
- `tables/*.md|csv` and `figures/*.png|pdf`.

All settings live in `config/experiments.yaml`. The protocol was frozen at the git commit titled *"PROTOCOL FREEZE"* before any confirmatory run. `PROGRESS.md` (repository root) documents every design iteration, including negative results and the issues found and fixed.

## 4. Using the method

```python
from src.models.missrocket import MissRocket      # univariate, X: (n, L) with NaN for missing values
clf = MissRocket(random_state=0).fit(X_train, y_train)   # gamma = 1, linear gap filling (defaults)
pred = clf.classes_[clf.decision_function(X_test).argmax(1)]
```

`MissRocketMV` is the channel-wise multivariate version (X: (n, D, L)). `src/models/maskrocket.py` contains the numba kernels:
- the group-mean (native) estimator;
- partial-convolution and zero-fill variants;
- the observed-tap counts.

## 5. Tests

```bash
python -m pytest -q tests
```

The tests check:
- bit-exact equivalence with MiniRocket responses on complete data;
- offset behaviour;
- MCAR unbiasedness of the native estimator;
- exact missing rates of the simulator for all mechanisms;
- the imputers;
- the limiting cases of the gap-adaptive variant.

## 6. Determinism

Seeds are fixed in `config/experiments.yaml`. Missingness masks use hashed, setting-specific seeds, so every method sees identical corrupted data. Numba caches are cleared at the start of each run (`src/utils_cache.py`). Small run-to-run differences can still arise from multithreaded floating-point reductions in BLAS and LightGBM.
