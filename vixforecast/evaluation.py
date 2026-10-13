"""Walk-forward forecasting and error metrics."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm


def walk_forward(closes, model, start, end):
    """Return one-step forecasts for every session from `start` to `end`.

    Parameters are re-estimated before the first forecast of each calendar month,
    using all closes before that target date. For the rest of the month they are
    held fixed and only the history passed to `predict` grows.
    """
    targets = closes.loc[start:end].index
    forecasts = pd.Series(index=targets, dtype=float, name=model.name)
    fitted_month = None
    for date in targets:
        history = closes.iloc[:closes.index.get_loc(date)]  # strictly before the target date
        month = (date.year, date.month)
        if month != fitted_month:
            model.fit(history)
            fitted_month = month
        forecasts[date] = model.predict(history)
    return forecasts


def mae(actual, forecast):
    """Mean absolute error."""
    return float(np.mean(np.abs(actual - forecast)))


def rmse(actual, forecast):
    """Root mean squared error."""
    return float(np.sqrt(np.mean((actual - forecast) ** 2)))


def clark_west(actual, benchmark, model, lags):
    """Clark–West test that a larger model adds predictive content to a benchmark nested in it.

    The larger model's squared error is first reduced by the squared gap between the two
    forecasts, which removes the noise that estimating extra parameters adds under the null.
    Returns the statistic and the one-sided p-value; large positive values favour the larger model.
    """
    actual, benchmark, model = (np.asarray(x, dtype=float) for x in (actual, benchmark, model))
    adjusted = (actual - benchmark) ** 2 - ((actual - model) ** 2 - (benchmark - model) ** 2)
    fit = sm.OLS(adjusted, np.ones(len(adjusted))).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    statistic = float(fit.tvalues[0])
    return statistic, float(norm.sf(statistic))
