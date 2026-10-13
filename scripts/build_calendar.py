"""Freeze regular US equity session dates, including shortened sessions."""
import csv
import hashlib
import json
from pathlib import Path
from importlib.metadata import version

import exchange_calendars as xcals

ROOT = Path(__file__).resolve().parents[1]
START, END = "2015-01-01", "2025-12-31"
calendar = xcals.get_calendar("XNYS", start="2014-12-01", end="2026-01-31")
sessions = calendar.sessions_in_range(START, END)
dates = set(sessions.strftime("%Y-%m-%d"))

# Regression checks for exceptional closures, holiday-rule changes and early closes.
for day in ("2018-12-05", "2025-01-09", "2022-06-20", "2024-07-04"):
    if day in dates:
        raise ValueError(f"Known closure incorrectly included: {day}")
for day in ("2021-06-18", "2021-12-31", "2024-07-03", "2024-11-29"):
    if day not in dates:
        raise ValueError(f"Known session incorrectly excluded: {day}")

out = ROOT / "data/calendar"
out.mkdir(parents=True, exist_ok=True)
path = out / "xnys_sessions_2015_2025.csv"
with path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["date"])
    writer.writerows((day,) for day in sorted(dates))
metadata = {
    "calendar": "XNYS",
    "implementation": "exchange_calendars",
    "version": version("exchange_calendars"),
    "implementation_source": "https://github.com/gerrymanoim/exchange_calendars",
    "start": START, "end": END, "sessions": len(dates),
    "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
    "policy": "Keep all NYSE regular-session dates, including early closes. This library-generated calendar is not an exchange-issued dataset.",
}
(out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
print(json.dumps(metadata, indent=2))
