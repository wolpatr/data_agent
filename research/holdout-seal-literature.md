# Holdout seal & leakage literature — fact-finding (v0.3 governance)

**Date:** 2026-11-10
**Prepared for:** v0.3 governance — sealed holdout timerange 2026-08-10 → 2026-11-10 (BTC/USDT hourly, freqtrade FreqAI classifiers; reference protocol arXiv 2606.00060: 12m-train / 3m-val / 3m-test sliding folds).
**Rule under underwriting:** results on the holdout are computed exactly once per proposal; any re-sweep against the holdout is logged as a manual intervention.

---

## Method & verification status

Checked against publisher registries and full texts on 2026-11-10: Crossref/DOI records, arXiv API + full-text HTML, NBER, ScienceDirect (article page), Wiley product page, Open Library, scikit-learn 1.9.1 docs, OTexts, Semantic Scholar. No paywalled body text was obtained where a publisher blocked it; such sources are marked accordingly. Two arXiv IDs often attached to this literature in informal notes were checked and are **wrong** (arXiv 2202.06695 is a graphene paper; 1907.13620 is a clinical-trials paper) — the correct IDs verified here are **2207.07048** (Kapoor & Narayanan) and **1905.11744** (Cerqueira et al.).

Status legend: **Verified** = bibliographic record AND quotable text fetched this session. **Bibliographic-only** = record verified, text not retrievable (paywall or PDF-binary). **Secondary-verified** = content relayed through another source whose text was fetched this session.

---

## 1. Tashman (2000) — rolling-origin evaluation

**Citation (verified, Crossref + ScienceDirect):** Leonard J. Tashman, "Out-of-sample tests of forecasting accuracy: an analysis and review," *International Journal of Forecasting* 16(4):437–450 (Oct 2000). DOI 10.1016/S0169-2070(00)00065-0. ~950–1,060 citations (Crossref / Semantic Scholar). **Verified** (ScienceDirect abstract page fetched in full).

**Quotable findings (from the fetched abstract):**

> "In evaluations of forecasting accuracy… researchers have paid attention to the selection of time series and to the appropriateness of forecast-error measures. However, they have not formally analyzed choices in the implementation of out-of-sample tests, making it difficult to replicate and compare forecasting accuracy studies."

> "The issues examined include series-splitting rules, **fixed versus rolling origins**, updating versus recalibration of model coefficients, fixed versus rolling windows, **single versus multiple test periods**, diversification through multiple time series, and design characteristics of forecasting competitions."

> "For individual time series, the **efficiency and reliability of out-of-sample tests can be improved by employing rolling-origin evaluations, recalibrating coefficients, and using multiple test periods**."

**Reading for our case:**
- (a) *Sealed holdout use:* Tashman does not prescribe a one-shot sealed set; his frame is how to structure out-of-sample tests rigorously (splitting rules, origins, test periods).
- (b) *Consult frequency:* prescribes **multiple test periods** with rolling origins *for estimation accuracy*; it is silent on a single sealed final window's re-use.
- (c) *Purging/embargo:* not covered.
- (d) *Multiple comparisons:* not covered.
- Verified standard-textbook rendering of the same idea: Hyndman & Athanasopoulos, *Forecasting: Principles and Practice*, §5.10 (OTexts, fetched): "This procedure is sometimes known as 'evaluation on a rolling forecasting origin' because the 'origin' at which the forecast is based rolls forward in time", and "no future observations can be used in constructing the forecast."

---

## 2. Cerqueira, Torgo & Mozetič (2020) — holdout vs rolling-origin vs CV

**Citation (verified, arXiv API):** Vitor Cerqueira, Luis Torgo, Igor Mozetič, "Evaluating time series forecasting models: an empirical study on performance estimation methods," *Machine Learning* 109:1997–2028 (2020). DOI 10.1007/s10994-020-05910-7. arXiv:1905.11744. **Verified** (arXiv full text fetched).

**Quotable findings (from fetched full text):**

> "…empirical experiments suggest that cross-validation approaches can be applied to stationary time series. However, in real-world scenarios, when different sources of non-stationary variation are at play, **the most accurate estimates are produced by out-of-sample methods that preserve the temporal order of observations**." (abstract)

> On Tashman: "In order to produce a robust estimate of predictive performance, **Tashman [2000] recommends employing these strategies in multiple test periods**." And: "OOS methods can be applied in several windows for more robust estimates, as recommended by Tashman."

