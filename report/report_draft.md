# One-Day-Ahead VIX Forecasting
## Comparing ARIMA, Random Forest and a Naive Benchmark

University of Cyprus · MSc Data Science · Time Series Analysis

**Working research draft — 8 October 2026.** This document contains the opening and proposed methodology. No dataset has been inspected and no empirical results are available. The final presentation is due 30 November 2026.

## 1. Introduction

The Cboe Volatility Index (VIX) measures option-implied expectations of S&P 500 volatility over the next 30 calendar days, expressed on an annualised basis [1]. It is derived from option prices and is distinct from realised volatility calculated from observed market returns. This study concerns the next trading day's VIX closing level. Its one-day forecasting horizon is therefore different from the 30-day volatility horizon represented by the index.

The research investigates whether modelling historical VIX observations improves forecasts relative to carrying forward the most recent closing value. ARIMA and Random Forest provide two different approaches to extracting information from the same historical series. ARIMA models linear temporal relationships, while Random Forest can learn nonlinear relationships among features constructed from past observations. More complex modelling does not guarantee better out-of-sample predictions; the naive benchmark makes this a directly testable question.

The main research question is: **Does Random Forest improve one-trading-day-ahead VIX forecasting accuracy relative to ARIMA and a naive benchmark when predictions use only historical VIX observations?** A secondary descriptive question is whether differences in forecast errors are widespread or concentrated around a small number of large VIX movements.

The intended contribution is a transparent forecasting comparison with chronological evaluation and a common information set. The study will not interpret success on this sample as evidence of universal model superiority or trading profitability.

## 2. Index and proposed sample

**Data update — 13 October 2026:** The Cboe source has now been downloaded and reconciled to a frozen NYSE regular-session calendar (XNYS, exchange_calendars 4.13.2). The modelling sample has 2,766 observations from 2 January 2015 to 31 December 2025. The original date-range extract has 2,793 observations; 27 non-session dates were excluded and logged. All expected regular-session dates are present, including early closes. No values were imputed or modified. The proposal text below describes the earlier planning stage; data documentation and the audit provide the current verified status. Forecasts target the next regular-session date and are issued only after the preceding Cboe closing value is available.

The proposed dataset consists of daily VIX index closing observations from 1 January 2015 to 31 December 2025, retaining the available trading-day observations within those dates. The target is the VIX index itself, rather than a VIX futures contract or an exchange-traded product. Weekends and market holidays are not extra forecasting steps. Missing observations within the trading calendar will be investigated rather than automatically filled.

The sample spans eleven calendar years and predates the project. Its inclusion of the COVID-19 period provides a reason to investigate unusual observations and changing forecasting conditions; it does not establish robustness across all market conditions. Exact coverage, observation counts, source provenance and data quality remain to be verified. The Cboe methodology cited here is a definition source, not evidence that the historical dataset has already been downloaded.

The provisional chronological split is:

| Role | Period | Purpose |
|---|---|---|
| Training | 2015–2021 | Estimate candidate models |
| Validation | 2022–2023 | Select model orders, features and hyperparameters |
| Test | 2024–2025 | Evaluate the selected procedures |

The boundaries will be fixed before comparing performance. A single split offers a manageable experiment but cannot establish performance stability across every possible evaluation window.

## 3. Proposed methodology

### Forecast target and information timing

Let y_t be the VIX closing level on trading day t. Each prediction targets y_(t+1) and is issued after y_t is available. Features must use only information observed through t. Earlier test observations may enter later forecasts as time advances; test errors must not guide model selection.

### Naive benchmark

The naive forecast is y-hat_(t+1|t) = y_t. It has no fitted parameters and establishes whether the other models improve on carrying today's closing value forward.

### ARIMA

ARIMA(p,d,q) combines autoregressive terms, differencing and moving-average terms based on past innovations. The differencing order d will be justified using training-period diagnostics; d = 0 remains a valid possibility. A small candidate set and chronological validation will keep selection manageable. Orders and diagnostics have not yet been determined.

### Random Forest

Random Forest averages predictions from an ensemble of regression trees. Historical observations must first be converted into supervised-learning examples, pairing features available at t with the next trading day's closing level. Candidate inputs include recent VIX levels and trailing summaries. Exact features and a small hyperparameter search will be defined before test evaluation. Trees do not automatically represent temporal order, and leaf-average predictions may struggle with outcomes beyond the range represented in training data.

### Evaluation

MAE and RMSE will be calculated on the same target dates in VIX index points. For errors e_i = y_i − y-hat_i and n forecasts:

- MAE = (1/n) × sum(|e_i|).
- RMSE = sqrt((1/n) × sum(e_i²)).

RMSE gives greater influence to large errors. If the metrics rank models differently, that difference will be discussed rather than hidden. After selection, fitted models can be re-estimated using data through the end of 2023. Parameter-refitting frequency and the treatment of model-state updates remain to be specified before testing. Neither lower average error nor a visual difference alone establishes statistical significance.

## 4. Remaining report sections

The literature review will be developed from verified forecasting and VIX research. Exploratory analysis, model diagnostics, empirical results, discussion, conclusion and abstract will be written after the relevant work is completed. No performance claims are available at this stage.

## References

[1] Cboe Global Markets. *Volatility Index Methodology: Cboe Volatility Index.* https://cdn.cboe.com/api/global/us_indices/governance/VIX_Methodology.pdf (consulted 8 October 2026).

## Progress log

- 8 October: research question, opening text, sample proposal and model comparison drafted.
- Pending: confirm assessment requirements, obtain and inspect data, verify methodological literature, and finalise the evaluation protocol.
- Priority: complete analysis with time left for the mandatory presentation and rehearsal before 30 November.
