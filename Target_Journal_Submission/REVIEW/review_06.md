# Review Round 6: Reviewer #6 (computational complexity, latency, memory, energy, scalability, deployment)

**Question:** is the improvement worth its computational cost?

| # | Severity | Issue | Response / action |
|---|---|---|---|
| 1 | **MAJOR** | Timings in Table (efficiency) were measured *during* the benchmark, with concurrent jobs and different library implementations. They conflate method cost and implementation, and are not a controlled measurement. | **New controlled benchmark** (`scripts/benchmark_scaling.py`): transform only, synthetic series (n ∈ {200, 1000}, L ∈ {128, 512, 2048}), 50% block missingness, isolated subprocesses on an idle machine, median of 3 after warm-up, peak RSS. Results: weighting adds no measurable cost (MissRocket 13.19 s vs γ=0 13.19 s at n=1000, L=2048); our numba transform is about an order of magnitude slower than aeon's MiniRocket (0.98 s); MissRocket is comparable to MultiRocket (12.4 s) and 3.5× faster than Hydra-MultiRocket (46.4 s); it has the lowest peak memory (373 MB vs 8,284 MB for Hydra-MultiRocket). Added to Sect. 6.6 and Online Resource 1 (Fig. S13, Table "scaling"). |
| 2 | MODERATE | The "4× slower than MiniRocket" in Table (efficiency) could be read as an inherent cost of the method. | Sect. 6.6 now separates the method (no extra cost) from the implementation (slower than aeon). Limitation 6 already states this. |
| 3 | MODERATE | Energy was not measured. | No power instrumentation is available in the cloud container. Wall time on a fixed 4-core CPU is reported as a proxy; stated as a limitation (added to limitation 6). |
| 4 | MINOR | Memory of kNN imputation grows with the training set. | Stated qualitatively in Sect. 6.6. |
| 5 | MINOR | Is the improvement worth the cost? | Yes, relative to MiniRocket with interpolation: the method cost is unchanged and the accuracy gains under long gaps and shift are several percentage points. Relative to MultiRocket and Hydra, MissRocket matches them on average at lower or equal time and much lower memory. Relative to GRU-D, it is about 30× faster on UCR and about 18× faster on PhysioNet 2012, but less accurate on the latter. |