> "In general, **cross-validation procedures tend to under-estimate the error (i.e. are optimistic estimators)**, while the prequential and out-of-sample variants tend to over-estimate the error (i.e. are pessimistic estimators)."

> Final remarks: "…when non-stationarities are present, they [CV variants] systematically provide worse estimations than the out-of-sample approaches…" and "**In particular, out-of-sample applied in multiple testing periods (Rep-Holdout) is recommended.**"

> Gap-type separation inside CV/streaming variants: the hv-Blocked CV "also removes adjacent observations between the training and test sets. Effectively, this creates a **gap** between both sets"; the prequential block variant with gap "comprises a block separating the training and testing blocks **in order to increase the independence between the two parts of the data**."

**Reading for our case:**
- (a) *Sealed holdout:* supports a two-part structure — estimation on ordered splits, with a final untouched validation window used as the ground-truth loss (`L^m`) in their own experiment design ("the model is re-trained… and tested on the validation set… the ground truth loss").
- (b) *Consult frequency:* their ground-truth window is consulted once per compared model; no repeated adaptation to it.
- (c) *Purging/embargo:* non-finance lineage of gap removal (CV-Mod removes observations correlated with the test set; CV-hvBl creates an explicit gap).
- (d) *Multiple comparisons:* not covered.

---

## 3. Bergmeir & Benítez (2012) — when k-fold CV is defensible for time series

**Citation (verified, Crossref):** Christoph Bergmeir, José M. Benítez, "On the use of cross-validation for time series predictor evaluation," *Information Sciences* 191:192–213 (May 2012). DOI 10.1016/j.ins.2011.12.028. ~1,300+ citations. Note: the journal is *Information Sciences*, not Knowledge and Information Systems as sometimes assumed. **Bibliographic-only** (Elsevier abstract elided by Semantic Scholar; ScienceDirect body not fetched).

**Verified secondary description (Cerqueira et al. 2020 full text, section 2.3.2 — fetched):**

> "Bergmeir and Benítez [2012] present a comparative study of estimation procedures using stationary time series. Their empirical results show evidence that in such conditions **cross-validation procedures yield more accurate estimates than an OOS approach**. Despite the theoretical issue of applying standard cross-validation, they found no practical problem in their experiments. Notwithstanding, **the Blocked cross-validation is suggested for performance estimation using stationary time series**."

