"""Input validation and normalization for reconciliation datasets."""
from decimal import Decimal, InvalidOperation
import pandas as pd

PLATFORM_REQUIRED = {
    "transaction_id", "transaction_date", "customer_id", "transaction_type",
    "original_transaction_id", "amount", "currency", "status"
}
BANK_REQUIRED = {
    "settlement_id", "transaction_id", "settlement_date",
    "settlement_amount", "currency", "bank_reference"
}

class DataValidationError(ValueError):
    """Raised when an uploaded or generated dataset is structurally invalid."""

def _require_columns(df, required, label):
    missing = sorted(required - set(df.columns))
    if missing:
        raise DataValidationError(f"{label} dataset is missing required columns: {', '.join(missing)}")

def _clean_id(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

def _decimal(value, row_label, column):
    try:
        if pd.isna(value) or str(value).strip() == "":
            raise InvalidOperation
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise DataValidationError(f"Invalid amount in {row_label}, column '{column}': {value!r}")

def validate_platform(df):
    _require_columns(df, PLATFORM_REQUIRED, "Platform")
    out = df.copy()
    out["transaction_id"] = out["transaction_id"].map(_clean_id)
    out["original_transaction_id"] = out["original_transaction_id"].map(_clean_id)
    if (out["transaction_id"] == "").any():
        raise DataValidationError("Platform transaction_id cannot be blank.")
    out["transaction_date"] = pd.to_datetime(out["transaction_date"], errors="coerce", format="ISO8601")
    if out["transaction_date"].isna().any():
        raise DataValidationError("Platform contains an invalid transaction_date.")
    out["amount_decimal"] = [
        _decimal(v, f"platform row {i}", "amount") for i, v in enumerate(out["amount"], start=2)
    ]
    out["currency"] = out["currency"].astype(str).str.strip().str.upper()
    out["transaction_type"] = out["transaction_type"].astype(str).str.strip().str.upper()
    invalid_types = sorted(set(out["transaction_type"]) - {"PAYMENT", "REFUND"})
    if invalid_types:
        raise DataValidationError(f"Unsupported transaction_type values: {invalid_types}")
    if (out["currency"] == "").any():
        raise DataValidationError("Platform currency cannot be blank.")
    return out

def validate_bank(df):
    _require_columns(df, BANK_REQUIRED, "Bank")
    out = df.copy()
    for col in ("settlement_id", "transaction_id"):
        out[col] = out[col].map(_clean_id)
        if (out[col] == "").any():
            raise DataValidationError(f"Bank {col} cannot be blank.")
    out["settlement_date"] = pd.to_datetime(out["settlement_date"], errors="coerce", format="ISO8601")
    if out["settlement_date"].isna().any():
        raise DataValidationError("Bank contains an invalid settlement_date.")
    out["settlement_amount_decimal"] = [
        _decimal(v, f"bank row {i}", "settlement_amount") for i, v in enumerate(out["settlement_amount"], start=2)
    ]
    out["currency"] = out["currency"].astype(str).str.strip().str.upper()
    if (out["currency"] == "").any():
        raise DataValidationError("Bank currency cannot be blank.")
    if out["settlement_id"].duplicated().any():
        raise DataValidationError("Bank settlement_id values must be unique.")
    return out
