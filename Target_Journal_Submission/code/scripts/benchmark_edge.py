"""Edge-CPU proxy benchmark for the CWRU case study (E9, added after external review).

Single CPU thread (NUMBA/OMP/BLAS threads = 1, aeon n_jobs = 1), as a proxy for a single-core edge processor;
this is NOT a measurement on embedded hardware. Data: CWRU fold 0 (train loads 1-3, complete; test load 0 with
30% long outages, condition shift_outage_long30, seed 0). For each method:
  1. "fit" subprocess: fits on the training set, records fit time and peak RSS, pickles the fitted model.
  2. "infer" subprocess (fresh process, deployment proxy): loads the model, records RSS after loading, then
     (a) per-segment latency: median and 95th percentile over 200 single-segment predictions (including gap filling),
     (b) batch throughput: time to predict all test segments, per segment,
     and the peak RSS of the inference process. Median over 3 repeats for (b); one warm-up call precedes timing.
Output: results/full/tables/table_edge.csv
"""
import json
import os
import subprocess
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV = dict(os.environ, NUMBA_NUM_THREADS="1", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
MODEL_DIR = os.path.join(ROOT, "data", "cache", "edge_models")

COMMON = r'''
import sys, os, json, time, pickle, resource, hashlib, numpy as np
sys.path.insert(0, ROOT)
from src.data.cwru import load_cwru, fold
from src.data.missingness import apply_missingness
from src.preprocessing.imputation import IMPUTERS
def hseed(*p): return int(hashlib.sha256("|".join(map(str, p)).encode()).hexdigest()[:8], 16)
X, y, load, rec = load_cwru()
Xtr, ytr, Xte0, yte = fold(0, X, y, load)
Xte = apply_missingness(Xte0, 0.3, "block@4096", hseed("cwru", 0, "shift_outage_long30", 0, "test"))
lin = IMPUTERS["linear"]
class AeonModel:
    def __init__(self, kind):
        from aeon.transformations.collection.convolution_based import MiniRocket, MultiRocket, HydraTransformer
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.linear_model import RidgeClassifierCV
        self.ts = ([MiniRocket(random_state=0, n_jobs=1)] if kind == "mini" else
                   [HydraTransformer(random_state=0, n_jobs=1), MultiRocket(random_state=0, n_jobs=1)])
        self.clf = make_pipeline(StandardScaler(), RidgeClassifierCV(alphas=np.logspace(-3, 3, 10)))
    def _f(self, X, fit=False):
        Z = lin(X)[:, None, :].astype(np.float64)
        return np.hstack([np.asarray(t.fit_transform(Z) if fit else t.transform(Z), dtype=np.float32) for t in self.ts])
    def fit(self, X, y):
        self.clf.fit(self._f(X, True), y); return self
    def predict(self, X):
        return self.clf.predict(self._f(X))
class MRModel:
    def __init__(self):
        from src.models.missrocket import MissRocket
        self.m = MissRocket(random_state=0, fixed=(1.0, False))
    def fit(self, X, y):
        self.m.fit(X, y); return self
    def predict(self, X):
        s = self.m.decision_function(X); return self.m.classes_[s.argmax(1)]
def make(name):
    return {"MissRocket": MRModel, "MiniRocket (aeon) + linear": lambda: AeonModel("mini"),
            "Hydra-MultiRocket (aeon) + linear": lambda: AeonModel("hydra")}[name]()
def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
'''.replace("ROOT", repr(ROOT))

FIT = COMMON + r'''
name, path = sys.argv[1], sys.argv[2]
r0 = rss()
m = make(name)
m.fit(Xtr[:40], ytr[:40])  # warm-up (JIT compilation), excluded from timing
m = make(name)
t = time.perf_counter(); m.fit(Xtr, ytr); fit_s = time.perf_counter() - t
pickle.dump(m, open(path, "wb"))
print(json.dumps(dict(fit_s=fit_s, fit_peak_rss_mb=rss(), rss_after_imports_mb=r0, model_mb=os.path.getsize(path) / 2**20)))
'''

INFER = COMMON + r'''
name, path = sys.argv[1], sys.argv[2]
r0 = rss()
m = pickle.load(open(path, "rb"))
r1 = rss()
m.predict(Xte[:1]); m.predict(Xte[:50])  # warm-up
lat = []
for i in range(200):
    t = time.perf_counter(); m.predict(Xte[i:i + 1]); lat.append(time.perf_counter() - t)
bt = []
for _ in range(3):
    t = time.perf_counter(); m.predict(Xte); bt.append((time.perf_counter() - t) / len(Xte))
print(json.dumps(dict(latency_ms_median=1e3 * float(np.median(lat)), latency_ms_p95=1e3 * float(np.percentile(lat, 95)),
                      batch_ms_per_segment=1e3 * float(np.median(bt)), infer_rss_after_load_mb=r1,
                      infer_peak_rss_mb=rss(), infer_rss_after_imports_mb=r0, n_test=len(Xte))))
'''


def run(code, *args):
    out = subprocess.run([sys.executable, "-c", code, *args], capture_output=True, text=True, cwd=ROOT, env=ENV)
    line = [l for l in out.stdout.splitlines() if l.startswith("{")]
    if not line:
        raise RuntimeError(out.stderr[-2000:])
    return json.loads(line[-1])


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    rows = []
    for name in ["MissRocket", "MiniRocket (aeon) + linear", "Hydra-MultiRocket (aeon) + linear"]:
        path = os.path.join(MODEL_DIR, name.split()[0] + ".pkl")
        r = dict(method=name)
        r.update(run(FIT, name, path))
        r.update(run(INFER, name, path))
        print(r, flush=True)
        rows.append(r)
    df = pd.DataFrame(rows)
    p = os.path.join(ROOT, "results", "full", "tables", "table_edge")
    df.to_csv(p + ".csv", index=False)
    with open(p + ".md", "w") as f:
        f.write(df.to_markdown(index=False, floatfmt=".2f"))
    print(df.to_string())


if __name__ == "__main__":
    main()
