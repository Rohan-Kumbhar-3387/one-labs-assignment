from pathlib import Path
import sys
from decimal import Decimal
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.reconciliation import reconcile
from src.data_validator import validate_platform, validate_bank, DataValidationError

DATA = ROOT / "data"

def load_data():
    p = pd.read_csv(DATA / "platform_transactions.csv", dtype=str, keep_default_na=False)
    b = pd.read_csv(DATA / "bank_settlements.csv", dtype=str, keep_default_na=False)
    return p, b

def test_all_four_planted_discrepancies_detected():
    p, b = load_data()
    result = reconcile(p, b)
    categories = set(result["discrepancies"]["category"])
    assert {"Timing difference", "Duplicate bank entry", "Aggregate rounding difference", "Unmatched refund"} <= categories

def test_unmatched_refund_not_double_counted_as_missing_settlement():
    p, b = load_data()
    result = reconcile(p, b)
    issues = result["discrepancies"]
    assert not ((issues.transaction_id == "REF-UNMATCHED-001") & (issues.category == "Missing settlement")).any()

def test_duplicate_adjusted_bank_total_excludes_duplicate():
    p, b = load_data()
    result = reconcile(p, b)
    s = result["summary"]
    assert Decimal(s["bank_total_raw"]) > Decimal(s["bank_total_duplicate_adjusted"])

def test_timing_difference_is_not_missing_settlement():
    p, b = load_data()
    result = reconcile(p, b)
    row = result["transactions"].set_index("transaction_id").loc["PAY-0120"]
    assert row.status == "Timing difference"

def test_invalid_platform_columns_raise_error():
    with pytest.raises(DataValidationError):
        validate_platform(pd.DataFrame({"transaction_id": ["x"]}))

def test_invalid_bank_columns_raise_error():
    with pytest.raises(DataValidationError):
        validate_bank(pd.DataFrame({"transaction_id": ["x"]}))

def test_invalid_date_format_raises_error():
    p, _ = load_data()
    p.loc[0, "transaction_date"] = "invalid-date"
    with pytest.raises(DataValidationError, match="invalid transaction_date"):
        validate_platform(p)

def test_invalid_amount_raises_error():
    p, _ = load_data()
    p.loc[0, "amount"] = "$100.00"
    with pytest.raises(DataValidationError, match="Invalid amount"):
        validate_platform(p)

def test_empty_both_datasets_reconcile_cleanly():
    p, b = load_data()
    p = p.iloc[0:0]
    b = b.iloc[0:0]
    result = reconcile(p, b)
    assert result["summary"]["reconciliation_status"] == "RECONCILED"
    assert result["summary"]["discrepancy_count"] == 0

def test_missing_settlement_is_detected():
    p, b = load_data()
    b = b[b.transaction_id != "PAY-0008"]
    result = reconcile(p, b)
    assert ((result["discrepancies"].transaction_id == "PAY-0008") & (result["discrepancies"].category == "Missing settlement")).any()

def test_unmatched_bank_entry_is_detected():
    p, b = load_data()
    extra = b.iloc[[0]].copy()
    extra["transaction_id"] = "BANK-ONLY-999"
    extra["settlement_id"] = "SET-BANK-ONLY-999"
    b = pd.concat([b, extra], ignore_index=True)
    result = reconcile(p, b)
    assert ((result["discrepancies"].transaction_id == "BANK-ONLY-999") & (result["discrepancies"].category == "Unmatched bank entry")).any()

def test_amount_mismatch_detected():
    p, b = load_data()
    b_idx = b[b.transaction_id == "PAY-0007"].index[0]
    b.loc[b_idx, "settlement_amount"] = "99999.00"
    result = reconcile(p, b)
    assert ((result["discrepancies"].transaction_id == "PAY-0007") & (result["discrepancies"].category == "Amount mismatch")).any()

def test_duplicate_platform_entry_detected():
    p, b = load_data()
    dup = p[p.transaction_id == "PAY-0009"].copy()
    p = pd.concat([p, dup], ignore_index=True)
    result = reconcile(p, b)
    assert ((result["discrepancies"].transaction_id == "PAY-0009") & (result["discrepancies"].category == "Duplicate platform entry")).any()

def test_decimal_financial_precision():
    p, b = load_data()
    result = reconcile(p, b)
    s = result["summary"]
    # Verify exact decimal representation
    adj_diff = Decimal(s["adjusted_net_difference"])
    expected_diff = Decimal(s["platform_total_duplicate_adjusted"]) - Decimal(s["bank_total_duplicate_adjusted"])
    assert adj_diff == expected_diff
