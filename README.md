# One-day-ahead VIX forecasting

An independent research project comparing ARIMA, Random Forest and a naive benchmark for one-day-ahead forecasting of VIX closing levels, using historical observations from 2015–2025.

## Current status

Data downloaded from Cboe and reconciled on 13 October 2026: 2,766 observations, 2015-01-02 to 2025-12-31, matching the frozen NYSE (XNYS) regular-session calendar. All expected sessions are present, including early closes. The original extract contains 2,793 rows; 27 non-session dates were excluded from modelling and logged. No models have been fitted and no forecast performance claims are available.

- [Data documentation and reproduction instructions](data/README.md)
- [Machine-readable data audit](data/data_audit.json)
- [Research proposal draft](report/report_draft.md)
- [Opening presentation notes](presentation/speaker_notes.md)

The report and presentation notes describe the research design and completed data preparation. Modelling and forecast evaluation remain in progress.

## Reproduce data preparation

In PowerShell, from the project root:

```powershell
./scripts/prepare_data.ps1 -Download
```

This downloads the official CSV, preserves it locally, extracts the requested date range, filters to the checked-in calendar and writes audit files. Routine preparation needs no additional packages. Regenerating the calendar uses Python and `requirements-data.txt`; instructions are in the data documentation. Raw and processed CSVs are excluded from Git; the calendar, exclusion log and audit metadata are included.

Python analysis and the research notebook are the next implementation stage.
