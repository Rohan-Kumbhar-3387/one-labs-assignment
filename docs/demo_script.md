# 2–3 Minute Demo Video Recording Script

**Title**: Payment Reconciliation & Discrepancy Detection Engine Demo  
**Duration**: Approx. 2 minutes 30 seconds  
**Speaker**: Presenter / Engineer  

---

### Segment 1: Introduction & Overview (0:00 – 0:35)
- **Visual**: Terminal showing project structure, then browser opening `http://localhost:8501`.
- **Narration**:
  > "Hello everyone. Today I'm demonstrating the Payment Reconciliation and Discrepancy Detection Engine. In real-world fintech systems, payment platform records and bank settlements frequently drift due to timing differences across month boundaries, duplicate processing, orphan refunds, and rounding anomalies. This application uses high-precision Python `Decimal` arithmetic and an intuitive Streamlit interface to automatically ingest both ledgers, detect all financial discrepancies, and provide actionable resolution guidance."

---

### Segment 2: Financial Summary & KPI Cards (0:35 – 1:10)
- **Visual**: Top of dashboard showing KPI cards: Platform total, Bank total, Net difference, Discrepancies, and Status badge.
- **Narration**:
  > "Looking at the dashboard for October 2026, we see 126 platform records and 126 bank settlement records. The engine displays both raw totals and duplicate-adjusted totals. Notice the Status badge is marked 'REVIEW REQUIRED' because our engine detected 4 discrepancies. Below the metrics, interactive Plotly charts compare our raw vs. duplicate-adjusted ledger amounts and display the breakdown of discrepancy types."

---

### Segment 3: Deep Dive into the 4 Discrepancy Types (1:10 – 1:55)
- **Visual**: Discrepancy investigation table, filtering by category dropdown.
- **Narration**:
  > "Let's explore the Discrepancy Investigation section. The engine identified four distinct discrepancy categories:
  > 1. **Duplicate Bank Entry**: Transaction `PAY-0060` has a duplicate settlement row `SET-DUPLICATE-001`. The engine flags the duplicate and excludes it from the adjusted bank balance to prevent distorted cash positions.
  > 2. **Unmatched Refund**: `REF-UNMATCHED-001` references a nonexistent original payment. Crucially, the engine flags it as an orphan refund without falsely double-counting it as a missing settlement.
  > 3. **Timing Difference**: `PAY-0120` occurred on October 31 but settled on November 1. The engine recognizes this month-boundary settlement lag as a timing difference to roll over into November, rather than a permanent loss.
  > 4. **Aggregate Rounding Difference**: Five micro-transactions each have sub-paise residuals of 0.004 INR. While individually within tolerance, together they accumulate to 0.020 INR, crossing our aggregate threshold."

---

### Segment 4: Search, Exports & Verification (1:55 – 2:30)
- **Visual**: Searching transaction ID `PAY-0120` in the transaction table, clicking 'Download discrepancy report' and 'Download full reconciliation', then terminal showing `pytest` passing 14/14 tests.
- **Narration**:
  > "Users can search any individual transaction in the reconciliation table to inspect its platform vs bank amount and status, or export the reports as CSVs for auditing. In the terminal, our automated pytest suite tests all 14 scenarios—including edge cases, schema violations, and decimal precision—passing 100%. Thank you for watching!"
