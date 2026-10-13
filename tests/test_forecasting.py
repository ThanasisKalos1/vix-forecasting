"""Checks on information timing and model behaviour, run on a synthetic series."""
import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression

from vixforecast.evaluation import mae, rmse, walk_forward
from vixforecast.features import EXTENDED_FEATURES, HAR_FEATURES, make_features
from vixforecast.models import Arima, FeatureModel, Naive, har


@pytest.fixture
def closes():
    """A persistent positive series on business days, about seven months long."""
    rng = np.random.default_rng(1)
    values = [18.0]
    for shock in rng.normal(0, 1.2, 149):
        values.append(max(9.0, 18 + 0.95 * (values[-1] - 18) + shock))
    dates = pd.bdate_range("2021-01-04", periods=150)
    return pd.Series(values, index=dates, name="vix_close")


def test_features_use_only_past_closes(closes):
    full = make_features(closes)
    cut = 100
    truncated = make_features(closes.iloc[:cut + 1])
    pd.testing.assert_series_equal(full.iloc[cut], truncated.iloc[-1])


def test_all_features_defined_from_23rd_session(closes):
    features = make_features(closes)[EXTENDED_FEATURES]
    assert features.iloc[21].isna().any()
    assert features.iloc[22:].notna().all().all()


class Recorder:
    """Stand-in model that records what the walk-forward loop gives it."""

    name = "Recorder"

    def __init__(self):
        self.fit_dates, self.predict_dates = [], []

    def fit(self, closes):
        self.fit_dates.append(closes.index[-1])

    def predict(self, closes):
        self.predict_dates.append(closes.index[-1])
        return closes.iloc[-1]


def test_walk_forward_never_sees_the_target(closes):
    model = Recorder()
    forecasts = walk_forward(closes, model, "2021-04-01", "2021-06-30")
    targets = forecasts.index
    # The last close given to the model is always the session before the target.
    previous_session = [closes.index[closes.index.get_loc(date) - 1] for date in targets]
    assert model.predict_dates == previous_session


def test_walk_forward_refits_once_per_calendar_month(closes):
    model = Recorder()
    walk_forward(closes, model, "2021-04-01", "2021-06-30")
    # April, May and June: fitted on the last session of March, April and May.
    assert [date.month for date in model.fit_dates] == [3, 4, 5]


def test_naive_forecast_is_previous_close(closes):
    forecasts = walk_forward(closes, Naive(), "2021-04-01", "2021-06-30")
    expected = closes.shift(1).loc[forecasts.index]
    np.testing.assert_allclose(forecasts.to_numpy(), expected.to_numpy())


def test_arima_010_reproduces_naive(closes):
    naive = walk_forward(closes, Naive(), "2021-06-01", "2021-06-30")
    arima = walk_forward(closes, Arima(0, 1, 0), "2021-06-01", "2021-06-30")
    np.testing.assert_allclose(arima.to_numpy(), naive.to_numpy(), atol=1e-6)


def test_linear_model_gives_same_forecast_for_level_and_change_targets(closes):
    # With the latest close among the regressors, the two targets differ only by that close.
    level = walk_forward(closes, har(), "2021-06-01", "2021-06-30")
    change_model = FeatureModel("HAR change", LinearRegression(), HAR_FEATURES, target="change")
    change = walk_forward(closes, change_model, "2021-06-01", "2021-06-30")
    np.testing.assert_allclose(level.to_numpy(), change.to_numpy(), atol=1e-8)


def test_metrics_on_known_errors():
    actual = np.array([10.0, 12.0, 15.0])
    forecast = np.array([11.0, 12.0, 11.0])  # errors: -1, 0, 4
    assert mae(actual, forecast) == pytest.approx(5 / 3)
    assert rmse(actual, forecast) == pytest.approx(np.sqrt(17 / 3))
