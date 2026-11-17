# Payment Reconciliation & Discrepancy Detection Engine

An end-to-end payment reconciliation and discrepancy detection application built with Python and Streamlit. The system ingests platform transaction logs and bank settlement statements, performs high-precision `Decimal` financial arithmetic, accurately isolates duplicates, detects timing differences across month boundaries, identifies aggregate rounding drifts, and flags unauthorized/orphan refunds.

---

## 🌟 Key Features

1. **Deterministic Dataset Generation**:
   - Generates 126 platform transactions and 126 bank settlement records with realistic settlement lags (1–2 days).
   - Fixed random seed (`20261017`) for 100% reproducible testing.
   - Deliberately plants all four critical discrepancy types.

2. **Core Reconciliation Engine**:
   - **Timing Differences**: Correctly recognizes month-end transactions settling in the subsequent period (e.g., October 31 settling November 1) as timing differences rather than permanently missing settlements.
   - **Duplicate Handling**: Separates raw ledger totals from duplicate-adjusted totals. Multiple bank rows referencing the same platform ID are isolated and excluded from the net balance calculation.
   - **Aggregate Rounding Detection**: Identifies subtle sub-paise/sub-cent residuals that are individually beneath transaction tolerance (0.005) but accumulate beyond aggregate thresholds (0.01).
   - **Orphan / Unmatched Refunds**: Detects refunds referencing nonexistent original transaction IDs without falsely double-counting them as missing settlements.
   - **Arbitrary Precision**: Uses Python's native `Decimal` arithmetic for all monetary calculations, eliminating floating-point rounding errors.

3. **Streamlit Interactive Dashboard**:
   - Live KPI cards: Platform total (raw & adjusted), Bank total (raw & adjusted), Net Difference, Discrepancies, and Status.
   - Interactive Plotly visualizations: Raw vs. Duplicate-Adjusted ledger bar charts and discrepancy category distributions.
   - Discrepancy investigation table with dynamic categorization filters and exportable CSV reports.
   - Transaction-level reconciliation view with search capabilities.
   - Live CSV file uploaders for custom data evaluation and sample download buttons.

---

## 📂 Project Structure

```text
├── .gitignore                      # Git ignore rules
├── .streamlit/
│   └── config.toml                 # Streamlit UI configuration
├── data/
│   ├── platform_transactions.csv   # 126 synthetic platform transactions (Oct 2026)
│   └── bank_settlements.csv        # 126 synthetic bank settlements
├── docs/
│   ├── architecture.md             # System architecture & data flow
│   ├── assumptions.md              # Financial & dataset assumptions
│   ├── test_cases.md               # Detailed test case descriptions
│   └── production_limitations.txt  # Production limitations summary
├── outputs/
│   ├── summary.json                # JSON reconciliation summary
│   ├── discrepancy_report.csv      # Exported discrepancy log
│   └── transaction_reconciliation.csv # Detailed transaction-level report
├── src/
│   ├── __init__.py
│   ├── data_generator.py           # Synthetic dataset generator
│   ├── data_validator.py           # Input validation and Decimal casting
│   └── reconciliation.py           # Reconciliation and discrepancy classification engine
├── tests/
│   └── test_reconciliation.py      # Comprehensive pytest test suite (14 test cases)
├── app.py                          # Streamlit web application
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Production dependencies
└── PROJECT_STATUS.md               # Incremental phase-by-phase tracking
```

---

## 🚀 Local Installation & Execution

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Windows PowerShell, macOS terminal, or Linux bash

### Setup Steps
```powershell
# 1. Clone repository or navigate to project folder
cd D:\payment_reconciliation_complete

# 2. (Optional) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate synthetic datasets
python src/data_generator.py

# 5. Run the reconciliation engine and generate output reports
python src/reconciliation.py

# 6. Run the automated test suite
python -m pytest -v

# 7. Launch the Streamlit dashboard
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Streamlit Community Cloud Deployment Guide

To deploy the application live:

1. **Create a GitHub Repository**:
   - Go to [GitHub](https://github.com/new) and create a new repository (e.g., `payment-reconciliation-engine`).
2. **Push Local Code to GitHub**:
   ```powershell
   git remote add origin https://github.com/<YOUR-USERNAME>/payment-reconciliation-engine.git
   git branch -M main
   git push -u origin main
   ```
3. **Connect to Streamlit Community Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/) and click **Sign In** (with GitHub).
   - Click **Create App** > **Deploy a public app from GitHub**.
   - Select your repository: `<YOUR-USERNAME>/payment-reconciliation-engine`.
   - Set Branch to `main`.
   - Set Main file path to `app.py`.
   - Click **Deploy!**.
4. **Verification**:
   - Wait 1–2 minutes for container initialization and dependency installation.
   - Access the generated public URL (e.g. `https://<app-name>.streamlit.app`).

---

## 🧪 Test Suite Summary

Run all automated unit and integration tests with:
```powershell
python -m pytest -v
```
All 14 test cases cover:
- Detection of all 4 deliberately planted discrepancies
- Duplicate exclusion from duplicate-adjusted totals
- Timing differences distinction from missing settlements
- Unmatched refunds distinction from missing settlements
- Amount mismatch detection
- Missing bank settlement detection
- Unmatched bank record detection
- Duplicate platform entry detection
- Schema validation & invalid date/amount rejection
- Empty dataset handling
- Exact `Decimal` arithmetic integrity
