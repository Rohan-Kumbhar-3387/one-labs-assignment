"""Deterministic reconciliation engine for platform and bank CSV data."""
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path
import pandas as pd
try:
    from .data_validator import validate_platform, validate_bank
except ImportError:
    from data_validator import validate_platform, validate_bank

ZERO = Decimal("0")


def reconcile(platform_df, bank_df, report_month="2026-10",
              transaction_tolerance=Decimal("0.005"),
              aggregate_rounding_threshold=Decimal("0.01")):
    p = validate_platform(platform_df)
    b = validate_bank(bank_df)
    period = pd.Period(report_month, freq="M")
    start, end = period.start_time.normalize(), period.end_time.normalize()
    issues, detail = [], []

    p_counts = Counter(p.transaction_id)
    for tx_id, count in p_counts.items():
        if count > 1:
            issues.append(_issue(tx_id, "", "Duplicate platform entry", explanation=f"Platform transaction ID appears {count} times.", action="Verify the source and retain one canonical transaction."))
    p_unique = p.drop_duplicates("transaction_id", keep="first")
    b_counts = Counter(b.transaction_id)
    for tx_id, count in b_counts.items():
        if count > 1:
            duplicates = b[b.transaction_id == tx_id].iloc[1:]
            for _, dup in duplicates.iterrows():
                issues.append(_issue(tx_id, dup.settlement_id, "Duplicate bank entry", bank_amount=str(dup.settlement_amount_decimal), event_date=dup.settlement_date.date().isoformat(), explanation=f"Multiple bank rows reference {tx_id}; duplicate settlement {dup.settlement_id} is excluded from adjusted totals.", action="Verify the bank statement and exclude duplicate settlement rows."))
    b_unique = b.drop_duplicates("transaction_id", keep="first")
    p_map = {r.transaction_id: r for _, r in p_unique.iterrows()}
    b_map = {r.transaction_id: r for _, r in b_unique.iterrows()}

    invalid_refunds = set()
    for _, r in p_unique.iterrows():
        if r.transaction_type == "REFUND":
            oid = r.original_transaction_id
            if not oid or oid not in p_map or p_map[oid].transaction_type != "PAYMENT":
                invalid_refunds.add(r.transaction_id)
                issues.append(_issue(r.transaction_id, "", "Unmatched refund", platform_amount=str(r.amount_decimal), difference=str(r.amount_decimal), event_date=r.transaction_date.date().isoformat(), explanation=f"Refund references missing or invalid original payment '{oid or 'blank'}'.", action="Investigate the refund authorization and locate its original payment."))

    residuals = []
    for _, pr in p_unique.iterrows():
        txid, amount = pr.transaction_id, pr.amount_decimal
        br = b_map.get(txid)
        row = {"transaction_id": txid, "transaction_type": pr.transaction_type,
               "transaction_date": pr.transaction_date.date().isoformat(),
               "platform_amount": str(amount), "bank_amount": "", "difference": "",
               "currency": pr.currency, "status": ""}
        if not (start <= pr.transaction_date <= end):
            row["status"] = "Outside reporting period"
        elif br is None:
            if txid in invalid_refunds:
                row["status"] = "Unmatched refund"
            else:
                row["status"] = "Missing settlement"
                issues.append(_issue(txid, "", "Missing settlement", platform_amount=str(amount), difference=str(amount), event_date=pr.transaction_date.date().isoformat(), explanation="No bank settlement was found for this reporting-period transaction.", action="Check bank settlement files and settlement processing status."))
        else:
            bank_amount = br.settlement_amount_decimal
            diff = amount - bank_amount
            row.update(bank_amount=str(bank_amount), difference=str(diff))
            if br.settlement_date > end:
                row["status"] = "Timing difference"
                issues.append(_issue(txid, br.settlement_id, "Timing difference", str(amount), str(bank_amount), str(diff), br.settlement_date.date().isoformat(), "The platform transaction belongs to the reporting month, but the bank settlement is dated after month-end.", "Carry this item into the next reporting period; do not classify it as permanently missing."))
            elif abs(diff) <= transaction_tolerance:
                row["status"] = "Matched" if diff == ZERO else "Rounding candidate"
                if diff != ZERO:
                    residuals.append((txid, pr.currency, diff, amount, bank_amount))
            else:
                row["status"] = "Amount mismatch"
                issues.append(_issue(txid, br.settlement_id, "Amount mismatch", str(amount), str(bank_amount), str(diff), br.settlement_date.date().isoformat(), "Platform and bank amounts differ beyond transaction tolerance.", "Investigate fees, partial settlement, adjustments, or data-entry errors."))
        detail.append(row)

    for currency in sorted({x[1] for x in residuals}):
        group = [x for x in residuals if x[1] == currency]
        net = sum((x[2] for x in group), ZERO)
        if abs(net) >= aggregate_rounding_threshold:
            ids = ", ".join(x[0] for x in group)
            for row in detail:
                if row["transaction_id"] in {x[0] for x in group}:
                    row["status"] = "Aggregate rounding difference"
            issues.append(_issue(ids, "", "Aggregate rounding difference", str(sum((x[3] for x in group), ZERO)), str(sum((x[4] for x in group), ZERO)), str(net), report_month, f"{len(group)} residuals are individually within {transaction_tolerance}, but their aggregate {net} {currency} reaches threshold {aggregate_rounding_threshold}.", "Review aggregate rounding, allocation, and currency-conversion procedures."))
        else:
            for txid, _, diff, pa, ba in group:
                issues.append(_issue(txid, "", "Rounding difference within aggregate threshold", str(pa), str(ba), str(diff), report_month, "Residual is within transaction tolerance and aggregate threshold.", "Monitor the residual."))

    for _, br in b_unique.iterrows():
        if br.transaction_id not in p_map:
            issues.append(_issue(br.transaction_id, br.settlement_id, "Unmatched bank entry", bank_amount=str(br.settlement_amount_decimal), difference=str(-br.settlement_amount_decimal), event_date=br.settlement_date.date().isoformat(), explanation="Bank settlement has no corresponding platform transaction.", action="Locate the originating platform transaction or investigate an unexpected bank entry."))

    p_period = p[(p.transaction_date >= start) & (p.transaction_date <= end)]
    b_period = b[(b.settlement_date >= start) & (b.settlement_date <= end)]
    pu_period = p_unique[(p_unique.transaction_date >= start) & (p_unique.transaction_date <= end)]
    bu_period = b_unique[(b_unique.settlement_date >= start) & (b_unique.settlement_date <= end)]
    p_raw = sum(p_period.amount_decimal, ZERO)
    b_raw = sum(b_period.settlement_amount_decimal, ZERO)
    p_adj = sum(pu_period.amount_decimal, ZERO)
    b_adj = sum(bu_period.settlement_amount_decimal, ZERO)
    detail_df = pd.DataFrame(detail)
    issue_df = pd.DataFrame(issues, columns=["transaction_id", "settlement_id", "category", "platform_amount", "bank_amount", "difference", "event_date", "explanation", "recommended_action"])
    matched = int((detail_df.status == "Matched").sum()) if not detail_df.empty else 0
    summary = {
        "report_month": report_month, "platform_record_count_raw": len(p_period), "bank_record_count_raw": len(b_period),
        "platform_total_raw": str(p_raw), "bank_total_raw": str(b_raw),
        "platform_total_duplicate_adjusted": str(p_adj), "bank_total_duplicate_adjusted": str(b_adj),
        "adjusted_net_difference": str(p_adj - b_adj), "matched_transaction_count": matched,
        "transaction_count_in_period": len(pu_period), "discrepancy_count": len(issue_df),
        "reconciliation_status": "REVIEW REQUIRED" if len(issue_df) else "RECONCILED"
    }
    return {"summary": summary, "transactions": detail_df, "discrepancies": issue_df}