> Follow-up (Bergmeir, Hyndman & Koo 2018, *Computational Statistics & Data Analysis* 120:70–83, bibliographic verified via Cerqueira's reference list): CV is suggested to be "**a better choice than OOS [Holdout] evaluation**" **"as long as the data are well fitted by the model"** (i.e., a correctly specified autoregressive model whose innovations are uncorrelated — that independence condition, not calendar ordering alone, is what licenses k-fold).

**Reading for our case:**
- (b) *Consult frequency:* n/a.
- (c) *Purging/embargo:* the k-fold admissibility conditions (stationarity / white-noise innovations under a correctly specified autoregressive model) are the non-finance counterpart of finance's purge-embargo machinery: when labels overlap, those conditions fail.
- (d) *Multiple comparisons:* not covered.
- Directly relevant: hourly BTC data with trend/seasonality (non-stationary regime variation) fails the condition; the B&B escape hatch does not apply to our sweep.

---

## 4. Kapoor & Narayanan (2022/2023) — leakage taxonomy, reproducibility crisis, and the seal

**Citation (verified, arXiv + Crossref):** Sayash Kapoor, Arvind Narayanan, "Leakage and the reproducibility crisis in ML-based science," arXiv:2207.07048 (2022); published in *Patterns* 4(7):100804 (Sep 2023). DOI 10.1016/j.patter.2023.100804 (~1,560 citations). **Verified** (arXiv full text fetched; Patterns record via Crossref).

**Quotable findings (from fetched full text):**

> Taxonomy headline: "we find 17 fields where errors have been found, **collectively affecting 329 papers**… leading to wildly overoptimistic conclusions." Their survey covers 20 method-review papers across those fields.

> "[L1.1] No test set. Using the same dataset for training as well as testing the model is a **text-book example of overfitting**, which leads to overoptimistic performance estimates."

> "[L3.1] **Temporal leakage.** When an ML model is used to make predictions about a future outcome of interest, **the test set should not contain any data from a date before the training set**. If the test set contains data from before the training set, the model is built using data 'from the future'…"

> "[L3.2] **Nonindependence between train and test samples constitutes leakage**, unless the scientific claim is about a distribution that has the same dependence structure."

> The closest published anchor for *sealing*: "In predictive modeling competitions… **none of the participants have access to the held-out evaluation set before the competition ends**. In contrast, in most ML-based science the researcher has access to the entire dataset while creating the ML models. **Leakage often occurs due to the researcher having access to the entire dataset during the modeling process.**"

> Required arguments before a claim (their "model info sheets"): "[L1] **Clean train-test separation.** …why the test set does not interact with training data during any of the preprocessing, modeling or evaluation steps"; "[L2] Each feature in the model is legitimate"; "[L3] **Test set is drawn from the distribution of scientific interest.**"

> Recommendation [R4]: "Adopt the common task framework when possible. The common task framework allows us to compare the performance of competing ML models using an agreed-upon training dataset and evaluation metrics, **a secret holdout dataset**, and a public leaderboard."

**Reading for our case:**
- (a) *Sealed holdout:* strongest general-ML support — the seal is the institutional fix for "the researcher has access to the entire dataset."
- (b) *Consult frequency:* the competition contrast implies **no access until the seal is "opened"**; K&N do not publish a numeric re-consult budget.
- (c) *Purging/embargo:* L3.2 covers dependence between train/test samples (generic); no financial-label-overlap machinery.
- (d) *Multiple comparisons:* not covered here (see §6).

---

## 5. López de Prado (2018), *Advances in Financial Machine Learning* — purged CV, embargo, CPCV

**Citation (verified, Wiley + Open Library):** Marcos López de Prado, *Advances in Financial Machine Learning*, John Wiley & Sons, February 2018, ISBN 978-1-119-48208-6, ~400 pp. **Bibliographic-only** (book body paywalled; description fetched from Wiley: readers learn to "back test their discoveries **while avoiding false positives**").

**What the book contributes (paraphrase; book text not fetched — flagged as unverified wording):** the classic chapters on cross-validation in finance introduce (i) **Purged K-Fold CV (PKCV)**: remove from the training set those observations whose labels overlap the evaluation period (because labels computed over a forward window overlap train/test boundaries), and (ii) an **embargo** gap past the test boundary to eliminate serial-correlation leakage, and (iii) **Combinatorial Purged Cross-Validation (CPCV)**: replicate many complementary backtest paths to estimate the distribution of post-selection performance. Chapter attributions commonly cited: Ch. 7 "Cross-Validation in Finance" (purging/embargo/PKCV, walk-forward), Ch. 12 (CPCV), Ch. 14 (backtest overfitting). These exact chapter placements were **not independently verified here**; treat as secondary.

**Peer-reviewed companions (verified):** the formal companion is Bailey, Borwein, López de Prado & Zhu's PBO/CSCV paper (§6), published in the *Journal of Computational Finance* (DOI 10.21314/jcf.2016.322; SSRN preprint abstract fetched via Crossref). Crossref/S2 searches today for a dedicated peer-reviewed "purged CV" follow-up surfaced no directly on-point journal paper; nearest are the preprint Arian, Norouzi Mobarekeh & Seco, "Backtest Overfitting in the Machine Learning Era: A Comparison of Out-of-Sample Testing Methods in a Synthetic Controlled Environment," SSRN (2024), DOI 10.2139/ssrn.4778909 (**bibliographic-only**), plus a 2026 SSRN methodology note applying purged CV to NPL valuation (DOI 10.2139/ssrn.6740278, bibliographic-only).

**Reading for our case:**
- (c) *Purging/embargo:* the finance-specific prescription. Non-finance analogs verified above (Cerqueira's CV-Mod/CV-hvBl gap; sklearn's `TimeSeriesSplit(gap=…)` — "Number of samples to exclude from the end of each train set before the test set", fetched from the 1.9.1 API docs).
- (d) *Multiple comparisons:* CPCV's purpose is exactly estimating the distribution of post-selection performance over many trial configurations.

---

## 6. Backtest overfitting & multiple-comparison deflation for sweep-heavy workflows

### 6.1 Bailey, Borwein, López de Prado & Zhu — "The Probability of Backtest Overfitting"

**Citation (verified via Crossref):** preprint: SSRN (DOI 10.2139/ssrn.2326253, 2013, abstract fetched); published: *Journal of Computational Finance* (DOI 10.21314/jcf.2016.322, issued 2016-09). **Verified** for the abstract; body bibliographic-only.

> "**Standard statistical techniques designed to prevent regression over-fitting, such as hold-out, tend to be unreliable and inaccurate in the context of investment backtests.** We propose a framework that estimates the probability of backtest over-fitting (PBO)… We show that CSCV produces accurate estimates of the probability that a particular backtest is over-fit." (fetched abstract; the estimator is "combinatorially symmetric cross-validation (CSCV)")

### 6.2 Bailey, Borwein, López de Prado & Zhu — "Pseudo-Mathematics and Financial Charlatanism"

**Citation (verified, Crossref):** *Notices of the American Mathematical Society* 61(5):458 (May 2014). DOI 10.1090/noti1105. **Bibliographic-only** (AMS PDF returned binary; text not extracted). Paraphrase (unverified wording): the article popularized the PBO framework for non-specialists — evaluating many strategy variants on a fixed window without accounting for the number of trials inflates the winner's apparent out-of-sample performance; it demonstrates this on seven S&P-500-style strategy selection examples and supplies mathematical appendices on the expected maximum of Sharpe ratios across N trials.

### 6.3 Bailey & López de Prado — "The Deflated Sharpe Ratio"

**Citation (verified via Crossref):** *The Journal of Portfolio Management* 40(5):94–107 (fall 2014). DOI 10.3905/jpm.2014.40.5.094. Preprint abstract (DOI 10.2139/ssrn.2460551) fetched. **Verified** for the abstract.

> "Backtest optimizers search for combinations of parameters that maximize the simulated historical performance of a strategy, leading to backtest overfitting. … **Not controlling for the number of trials involved in a particular discovery leads to over-optimistic performance expectations.**" And: "The **Deflated Sharpe Ratio (DSR) corrects for two leading sources of performance inflation: Selection bias under multiple testing and non-Normally distributed returns**. In doing so, DSR helps separate legitimate empirical findings from statistical flukes."

Computationally, DSR uses the **number of independent trials N**, the **variance of the trials' Sharpe-type metrics**, and the trial-return skew/kurtosis — i.e., a workflow must *record its sweep matrix* to be auditable (that input requirement is the policy-relevant fact; exact formula in the JPM paper, bibliographic-only here).

### 6.4 Harvey, Liu & Zhu — multiple-testing hurdle in financial research

**Citation (verified, Crossref + NBER):** Campbell R. Harvey, Yan Liu, Heqing Zhu, "… and the Cross-Section of Expected Returns," *Review of Financial Studies* 29(1):5–68 (2016). DOI 10.1093/rfs/hhv059 (~2,180 citations). NBER WP 20592 abstract fetched. **Verified** for the abstract.

> "Given this extensive data mining, it does not make any economic or statistical sense to use the usual significance criteria for a newly discovered factor, e.g., a t-ratio greater than 2.0. … The estimation of our model suggests that a newly discovered factor needs to clear a much higher hurdle, **with a t-ratio greater than 3.0**. … we argue that **most claimed research findings in financial economics are likely false**."

**Verdict for sweep-heavy evaluation (facts, per the verified texts):** one headline number chosen from many configurations against any evaluation surface (val folds *or* holdout) is inflated under selection; the peer-reviewed remedies are (i) estimate PBO over the trial matrix (CSCV), (ii) deflate the best-performer's Sharpe with trial count/variance (DSR), (iii) apply a much stricter significance hurdle when many experiments precede the claim (Harvey et al.), and (iv) keep ordering/overlap discipline inside folds (purge/embargo). A single sealed holdout consulted once reduces but does not eliminate inflation from the sweep itself, because **the sweep over the validation folds is itself the multiple-testing event** — this is the explicit thesis of §6.1's first sentence (hold-out is "unreliable and inaccurate" *in the context of investment backtests*).

---

## 7. Governance / benchmark-integrity angle

**Bouthillier et al. (2021) — variance in benchmarks.** Citation (verified, arXiv API): Xavier Bouthillier et al., "Accounting for Variance in Machine Learning Benchmarks," arXiv:2103.03098 (submitted to MLSys 2021 per arXiv comment). **Verified** (abstract). Quotes: "We model the whole benchmarking process, revealing that **variance due to data sampling, parameter initialization and hyperparameter choice impact markedly the results**."; "adding more sources of variation to an imperfect estimator approaches better the ideal estimator **at a 51 times reduction in compute cost**." Relevance: single-run, single-window comparisons are noisy; a one-consultation policy should also fix the random seeds and record that the consult is one sample of a noisy estimator.

**scikit-learn documentation (1.9.1, fetched):** the de-facto general-ML position on test-set discipline:
> "**Test data should never be used to make choices about the model.**" and "Data leakage occurs when information that would not be available at prediction time is used when building the model." (User Guide §12 "Common pitfalls and recommended practices")
> `TimeSeriesSplit`: "Provides train/test indices to split time-ordered data, where other cross-validation methods are inappropriate, as they would lead to **training on future data and evaluating on past data**." Its `gap` parameter is a first-class embargo: "Number of samples to exclude from the end of each train set before the test set."

**Kapoor & Narayanan** (§4) complete the governance picture: report/justify (model info sheets with the L1/L2/L3 arguments), standardize (common task framework with "a secret holdout dataset"), and audit code+data (computational reproducibility, R5).

---

## Contradictions and tensions between the sources (facts, not resolved here)

1. **Estimation-accuracy vs post-selection-overfitting lenses.** Tashman/Cerqueira optimize *how well you estimate a model's loss* (multi-period rolling origin wins for non-stationary real-world series). Bailey/de Prado/Harvey optimize *whether the post-selection claim from a sweep survives* (single-window numbers — including holdouts — are unreliable once many trials have been run). Both can be true for one workflow; neither source denies the other, but they weight different failure modes.
2. **k-fold admissibility.** Bergmeir & Benítez (2012)/Bergmeir-Hyndman-Koo (2018) license k-fold under stationarity/white-noise innovations of a correctly specified autoregressive model; Cerqueira's 62 real-world series and the purged-CV finance line reject it once non-stationarity/overlapping labels are present. Our regime (hourly BTC with regime shifts + FreqAI label horizons) sits on the "conditions fail" side of that split.
3. **Holdout as shield vs holdout as trial.** sklearn/K&N treat the untouched test set as the integrity device; the PBO/DSSR line treats any number — including a holdout number — as one draw that must be deflated across trials. The literature does not declare a canonical "allowed number of holdout consultations"; the closest quantitative anchors are (i) the competition framework: **zero access until the seal opens** (K&N), and (ii) DSR/PBO: **every consult is a trial that must be counted**.
4. **No numeric embargo formula exists as the standard rule.** Purge width is tied to the label-overlap horizon (finance) or the dependence structure (general ML); the concrete number is dataset-specific (e.g., sklearn's `gap` parameter).

---

## Design implications for the v0.3 policy file

Facts → possible policy handles only; no decision made.

- **Two named layers are supported by the literature:** a *sweep layer* (sliding 12m/3m/3m rolling-origin folds per Tashman/TimeSeriesSplit) and a *seal layer* (final 2026-08-10→2026-11-10 window untouched until a one-shot confirmation per proposal, per K&N's competition contrast + sklearn's "test data should never be used to make choices about the model").
- **Consultation budget:** no source prescribes an exact re-consult count; the defensible published anchors are "no access before the seal opens" (qualitative) and "each consult is a trial to be logged" (quantitative lineage: DSR needs trial counts). A policy option is: exactly one holdout evaluation per proposal (as frozen today); any re-sweep entered into an interventions log *and* counted in a persistent trials ledger.
- **Purge/embargo knob:** a concrete, implementable prescription exists on both lines — purge samples whose labels overlap the boundary + embargo `gap` bars after the boundary (AFML finance-side, unverified-wording; Cerqueira CV-hvBl/CV-Mod and sklearn `TimeSeriesSplit(gap=…)` verified). Policy could require: fold boundaries and seal boundary both carry `gap ≥ label lookahead horizon`, with the value recorded per experiment.
- **Ordering discipline inside folds:** k-fold/shuffled splits are contradicted for our data class (Cerqueira real-world result; B&B admissibility conditions fail); policy option: forbid shuffle-based splitters anywhere in the sweep.
- **Sweep ledger for deflation:** DSR/PBO are computable only if the runner persists the full per-configuration metric matrix (trial count N, per-trial metrics' mean/variance, seeds). Policy option: make the results matrix a required artifact of every sweep, so deflation is computable later without re-running.
- **Pre-seal manifest (preregistration-style):** K&N's three required arguments map directly to a manifest per proposal: (L1) statement of clean separation (incl. purge/embargo at the seal boundary), (L2) feature-legitimacy note for the feature/indicator set, (L3) statement that the seal is the distribution of scientific interest (pair, exchange, timeframe). Freeze timestamp on the manifest before the one holdout consult.
- **Reporting:** the holdout result should be published together with its trial context (N configurations tried on the val folds, seeds, fold list) — this is what makes a one-shot holdout number interpretable under Harvey/DSR/PBO rather than bare.
- **Known gap:** the literature does not define what happens *after* a failed holdout consult (re-search + re-seal would restart the trial counter); a policy statement on that restart semantics would be novel relative to these sources, not supported by them.
