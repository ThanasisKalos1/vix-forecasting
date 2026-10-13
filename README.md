# One-day-ahead VIX forecasting

An independent research project comparing ARIMA, Random Forest and a naive benchmark for one-day-ahead forecasting of VIX closing levels, using historical observations from 2015–2025.

## Current status

Data downloaded from Cboe and reconciled on 13 October 2026: 2,766 observations, 2015-01-02 to 2025-12-31, matching the frozen NYSE (XNYS) regular-session calendar. All expected sessions are present, including early closes. The original extract contains 2,793 rows; 27 non-session dates were excluded from modelling and logged. Exploratory analysis of the training period (2015–2021) is complete, and the evaluation protocol (models, candidate settings, selection rule and statistical tests) was fixed on the same date, before any model was fitted. Models have been selected on the validation period (2022–2023): ARIMA(1,0,0) and a Random Forest that predicts the next change. On that period all four forecasts are within 0.6% of one another in RMSE. The test period (2024–2025) has not been evaluated, so no out-of-sample performance claims are available.

- [Data documentation and reproduction instructions](data/README.md)
- [Machine-readable data audit](data/data_audit.json)
- [Exploratory analysis notebook](notebooks/01_exploratory_analysis.ipynb)
- [Model selection notebook](notebooks/02_model_selection.ipynb), with the [selected configurations](results/selected_models.json) and [validation errors of every candidate](results/validation_candidates.csv)
- [Research report draft](report/report_draft.md), including the [evaluation protocol](report/report_draft.md#4-methodology-and-evaluation-protocol)
- [Opening presentation notes](presentation/speaker_notes.md)

The report describes the research design, data preparation, exploratory findings and model selection. The test evaluation remains to be run.

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

## Reproduce the model selection

The forecasting code is in the `vixforecast` package: `features.py` builds inputs from past closes, `models.py` defines the naive, ARIMA, HAR and Random Forest forecasters, and `evaluation.py` runs the walk-forward loop. To run the tests and repeat the selection:

```powershell
./.venv/Scripts/python.exe -m pytest
./.venv/Scripts/python.exe -m jupyter nbconvert --to notebook --execute --inplace notebooks/02_model_selection.ipynb
```

The tests use a synthetic series and need no data files. The notebook takes roughly 15 minutes, uses data up to the end of 2023 only, and rewrites the files in `results/`.

Evaluating the selected models once on the test period is the next implementation stage.
