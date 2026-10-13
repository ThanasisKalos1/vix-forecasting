"""Forecasting models with a common interface.

Each model has two methods:

    fit(closes)      estimate parameters from closes up to and including the forecast origin
    predict(closes)  forecast the next close from the same kind of history, parameters held fixed

`closes` is a pandas Series of VIX closes indexed by session date.
"""
import warnings

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA

from .features import EXTENDED_FEATURES, HAR_FEATURES, HISTORY_NEEDED, make_features

RANDOM_SEED = 0


class Naive:
    """Carry the latest close forward."""

    name = "Naive"

    def fit(self, closes):
        pass

    def predict(self, closes):
        return closes.iloc[-1]


class Arima:
    """ARIMA(p, d, q) on the level, with a constant only when d = 0."""

    def __init__(self, p, d, q):
        self.order = (p, d, q)
        self.trend = "c" if d == 0 else "n"
        self.name = f"ARIMA({p},{d},{q})"
        self.params = None
        self.failed_fits = []  # origins at which re-estimation did not converge

    def _model(self, closes):
        return ARIMA(closes.to_numpy(), order=self.order, trend=self.trend)

    def fit(self, closes):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # convergence is checked explicitly below
            result = self._model(closes).fit()
        if result.mle_retvals["converged"]:
            self.params = result.params
            return
        # Protocol: keep the previous parameters and log the event;
        # a candidate whose first estimation fails is dropped.
        self.failed_fits.append(closes.index[-1])
        if self.params is None:
            raise RuntimeError(f"{self.name}: first estimation did not converge.")

    def predict(self, closes):
        # Run the filter over the history with the stored parameters, then step one session ahead.
        return self._model(closes).filter(self.params).forecast(1)[0]


class FeatureModel:
    """Regression of the next close, or the next change, on features of past closes."""

    def __init__(self, name, estimator, columns, target="level"):
        if target not in ("level", "change"):
            raise ValueError("target must be 'level' or 'change'")
        self.name = name
        self.estimator = estimator
        self.columns = columns
        self.target = target

    def fit(self, closes):
        features = make_features(closes)
        outcome = closes.shift(-1)  # the next session's close
        if self.target == "change":
            outcome = outcome - closes
        # Keep origins where every feature is defined and the next close is already known.
        usable = features.notna().all(axis=1) & outcome.notna()
        self.estimator.fit(features.loc[usable, self.columns], outcome[usable])

    def predict(self, closes):
        latest = make_features(closes.iloc[-HISTORY_NEEDED:])[self.columns].iloc[[-1]]
        prediction = self.estimator.predict(latest)[0]
        return prediction if self.target == "level" else closes.iloc[-1] + prediction


def har():
    """HAR regression: next close on the latest close and its 5- and 22-session means."""
    return FeatureModel("HAR", LinearRegression(), HAR_FEATURES, target="level")


def forest(target, features, min_samples_leaf, split_features):
    """Random Forest candidate.

    `features` is 'har' or 'extended'. `split_features` is 'third' (one third of the
    features considered at each split, rounded down, at least one) or 'all'.
    """
    columns = HAR_FEATURES if features == "har" else EXTENDED_FEATURES
    estimator = RandomForestRegressor(
        n_estimators=500,
        min_samples_leaf=min_samples_leaf,
        max_features=1 / 3 if split_features == "third" else 1.0,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    name = f"RF({target}, {features}, leaf={min_samples_leaf}, split={split_features})"
    return FeatureModel(name, estimator, columns, target=target)
