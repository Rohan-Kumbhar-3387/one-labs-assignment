# Test Cases & Verification Results

| # | Test Function Name | Tested Condition | Expected Result | Actual Result |
|---|---|---|---|---|
| 1 | `test_all_four_planted_discrepancies_detected` | Planted synthetic discrepancies in October 2026 dataset | Detected: Timing difference, Duplicate bank entry, Aggregate rounding difference, Unmatched refund | **PASSED** |
| 2 | `test_unmatched_refund_not_double_counted_as_missing_settlement` | Refund referencing nonexistent parent payment | Marked as "Unmatched refund", excluded from "Missing settlement" counts | **PASSED** |
| 3 | `test_duplicate_adjusted_bank_total_excludes_duplicate` | Duplicate bank entry for single platform transaction | `bank_total_raw` > `bank_total_duplicate_adjusted` | **PASSED** |
| 4 | `test_timing_difference_is_not_missing_settlement` | Payment on month-end (2026-10-31) settling in next month (2026-11-01) | Marked as "Timing difference", not missing settlement | **PASSED** |
| 5 | `test_invalid_platform_columns_raise_error` | Missing required columns in platform dataframe | Raises `DataValidationError` | **PASSED** |
| 6 | `test_invalid_bank_columns_raise_error` | Missing required columns in bank dataframe | Raises `DataValidationError` | **PASSED** |
| 7 | `test_invalid_date_format_raises_error` | Unparseable / corrupted transaction date string | Raises `DataValidationError` | **PASSED** |
| 8 | `test_invalid_amount_raises_error` | Non-decimal currency amount (e.g. "$100.00") | Raises `DataValidationError` | **PASSED** |
| 9 | `test_empty_both_datasets_reconcile_cleanly` | Empty platform and bank datasets | Status "RECONCILED", 0 discrepancies | **PASSED** |
| 10 | `test_missing_settlement_is_detected` | Platform transaction without any bank settlement | Classified as "Missing settlement" with platform amount | **PASSED** |
| 11 | `test_unmatched_bank_entry_is_detected` | Bank settlement with no matching platform transaction | Classified as "Unmatched bank entry" with bank amount | **PASSED** |
| 12 | `test_amount_mismatch_detected` | Bank amount differing from platform amount beyond tolerance | Classified as "Amount mismatch" | **PASSED** |
| 13 | `test_duplicate_platform_entry_detected` | Platform file containing duplicate transaction ID | Classified as "Duplicate platform entry" | **PASSED** |
| 14 | `test_decimal_financial_precision` | High-precision arithmetic calculation across all ledgers | Exact `Decimal` arithmetic verified with zero float drift | **PASSED** |

Execution Summary:
- **14 passed, 0 failed, 0 warnings** in 1.11s.
