# SafeMA: Anytime-Valid Sequential Meta-Analysis with E-Values — Design Spec

**Goal:** World-first browser implementation of e-value-based sequential meta-analysis (ALL-IN framework, Grünwald/Ter Schure). Replace alpha-spending with anytime-valid inference for living systematic reviews.

**Target journals:** Statistics in Medicine (methods) + JOSS (software)

**Mathematical foundation:** Grünwald, de Heide, Koolen. "Safe Testing." JRSS-B 86(5):1091-1128, 2024. Ter Schure, Grünwald. "ALL-IN Meta-Analysis." F1000Research 11:549, 2022.

---

## 1. Core Mathematical Framework

### 1.1 E-Values

An e-value E is a nonneg random variable satisfying E_{H_0}[E] <= 1. Key properties:
- **Markov composition:** P(E >= 1/alpha) <= alpha (anytime-valid Type I control)
- **Multiplicative accumulation:** E_1:k = prod(E_i) for independent studies
- **Optional stopping/continuation:** Valid regardless of when you peek or stop
- **No alpha-spending needed:** The e-process itself controls error

### 1.2 Growth-Rate Optimal (GRO) E-Variables

For testing H_0: mu = 0 vs H_1: mu = mu_1 (the anticipated effect):

**For normal data (known variance):**
```
E_i = exp(lambda * y_i - lambda^2 * sigma_i^2 / 2)
```
where lambda = mu_1 / sigma_i^2 is the GRO betting fraction.

The optimal lambda maximizes E_{H_1}[log E], yielding:
```
lambda* = mu_1 / (sigma_i^2 + mu_1^2 / sigma_i^2)  [GROW criterion]
```

For the simplified case (small mu_1 relative to sigma):
```
lambda* ≈ mu_1 / sigma_i^2
```

### 1.3 E-Process for Sequential Meta-Analysis

Given k studies with effects y_i and variances v_i = se_i^2:

**Step 1:** Choose anticipated effect mu_1 (from prior knowledge or pilot estimate)

**Step 2:** For each study i = 1, ..., k:
```
E_i = exp(mu_1 * y_i / v_i - mu_1^2 / (2 * v_i))
```

**Step 3:** Cumulative e-value:
```
S_k = prod_{i=1}^{k} E_i = exp(mu_1 * sum(y_i/v_i) - mu_1^2/2 * sum(1/v_i))
```

**Step 4:** Reject H_0 when S_k >= 1/alpha (default: S_k >= 20 for alpha = 0.05)

### 1.4 Anytime-Valid Confidence Sequences

A (1-alpha) confidence sequence is a sequence of sets {C_k} such that:
```
P(mu in C_k for ALL k >= 1) >= 1 - alpha
```

For the normal model, the confidence sequence at step k is:
```
C_k = {mu : prod_{i=1}^{k} E_i(mu) >= 1/alpha}
```

This can be computed by finding mu_lo, mu_hi such that:
```
sum_{i=1}^{k} mu * y_i/v_i - mu^2/(2*v_i) = log(1/alpha)
```

Solving the quadratic in mu:
```
W_k = sum(1/v_i), T_k = sum(y_i/v_i)
mu_hat = T_k / W_k  (same as inverse-variance estimate)
```

The confidence sequence boundaries are:
```
mu_hat +/- sqrt(2 * log(1/alpha) / W_k + (more terms for finite-sample correction))
```

For the **mixture** e-value (recommended for unknown mu_1), integrate over a prior for mu_1:
```
E_i^mix = integral E_i(mu_1) * pi(mu_1) d(mu_1)
```

With a normal prior pi(mu_1) = N(0, tau^2), this has a closed form:
```
E_i^mix = sqrt(v_i / (v_i + tau^2)) * exp(tau^2 * y_i^2 / (2 * v_i * (v_i + tau^2)))
```

### 1.5 Random-Effects Extension

For random-effects meta-analysis, the e-value must account for heterogeneity. Under H_0: mu = 0 with between-study variance sigma_b^2:

