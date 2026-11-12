## 3 Problem formulation and preliminaries

### 3.1 Classification with missing values

Let $\mathcal{D}=\{(\mathbf{x}_i,\mathbf{m}_i,y_i)\}_{i=1}^{n}$ be a training set of univariate series $\mathbf{x}_i\in\mathbb{R}^{L}$ with observation masks $\mathbf{m}_i\in\{0,1\}^{L}$ ($m_{it}=1$ if $x_{it}$ is observed) and labels $y_i\in\{1,\dots,K\}$. Values at positions with $m_{it}=0$ are unavailable. The task is to learn $f(\mathbf{x}\odot\mathbf{m},\mathbf{m})\mapsto y$. Variable-length series are represented by right-padding with unobserved positions. Following @Rubin1976 and @Little2019, missingness is *missing completely at random* (MCAR) if $\mathbf{m}$ is independent of $(\mathbf{x},y)$, and *missing not at random* (MNAR) if it depends on the unobserved values themselves.

### 3.2 MiniRocket as a contrast of tap-group means

MiniRocket [@Dempster2021] applies 84 fixed kernels of length nine. Each kernel is indexed by a set $P_k\subset\{0,\dots,8\}$ of three taps with weight $+2$; the remaining six taps $Q_k$ have weight $-1$. The kernels are applied at a set of dilations $d$. For position $t$ and dilation $d$, the tap values are $v_j(t)=x_{t+(j-4)d}$, with zero padding outside the series. The response is

$$C_k(t)=2\sum_{j\in P_k}v_j(t)-\sum_{j\in Q_k}v_j(t) \tag{1}$$

Because the weights sum to zero ($3\cdot2-6\cdot1=0$), Eq. (1) can be rewritten as a scaled difference of two group means:

$$C_k(t)=6\big(\bar v_{P_k}(t)-\bar v_{Q_k}(t)\big),\qquad \bar v_{S}(t)=\tfrac{1}{|S|}\textstyle\sum_{j\in S}v_j(t) \tag{2}$$

Each response is pooled by the *proportion of positive values* (PPV) with respect to a bias $b$. The biases are quantiles of the responses of a randomly chosen training series:

$$\mathrm{PPV}_{k,d,b}=\frac{1}{|T|}\sum_{t\in T}\mathbb{1}[C_k(t)>b] \tag{3}$$

Here $T$ is either all positions (zero padding) or the positions whose taps are all inside the series. MiniRocket alternates between the two choices across kernels and dilations. The roughly 10,000 resulting features are classified by a ridge classifier whose penalty is chosen by efficient leave-one-out (generalised) cross-validation.

Eq. (1) is undefined when taps are missing. The common practice is to fill the gaps first (zero, mean, last observation carried forward, or interpolation) and then apply Eq. (1) as if the series were complete.

## 4 Methods

### 4.1 A native estimator from observed taps

Equation (2) suggests estimating the response from the observed taps only. Let $O(t)$ be the set of observed taps; out-of-bounds taps under zero padding count as observed zeros, exactly as in MiniRocket. Let $n_P=|P_k\cap O(t)|$ and $n_Q=|Q_k\cap O(t)|$. Define

$$\hat C_k(t)=6\Big(\tfrac{1}{n_P}\textstyle\sum_{j\in P_k\cap O(t)}v_j(t)-\tfrac{1}{n_Q}\sum_{j\in Q_k\cap O(t)}v_j(t)\Big),\quad\text{defined if } n_P\ge1,\ n_Q\ge1 \tag{4}$$

PPV is then computed over the positions where Eq. (4) is defined. We call this estimator *group-mean* (native) masking.

**Proposition 1 (properties of Eq. 4).**

\(i) *Exactness:* if $\mathbf{m}\equiv\mathbf{1}$, then $\hat C_k(t)=C_k(t)$ for all $k,t,d$.

\(ii) *Offset invariance:* for any constant $c$ and any window whose taps lie inside the series, $\hat C_k(t;\mathbf{x}+c\mathbf{1})=\hat C_k(t;\mathbf{x})$.

\(iii) *Conditional unbiasedness under MCAR:* if each tap is observed independently with the same probability, then $\mathbb{E}[\hat C_k(t)\mid n_P\ge1,n_Q\ge1]=C_k(t)$.

*Proof.*

\(i) With all taps observed, $n_P=3$ and $n_Q=6$, so Eq. (4) reduces to Eq. (2). In our implementation the coefficients $6/3$ and $6/6$ are exact in floating point, so the identity also holds bit-for-bit (unit test `test_complete_data_equivalence_responses`).

\(ii) Adding $c$ to every observed value adds $c$ to both observed-group means, and the difference is unchanged.

\(iii) Under MCAR and conditional on the counts, the observed subset of $P_k$ is a uniformly random subset of size $n_P$. The mean of a uniformly random subset is unbiased for the mean of the full set, and likewise for $Q_k$. Linearity completes the proof. ∎

By contrast, zero filling applies Eq. (1) to $\mathbf{x}\odot\mathbf{m}$. Its response to an offset $c$ changes by $c\,(2n_P-n_Q)$, which depends on the missingness pattern. Partial-convolution renormalisation [@Liu2018] changes it by $9c\,(2n_P-n_Q)/(n_P+n_Q)$. Both therefore inject the level of the series into the response through the missingness pattern. Eq. (4) does not.