def _issue(txid, settlement_id, category, platform_amount="", bank_amount="", difference="", event_date="", explanation="", action=""):
    return {"transaction_id": txid, "settlement_id": settlement_id, "category": category,
            "platform_amount": platform_amount, "bank_amount": bank_amount, "difference": difference,
            "event_date": event_date, "explanation": explanation, "recommended_action": action}


def run_and_save(platform_csv=None, bank_csv=None, output_dir=None, report_month="2026-10"):
    root = Path(__file__).resolve().parents[1]
    platform_csv = Path(platform_csv) if platform_csv else root / "data" / "platform_transactions.csv"
    bank_csv = Path(bank_csv) if bank_csv else root / "data" / "bank_settlements.csv"
    output_dir = Path(output_dir) if output_dir else root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    p = pd.read_csv(platform_csv, dtype=str, keep_default_na=False)
    b = pd.read_csv(bank_csv, dtype=str, keep_default_na=False)

    result = reconcile(p, b, report_month=report_month)

    with (output_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(result["summary"], f, indent=2)

    result["transactions"].to_csv(output_dir / "transaction_reconciliation.csv", index=False)
    result["discrepancies"].to_csv(output_dir / "discrepancy_report.csv", index=False)
    return result


if __name__ == "__main__":
    res = run_and_save()
    print("Reconciliation complete.")
    print(f"Status: {res['summary']['reconciliation_status']}")
    print(f"Discrepancies found: {res['summary']['discrepancy_count']}")
    print(f"Raw Platform Total: {res['summary']['platform_total_raw']}")
    print(f"Raw Bank Total: {res['summary']['bank_total_raw']}")
    print(f"Duplicate-Adjusted Platform: {res['summary']['platform_total_duplicate_adjusted']}")
    print(f"Duplicate-Adjusted Bank: {res['summary']['bank_total_duplicate_adjusted']}")
    print(f"Adjusted Net Difference: {res['summary']['adjusted_net_difference']}")