```
E_i = sqrt((v_i + sigma_b^2) / (v_i + sigma_b^2 + tau_design^2)) * 
      exp(tau_design^2 * y_i^2 / (2 * (v_i + sigma_b^2) * (v_i + sigma_b^2 + tau_design^2)))
```

where tau_design^2 is the design parameter (anticipated heterogeneity), estimated from cumulative data.

### 1.6 Comparison with Classical TSA

| Feature | TSA (alpha-spending) | SafeMA (e-values) |
|---------|---------------------|-------------------|
| Pre-specify #looks | Required | Not needed |
| Pre-specify RIS | Required | Not needed |
| Optional stopping | Only at planned looks | Anytime |
| Optional continuation | Must re-spend alpha | Automatic |
| Type I error control | At planned looks only | Always (Ville's inequality) |
| Mathematical basis | Neyman-Pearson | Game-theoretic / martingale |
| Key statistic | Z-statistic | E-value (likelihood ratio) |
| Threshold | z-boundary | E >= 1/alpha |

---

## 2. Application Architecture

### 2.1 Single-File HTML App (~1,500-2,000 lines)

**Tabs:**
1. **Data Entry** — Study name, year, effect size, SE (or 2x2 data for binary)
2. **Settings** — Alpha, anticipated effect, prior variance, outcome type
3. **E-Value Plot** — Cumulative e-process vs 1/alpha threshold, alongside classical Z for comparison
4. **Confidence Sequences** — Anytime-valid CS vs classical CI at each look
5. **Report** — Structured paragraph suitable for publication

### 2.2 Supported Outcome Types
- Binary: OR, RR, RD (log-transform for ratio measures)
- Continuous: MD, SMD
- Time-to-event: log-HR

### 2.3 E-Value Engines
1. **Fixed-effect e-values** (known mu_1): GRO e-variable
2. **Mixture e-values** (unknown mu_1): Normal prior integration
3. **Random-effects e-values**: Heterogeneity-adjusted via cumulative tau^2
4. **GROW criterion**: Growth-rate optimal under working model

### 2.4 Built-in Examples
1. **SGLT2i-HF** (k=8) — Strong evidence, e-process should cross early
2. **Magnesium-MI / Teo-ISIS4** (k=16) — Classic false positive under p-values; e-process should NOT cross
3. **HCQ COVID-19** (k=6) — Evidence reversal; e-process should show initial growth then decline

### 2.5 Visualizations (Canvas)
1. **E-Process Plot:** log(S_k) vs study index, with log(1/alpha) threshold line and classical cumulative Z overlay
2. **Confidence Sequence:** mu_hat_k with CS bands vs classical CI bands — CS never shrinks (by construction)
3. **Study-level E-values:** Bar chart of individual log(E_i) contributions

---

## 3. Key Innovation Claims

1. **World-first browser implementation** of e-value sequential meta-analysis
2. **No alpha-spending needed** — fundamentally simpler than TSA
3. **Anytime-valid confidence sequences** — stronger than CIs (valid at ALL stopping times)
4. **Random-effects extension** — accounts for heterogeneity in the e-value computation
5. **Side-by-side comparison** with classical TSA boundaries
6. **GROW criterion** — information-theoretically optimal e-variables

---

## 4. Validation Plan

- Cross-validate against R `safestats` package for simple cases
- Reproduce the Teo/ISIS-4 magnesium example showing e-values DON'T cross while classical p-values do
- Reproduce SGLT2i example showing early e-value crossing
- Verify E[E] <= 1 under H_0 via simulation (10K replicates)
- Verify confidence sequence coverage >= 1-alpha via simulation

---

## 5. Non-Goals (v1.0)

- Network meta-analysis e-values
- IPD-level e-values (summary-level only)
- Bayesian e-values (frequentist focus)
- Safe logrank test (would need individual survival data)
- GROW with nuisance parameters (would require profile e-values)
