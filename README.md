# One-day-ahead VIX forecasting

An independent research project comparing ARIMA, Random Forest and a naive benchmark for one-day-ahead forecasting of VIX closing levels, using historical observations from 2015–2025.

## Current status

Data downloaded from Cboe and reconciled on 13 October 2026: 2,766 observations, 2015-01-02 to 2025-12-31, matching the frozen NYSE (XNYS) regular-session calendar. All expected sessions are present, including early closes. The original extract contains 2,793 rows; 27 non-session dates were excluded from modelling and logged. Exploratory analysis of the training period (2015–2021) is complete. No models have been fitted and no forecast performance claims are available.

- [Data documentation and reproduction instructions](data/README.md)
- [Machine-readable data audit](data/data_audit.json)
- [Exploratory analysis notebook](notebooks/01_exploratory_analysis.ipynb)
- [Research proposal draft](report/report_draft.md)
- [Opening presentation notes](presentation/speaker_notes.md)

The report and presentation notes describe the research design, completed data preparation and exploratory findings. Modelling and forecast evaluation remain in progress.

## Reproduce data preparation

In PowerShell, from the project root:

```powershell
./scripts/prepare_data.ps1 -Download
```

This downloads the official CSV, preserves it locally, extracts the requested date range, filters to the checked-in calendar and writes audit files. Routine preparation needs no additional packages. Regenerating the calendar uses Python and `requirements-data.txt`; instructions are in the data documentation. Raw and processed CSVs are excluded from Git; the calendar, exclusion log and audit metadata are included.

## Reproduce the exploratory analysis

After preparing the data, from the project root:

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements-analysis.txt
./.venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute --inplace notebooks/01_exploratory_analysis.ipynb
```

This re-runs the notebook and rewrites the figures in `report/figures/`. All statistics and diagnostics use the training period only; the full series is plotted once for context.

Fixing the evaluation protocol and fitting the models are the next implementation stage.
