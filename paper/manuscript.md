# SafeMA: Anytime-Valid Sequential Meta-Analysis with E-Values — A Browser Implementation of the ALL-IN Framework

**Mahmood Ahmad**^1

1. Royal Free Hospital, London, United Kingdom

**Correspondence:** Mahmood Ahmad, mahmood.ahmad2@nhs.net | **ORCID:** 0009-0003-7781-4478

---

## Abstract

**Background:** Living systematic reviews require sequential monitoring of cumulative evidence, but classical Trial Sequential Analysis (TSA) depends on pre-specified sample sizes, planned looks, and alpha-spending functions. E-values — a recent paradigm shift in hypothesis testing — provide anytime-valid inference that requires none of these pre-specifications, with Type I error guaranteed at all stopping times by Ville's inequality.

**Methods:** SafeMA is a browser-based tool (814 lines) implementing the ALL-IN (Anytime Live and Leading INterim) meta-analysis framework. For each study, the tool computes growth-rate optimal (GRO) e-values and mixture e-values using the formulas:

E_i^GRO = exp(mu_1 * y_i / v_i - mu_1^2 / (2 * v_i))

E_i^mix = sqrt(v_i / (v_i + tau^2)) * exp(tau^2 * y_i^2 / (2 * v_i * (v_i + tau^2)))

The cumulative e-process S_k = product(E_i) is compared against a threshold 1/alpha. Anytime-valid confidence sequences are derived by inverting the e-process. Three built-in clinical examples demonstrate distinct evidence patterns.

**Results:** Applied to SGLT2 inhibitors in heart failure (k=8), the e-process crossed the threshold (1/alpha=20) after the first study alone (S_1 = 2.3 x 10^14), indicating overwhelming evidence. For the classic Teo magnesium-in-MI dataset (k=8), the e-process reached only 3.61 — correctly failing to cross the threshold, consistent with ISIS-4 negating the small-trial signal. For hydroxychloroquine in COVID-19 (k=6), the e-process declined to 0.39, indicating evidence supporting the null. In all three cases, e-values agreed with the eventually-known truth without requiring any pre-specification of sample sizes, looks, or spending functions.

**Conclusion:** SafeMA is the first browser-based implementation of e-value sequential meta-analysis, providing anytime-valid inference for living systematic reviews without alpha-spending. Available at https://github.com/mahmood726-cyber/safema under MIT licence.

**Keywords:** e-values, safe testing, anytime-valid inference, sequential meta-analysis, living systematic review, Ville's inequality, confidence sequence

---

## 1. Introduction

### 1.1 The Problem with Classical Sequential Testing

When a living systematic review is updated after each new trial, the traditional approach is to compute a cumulative p-value and compare it against a nominal threshold (typically 0.05). This approach inflates the Type I error rate because each "peek" at the accumulating data constitutes an additional test.^1

Trial Sequential Analysis (TSA) addresses this by borrowing alpha-spending boundaries from group sequential clinical trial designs.^2 However, TSA requires three strong pre-specifications: (a) the anticipated effect size, (b) the required information size (total sample size), and (c) the number and timing of planned interim looks. These requirements are fundamentally at odds with the nature of living reviews, where new trials arrive unpredictably and the review may continue indefinitely.

### 1.2 E-Values: A Paradigm Shift

E-values, formalised by Grünwald, de Heide, and Koolen in their 2024 JRSS-B Read Paper,^3 provide a fundamentally different approach. An e-value E is a nonnegative random variable satisfying E_{H_0}[E] <= 1. The key property is Markov's inequality applied to the e-process:

P(S_k >= 1/alpha for any k) <= alpha

This holds for **all** stopping times, including data-dependent ones — a guarantee that is provably impossible with p-values.^4 E-values compose by multiplication: S_k = E_1 * E_2 * ... * E_k. No alpha-spending is needed because the multiplicative structure automatically controls error.

### 1.3 The ALL-IN Framework

Ter Schure and Grünwald proposed ALL-IN (Anytime Live and Leading INterim) meta-analysis,^5 applying safe testing to cumulative evidence synthesis. The framework uses growth-rate optimal (GRO) e-variables that maximise the expected log-growth under the alternative hypothesis, providing the fastest possible evidence accumulation while maintaining anytime validity.

SafeMA implements this framework in the browser, providing the first accessible tool for e-value-based sequential meta-analysis.

---

## 2. Methods

### 2.1 E-Value Computation

For study i with observed effect y_i (on the log scale for ratio measures) and variance v_i = se_i^2, the GRO e-value under a point alternative mu_1 is:

E_i^GRO = exp(mu_1 * y_i / v_i - mu_1^2 / (2 * v_i))

This is the likelihood ratio statistic for the normal location model. Under H_0 (mu = 0), the expected value is exactly 1. Under H_1 (mu = mu_1), the expected log-growth is maximised — this is the GROW (Growth-Rate Optimal in Worst case) criterion.^3

For settings where mu_1 is unknown, SafeMA computes the mixture e-value by integrating over a normal prior:

E_i^mix = sqrt(v_i / (v_i + tau^2)) * exp(tau^2 * y_i^2 / (2 * v_i * (v_i + tau^2)))

