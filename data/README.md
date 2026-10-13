# VIX research data

Source: [Cboe historical VIX data](https://www.cboe.com/tradable-products/vix/vix-historical-data/).
The direct CSV endpoint is recorded in `data_audit.json` and the preparation script.

`raw/VIX_History.csv` is the unmodified downloaded source. `processed/vix_daily_2015_2025.csv` contains only `date` (ISO trading date) and `vix_close` (VIX index points), for 2015 through 2025 inclusive. This is the VIX index close, not futures settlement or realised volatility.

Rebuild from the saved raw snapshot, from the project root in PowerShell:

```powershell
./scripts/prepare_data.ps1
```

To download the current source and rebuild:

```powershell
./scripts/prepare_data.ps1 -Download
```

The source can change. SHA-256 hashes and the raw file timestamp identify the local snapshot; a fresh download may produce different hashes. No missing-value imputation, interpolation, outlier deletion, scaling or statistical transformation is performed.

`data_audit.json` records coverage and structural checks. `absent_weekdays.csv` lists weekdays absent from the raw source, now verified as non-session dates. `excluded_dates.csv` lists source dates excluded from the modelling sample. Weekends and holidays are not inserted or filled.

Raw and processed data are local and excluded from Git by default. The repository publishes retrieval instructions and audit metadata; it does not assign a licence to Cboe data.

The report's training/validation/test dates were fixed on 13 October 2026, before any model was fitted. Structural validation is not model selection. Model selection has used the training and validation periods only; the test period has not been evaluated.

## Calendar policy — 13 October 2026

Final modelling sample: **2,766 observations**, with **27 source dates excluded** and **zero missing expected sessions**. Coverage remains 2015-01-02 through 2025-12-31. Each retained value is the original Cboe close.

The original date-range extract has 2,793 observations from 2015-01-02 through 2025-12-31, with no duplicate dates, invalid/missing closes or weekend dates. Its 77 absent weekdays are non-session dates. The raw file remains unchanged.

The modelling sample keeps only NYSE regular-session dates, including shortened sessions. A one-step target is the next date in this calendar. The source includes some observations without a regular US equity session; these are excluded by design, not declared erroneous. [Cboe's 4 July 2024 notice](https://cdn.cboe.com/resources/schedule_update/2024/Cboe-Holiday-Reminder-Modified-Trading-Hours-on-Wednesday-July-3-and-Thursday-July-4-2024.pdf), for example, distinguishes global options trading from regular sessions.

The frozen date list in `calendar/xnys_sessions_2015_2025.csv` comes from the XNYS calendar in [exchange_calendars](https://github.com/gerrymanoim/exchange_calendars); its version and hash are in `calendar/metadata.json`. This is a maintained calendar implementation, not an official exchange-issued data file. The preparation script verifies the snapshot hash and fails if any expected session lacks a VIX observation. Retained Cboe closes are unchanged; this filtering does not redefine the VIX close as the 4 p.m. equity close. Forecasts must be issued after the Cboe daily close becomes available.

Calendar checks cover exceptional closures on [5 December 2018](https://ir.nasdaq.com/news-releases/news-release-details/nasdaq-announces-closure-its-us-markets-honor-national-day) and [9 January 2025](https://www.nyse.com/publicdocs/nyse/markets/american-options/rule-interpretations/2025/National_Day_of_Mourning_20250102.pdf), the introduction of Juneteenth as an exchange holiday in 2022, and retained early closes. See also [NYSE holidays and hours](https://www.nyse.com/markets/hours-calendars).

To regenerate the frozen calendar (not needed for routine preparation):

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements-data.txt
./.venv/Scripts/python.exe scripts/build_calendar.py
./scripts/prepare_data.ps1
```
