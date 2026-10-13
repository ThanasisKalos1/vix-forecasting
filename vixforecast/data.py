"""Load the prepared VIX sample and define the chronological split."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# Fixed on 13 October 2026, before any model was fitted.
SPLITS = {
    "training": ("2015-01-01", "2021-12-31"),
    "validation": ("2022-01-01", "2023-12-31"),
    "test": ("2024-01-01", "2025-12-31"),
}


def load_vix(root=ROOT):
    """Return daily VIX closes indexed by session date, checked against the frozen calendar."""
    closes = pd.read_csv(
        root / "data" / "processed" / "vix_daily_2015_2025.csv",
        parse_dates=["date"], index_col="date",
    )["vix_close"]
    sessions = pd.read_csv(
        root / "data" / "calendar" / "xnys_sessions_2015_2025.csv", parse_dates=["date"]
    )["date"]
    if not closes.index.equals(pd.DatetimeIndex(sessions)):
        raise ValueError("Sample dates differ from the frozen session calendar.")
    if closes.isna().any() or (closes <= 0).any():
        raise ValueError("Unexpected missing or non-positive closes.")
    return closes