The default prior variance tau^2 = 0.5 provides reasonable sensitivity for typical meta-analytic effect sizes. SafeMA uses the maximum of GRO and mixture e-values for each study.

### 2.2 Cumulative E-Process and Decision Rule

The e-process is the running product: S_k = product_{i=1}^{k} E_i.

Reject H_0 when S_k >= 1/alpha (default: S_k >= 20 for alpha = 0.05).

By Ville's inequality,^6 P(S_k >= 1/alpha for any k >= 1) <= alpha. This holds regardless of the stopping rule — the analyst may peek after every study, stop when convenient, or continue indefinitely, and the Type I error is always controlled.

### 2.3 Anytime-Valid Confidence Sequences

A (1-alpha) confidence sequence {C_k} satisfies P(mu in C_k for all k >= 1) >= 1 - alpha. This is strictly stronger than a confidence interval, which is valid only at a single pre-specified time point.

SafeMA computes confidence sequences by inverting the e-process: C_k = {mu_0 : S_k(mu_0) < 1/alpha}, where S_k(mu_0) is the e-process computed under H_0: mu = mu_0.

### 2.4 Comparison with Classical TSA

SafeMA includes a side-by-side comparison tab showing the cumulative e-process alongside the classical cumulative Z-statistic and O'Brien-Fleming spending boundaries. This allows users to see exactly where the two frameworks agree and diverge.

---

## 3. Results

### 3.1 SGLT2 Inhibitors in Heart Failure (k=8)

The e-process crossed the threshold after the first study (DAPA-HF): S_1 = 2.3 x 10^14. The pooled log-OR was -0.267 (OR = 0.77). The anytime-valid confidence sequence excluded the null at all 8 looks. **Verdict:** Overwhelming evidence of benefit, confirmed with anytime-valid guarantees.

### 3.2 Magnesium-in-MI / Teo Dataset (k=8)

The e-process reached a maximum of S_k = 3.61 — far below the threshold of 20. Classical meta-analysis of the early small trials (pre-ISIS-4) showed p < 0.05, leading to widespread clinical adoption. The e-process correctly identifies this as insufficient evidence. After ISIS-4 (k=8), the pooled log-OR was 0.050 (OR = 1.05), consistent with no effect. **Verdict:** E-values correctly prevent a false positive that classical sequential testing (with sufficient pre-specification) also prevents, but without requiring any pre-specification at all.

### 3.3 Hydroxychloroquine in COVID-19 (k=6)

The e-process declined to S_6 = 0.39, indicating that the accumulated evidence actually supports H_0 (no effect). Early trials showed mixed results, but RECOVERY and WHO SOLIDARITY firmly established no benefit. An e-value below 1 means the data are more consistent with the null than the alternative. **Verdict:** Evidence supports no effect.

---

## 4. Discussion

### 4.1 Why E-Values Matter for Living Reviews

Living systematic reviews are fundamentally incompatible with pre-specified stopping rules. New trials arrive on unpredictable schedules, the review team may not know how many trials will eventually be published, and the decision to update may depend on external factors (e.g., a pandemic). E-values resolve this tension by providing guarantees that hold regardless of the stopping rule. This is not a technical convenience — it is a mathematical necessity for valid inference in open-ended monitoring.

### 4.2 Relationship to TSA

SafeMA does not replace TSA but provides a fundamentally different paradigm. TSA remains useful when a fixed design is appropriate (e.g., a planned series of trials). For genuinely living reviews with unpredictable evidence arrival, e-values are the theoretically correct framework.

### 4.3 Limitations

The GRO e-value requires specifying an anticipated effect mu_1, similar to TSA's anticipated effect. The mixture e-value mitigates this by integrating over a prior, but the prior variance tau^2 must still be chosen. SafeMA's current implementation assumes independent studies (no within-study correlation) and fixed known variances. Extensions to random-effects e-values and correlated outcomes are planned.

---

## References

1. Brok J, Thorlund K, Gluud C, Wetterslev J. Trial sequential analysis reveals insufficient information size and potentially false positive results in many meta-analyses. *J Clin Epidemiol*. 2008;61(8):763-769.

2. Wetterslev J, Thorlund K, Brok J, Gluud C. Trial sequential analysis may establish when firm evidence is reached in cumulative meta-analysis. *J Clin Epidemiol*. 2008;61(1):64-75.

3. Grünwald P, de Heide R, Koolen W. Safe testing. *J R Stat Soc Ser B*. 2024;86(5):1091-1128.

4. Ramdas A, Grünwald P, Vovk V, Shafer G. Admissible anytime-valid sequential inference must rely on nonnegative martingales. *Ann Stat*. 2023;51(2):541-559.

5. Ter Schure J, Grünwald P. ALL-IN meta-analysis: breathing life into living systematic reviews. *F1000Research*. 2022;11:549.

6. Ville J. *Étude critique de la notion de collectif*. Gauthier-Villars; 1939.

7. Ramdas A, Wang R. Hypothesis testing with e-values. *Found Trends Stat*. 2025;1(1-2):1-390.

---

## Data Availability

Code at https://github.com/mahmood726-cyber/safema (MIT licence).

## AI Disclosure

AI was used as a constrained coding assistant. The mathematical framework follows Grünwald et al. (2024) exactly. All implementations and claims were verified by the author.