**Proposition 2 (variance).** Suppose $v_j=s_j+\varepsilon_j$, where $\varepsilon_j$ are i.i.d. with variance $\sigma^2$. Conditional on the observed set,

$$\mathrm{Var}[\hat C_k(t)\mid O]=36\sigma^2\big(1/n_P+1/n_Q\big).$$

This equals $18\sigma^2$ for complete windows and grows to $72\sigma^2$ when $n_P=n_Q=1$.

*Proof.* The two group means are independent, with variances $\sigma^2/n_P$ and $\sigma^2/n_Q$. ∎

Proposition 2 explains a central negative result of this study (Section 6). The native estimator is unbiased, but it discards the temporal smoothness that interpolation exploits. When gaps are short and scattered, which is typical of MCAR, an interpolated tap is a low-variance estimate of the missing value. A tap-wise unbiased estimate is noisier, and the noise propagates through the threshold in Eq. (3).

### 4.2 MissRocket: observed-tap-weighted pooling

Interpolation fails differently. Inside a long gap every tap is fabricated, and the response degenerates into a deterministic artefact of the interpolant.

**Proposition 3 (fabricated responses).** Let $\tilde{\mathbf{x}}$ be the linear interpolation of $\mathbf{x}$. If all nine taps of a window lie strictly inside one gap, so that $\tilde v_j=\alpha+\beta(j-4)d$, then

$$C_k(t)=\beta d\Big(2\sum_{j\in P_k}(j-4)-\sum_{j\in Q_k}(j-4)\Big).$$

This value depends only on the slope between the gap's two end points and on the kernel geometry, not on the unobserved signal.

*Proof.* Substitute the affine taps into Eq. (1). The constant $\alpha$ cancels because the weights sum to zero. ∎

Such windows are rare under MCAR. At a missing rate of $r$, the probability that all nine taps are missing is $r^9$, which is below 1% for $r=0.6$. They are common under contiguous (block) missingness, where they produce identical, spurious PPV contributions in every series with a gap of similar slope.

MissRocket keeps the low-variance interpolated responses but weights each position's contribution to PPV by the reliability of its window. Let $c(t)=|O(t)|\in\{0,\dots,9\}$ be the number of truly observed taps of the window at dilation $d$; padding taps count as observed, as above. With $w_\gamma(c)=(c/9)^\gamma$,

$$\mathrm{PPV}^{\gamma}_{k,d,b}=\frac{\sum_{t\in T}w_\gamma(c(t))\,\mathbb{1}[\tilde C_k(t)>b]}{\sum_{t\in T}w_\gamma(c(t))} \tag{5}$$

where $\tilde C_k$ is Eq. (1) evaluated on the linearly interpolated series. Positions with $c(t)=0$, which are exactly the fabricated windows of Proposition 3, receive zero weight for any $\gamma>0$. The exponent $\gamma$ interpolates between three cases:

- $\gamma=0$ gives MiniRocket on the interpolated series;
- $\gamma=1$ gives each window the fraction of its taps that were observed;
- $\gamma\to\infty$ keeps only completely observed windows.

We fixed $\gamma=1$ for the proposed method using the development datasets only (Section 5.4). The other values, and a variant that selects $\gamma$ on the training set, are reported as ablations.

**Proposition 4 (special cases).**

- If $\mathbf{m}\equiv\mathbf{1}$, MissRocket equals MiniRocket for every $\gamma$.
- For $\gamma=0$, MissRocket equals MiniRocket applied to the linearly interpolated series.

*Proof.* In the first case $c(t)=9$ and $w_\gamma=1$ everywhere, and $\tilde{\mathbf{x}}=\mathbf{x}$. In the second case $w_0\equiv1$. ∎

Biases are drawn as in MiniRocket, from the responses of a random training series at positions with $c(t)\ge1$. The classifier is MiniRocket's ridge head (standardisation followed by `RidgeClassifierCV` with $\alpha\in\{10^{-3},\dots,10^{3}\}$).

**Optional components (ablations).**

- *Missingness-pattern features:* MiniRocket applied to the binary mask, giving 1,000 features. This is a time-series analogue of the missing-indicator method [@VanNess2023].
- *Training-set selection:* $(\gamma,\text{mask})$ chosen from $\{0,0.5,1,2\}\times\{\text{off},\text{on}\}$ by the ridge head's leave-one-out criterion.
- *Other gap fillers:* zero, last observation carried forward (LOCF), and cross-series k-nearest-neighbour imputation.

### 4.3 Implementation and complexity

Because $w_\gamma$ depends only on the integer count $c(t)$, the numerator and denominator of Eq. (5) are obtained from per-count histograms of threshold exceedances. Several values of $\gamma$ can therefore be evaluated in one pass at negligible extra cost. Per series, the cost is that of MiniRocket, $\mathcal{O}(\sum_d L\,(84\cdot 9+F_d))$ with $F_d$ the number of features at dilation $d$, plus $\mathcal{O}(9L)$ per dilation to count observed taps. The implementation uses numba [@Lam2015] and parallelises over series. The kernels, dilations, padding alternation and bias quantiles follow the reference MiniRocket code. On complete data our implementation reproduces the reference accuracy, and the proposed and standard responses agree bit-for-bit (unit tests).

For multivariate series (Section 5.3), the transform is applied channel-wise with a per-channel feature budget, and a single ridge head is fit on the concatenated features.
