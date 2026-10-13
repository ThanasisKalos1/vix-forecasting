"""Walk-forward forecasting and error metrics."""
import numpy as np
import pandas as pd


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
