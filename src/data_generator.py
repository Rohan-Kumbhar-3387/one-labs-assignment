"""Generate deterministic synthetic payment and bank settlement datasets."""
from pathlib import Path
from decimal import Decimal
import csv
import random
from datetime import date, timedelta

SEED = 20261017
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def generate_datasets(output_dir=DATA_DIR):
    rng = random.Random(SEED)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    platform, bank = [], []
    start = date(2026, 10, 1)
    rounding_ids = {f"PAY-{i:04d}" for i in range(1, 6)}

    for i in range(1, 121):
        tx_id = f"PAY-{i:04d}"
        if tx_id == "PAY-0120":
            tx_date = date(2026, 10, 31)
            settlement_date = date(2026, 11, 1)
        else:
            tx_date = start + timedelta(days=rng.randrange(28))
            settlement_date = tx_date + timedelta(days=rng.choice([1, 2]))

        amount = (Decimal(rng.randrange(500, 50001)) / Decimal("100")).quantize(Decimal("0.01"))
        if tx_id in rounding_ids:
            amount = Decimal("100.004")
        platform.append({
            "transaction_id": tx_id, "transaction_date": tx_date.isoformat(),
            "customer_id": f"CUST-{rng.randrange(1, 46):03d}",
            "transaction_type": "PAYMENT", "original_transaction_id": "",
            "amount": format(amount, "f"), "currency": "INR", "status": "SUCCESS"
        })
        bank_amount = Decimal("100.000") if tx_id in rounding_ids else amount
        bank.append({
            "settlement_id": f"SET-{i:04d}", "transaction_id": tx_id,
            "settlement_date": settlement_date.isoformat(),
            "settlement_amount": format(bank_amount, "f"), "currency": "INR",
            "bank_reference": f"BNK-{rng.randrange(100000, 999999)}"
        })

    for j, original_id in enumerate(["PAY-0010", "PAY-0020", "PAY-0030", "PAY-0040", "PAY-0050"], start=1):
        original = next(x for x in platform if x["transaction_id"] == original_id)
        refund_amount = (Decimal(original["amount"]) * Decimal("0.10")).quantize(Decimal("0.01"))
        refund_date = date(2026, 10, 20) + timedelta(days=j)
        refund_id = f"REF-{j:03d}"
        platform.append({
            "transaction_id": refund_id, "transaction_date": refund_date.isoformat(),
            "customer_id": original["customer_id"], "transaction_type": "REFUND",
            "original_transaction_id": original_id, "amount": format(-refund_amount, "f"),
            "currency": "INR", "status": "SUCCESS"
        })
        bank.append({
            "settlement_id": f"SET-REF-{j:03d}", "transaction_id": refund_id,
            "settlement_date": (refund_date + timedelta(days=1)).isoformat(),
            "settlement_amount": format(-refund_amount, "f"), "currency": "INR",
            "bank_reference": f"BNK-REF-{rng.randrange(100000, 999999)}"
        })

    platform.append({
        "transaction_id": "REF-UNMATCHED-001", "transaction_date": "2026-10-28",
        "customer_id": "CUST-999", "transaction_type": "REFUND",
        "original_transaction_id": "PAY-DOES-NOT-EXIST", "amount": "-750.00",
        "currency": "INR", "status": "SUCCESS"
    })
    duplicate = dict(next(x for x in bank if x["transaction_id"] == "PAY-0060"))
    duplicate["settlement_id"] = "SET-DUPLICATE-001"
    duplicate["bank_reference"] = "BNK-DUPLICATE-001"
    bank.append(duplicate)

    platform_fields = ["transaction_id", "transaction_date", "customer_id", "transaction_type",
                       "original_transaction_id", "amount", "currency", "status"]
    bank_fields = ["settlement_id", "transaction_id", "settlement_date",
                   "settlement_amount", "currency", "bank_reference"]
    for filename, rows, fields in [
        ("platform_transactions.csv", platform, platform_fields),
        ("bank_settlements.csv", bank, bank_fields)
    ]:
        with (output_dir / filename).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    return platform, bank

if __name__ == "__main__":
    p, b = generate_datasets()
    print(f"Generated {len(p)} platform records and {len(b)} bank settlement records.")
