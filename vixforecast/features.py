"""Features built from past closes only.

Every column on a given row uses closes up to and including that row's date,
so a row can be used to forecast the following session.
"""
import pandas as pd

HAR_FEATURES = ["close", "mean_5", "mean_22"]
EXTENDED_FEATURES = HAR_FEATURES + ["change_1", "change_5", "vol_5", "vol_22"]

# Closes needed before every feature is defined: 22 daily changes need 23 closes.
HISTORY_NEEDED = 23


def make_features(closes):
    """Return one row of features per session; early rows contain NaN until enough history exists."""
    change = closes.diff()
    return pd.DataFrame({
        "close": closes,
        "mean_5": closes.rolling(5).mean(),
        "mean_22": closes.rolling(22).mean(),
        "change_1": change,
        "change_5": closes.diff(5),
        "vol_5": change.rolling(5).std(),
        "vol_22": change.rolling(22).std(),
    })
