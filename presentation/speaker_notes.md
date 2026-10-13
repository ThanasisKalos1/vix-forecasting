# Opening presentation — speaker notes

## 1. One-Day-Ahead VIX Forecasting
This study asks whether historical VIX observations can help predict its next trading-day closing level. The comparison includes ARIMA, Random Forest and a naive forecast. These are opening proposal slides; the empirical work has not yet been completed.

## 2. Does complexity improve the forecast?
The naive forecast uses today's close as tomorrow's prediction. The interesting question is whether the fitted models improve on this simple reference point. Beating ARIMA alone would not establish improvement over the naive model. Any conclusion must be limited to the sample and evaluation procedure.

## 3. One index. Two different horizons.
The VIX is derived from S&P 500 option prices and represents 30-calendar-day implied volatility on an annualised scale. We predict tomorrow's value of that index, not tomorrow's realised volatility. Option-implied volatility is not a guarantee of subsequent realised volatility.

Source: Cboe Global Markets, VIX Methodology, https://cdn.cboe.com/api/global/us_indices/governance/VIX_Methodology.pdf (consulted 8 October 2026).

## 4. Daily VIX closes, 2015–2025

Data preparation is complete: 2,766 observations after excluding 27 non-session dates using the frozen NYSE calendar. All expected sessions are present; early closes are retained. The period covers eleven calendar years. Training, validation and test boundaries remain provisional and must be fixed before performance comparison. Descriptive statistical analysis is the next stage. Weekends and non-session holidays are not filled to create a daily calendar.

## 5. Three methods. A common target.
Naive forecasting carries the latest close forward. ARIMA combines autoregressive terms, differencing if justified, and moving-average terms based on past innovations. Random Forest averages regression trees trained on lagged values and possibly trailing summaries. Its inputs must explicitly encode historical information. The feature set, orders and hyperparameters have not yet been chosen.

## 6. Judge performance on unseen dates
All methods predict the same target dates using information available at the forecast origin. After a day's close becomes available, it can inform later predictions, including within the test period. Test performance must not guide model selection. The parameter-refitting schedule remains to be specified. MAE and RMSE are reported in VIX index points, and RMSE places greater influence on large errors. Differences in these metrics do not by themselves establish statistical significance.
