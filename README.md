# Payment Reconciliation & Discrepancy Detection

A Streamlit application that compares payment-platform transactions with bank settlements, classifies discrepancies, and exports investigation reports.

## Features
- Reproducible synthetic datasets (126 records per source)
- Duplicate-aware reconciliation and Decimal financial arithmetic
- Timing differences, aggregate rounding, unmatched refunds, missing settlements, amount mismatches, and unmatched bank entries
- Streamlit dashboard, CSV upload/download, search, and filters
- Pytest coverage

## Run locally (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/data_generator.py
python -m pytest -q
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and push this project.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Select the repository, branch, and `app.py` as the main file.
4. Deploy and wait for the build to finish.
5. Open the generated public URL and verify dashboard uploads and exports.

Deployment requires the owner's GitHub and Streamlit authentication; this repository does not claim a deployment has already occurred.

## Project structure
- `app.py`: Streamlit UI
- `src/data_generator.py`: deterministic synthetic data
- `src/data_validator.py`: schema and value validation
- `src/reconciliation.py`: reconciliation engine
- `tests/`: automated tests
- `docs/`: assumptions, architecture, and test case notes

## Important financial assumption
The rounding demonstration uses sub-paise synthetic residuals (INR 0.004 each) to demonstrate accumulation. It is a teaching example, not a claim that normal INR cash settlement occurs in fractions of a paise. See `docs/assumptions.md`.
