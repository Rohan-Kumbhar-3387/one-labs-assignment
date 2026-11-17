from pathlib import Path
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.reconciliation import reconcile
from src.data_generator import generate_datasets

st.set_page_config(page_title="Payment Reconciliation", page_icon="💳", layout="wide")
st.title("💳 Payment Reconciliation & Discrepancy Detection")
st.caption("Compare platform transactions with bank settlements and investigate financial gaps.")

with st.sidebar:
    st.header("Reconciliation settings")
    report_month = st.text_input("Reporting month (YYYY-MM)", "2026-10")
    st.caption("Default sample period: October 2026")
    if st.button("Regenerate sample data", use_container_width=True):
        generate_datasets()
        st.success("Sample data regenerated.")

c1, c2 = st.columns(2)
with c1:
    p_file = st.file_uploader("Platform transactions CSV", type="csv", key="platform")
with c2:
    b_file = st.file_uploader("Bank settlements CSV", type="csv", key="bank")

if p_file and b_file:
    try:
        platform = pd.read_csv(p_file, dtype=str, keep_default_na=False)
        bank = pd.read_csv(b_file, dtype=str, keep_default_na=False)
    except Exception as exc:
        st.error(f"Could not read uploaded CSV: {exc}")
        st.stop()
else:
    platform_path = ROOT / "data" / "platform_transactions.csv"
    bank_path = ROOT / "data" / "bank_settlements.csv"
    if not platform_path.exists() or not bank_path.exists():
        st.warning("Sample data not found. Generate it using the sidebar button.")
        st.stop()
    platform = pd.read_csv(platform_path, dtype=str, keep_default_na=False)
    bank = pd.read_csv(bank_path, dtype=str, keep_default_na=False)
    st.info("Showing generated sample datasets. Upload both CSV files to analyze your own data.")

try:
    result = reconcile(platform, bank, report_month=report_month)
except Exception as exc:
    st.error(f"Reconciliation could not be completed: {exc}")
    st.stop()

s = result["summary"]
cols = st.columns(4)
metrics = [
    ("Platform total (adjusted)", f"₹{float(s['platform_total_duplicate_adjusted']):,.2f}"),
    ("Bank total (adjusted)", f"₹{float(s['bank_total_duplicate_adjusted']):,.2f}"),
    ("Net difference", f"₹{float(s['adjusted_net_difference']):,.2f}"),
    ("Discrepancies", str(s["discrepancy_count"])),
]
for col, (label, value) in zip(cols, metrics):
    col.metric(label, value)

st.subheader(f"Reconciliation status: {s['reconciliation_status']}")
a, b, c = st.columns(3)
a.metric("Matched transactions", s["matched_transaction_count"])
b.metric("Platform records", s["platform_record_count_raw"])
c.metric("Bank records", s["bank_record_count_raw"])

left, right = st.columns(2)
with left:
    st.subheader("Raw vs duplicate-adjusted totals")
    totals = pd.DataFrame({"Ledger": ["Platform raw", "Platform adjusted", "Bank raw", "Bank adjusted"],
                           "Amount": [float(s["platform_total_raw"]), float(s["platform_total_duplicate_adjusted"]), float(s["bank_total_raw"]), float(s["bank_total_duplicate_adjusted"])]})
    st.plotly_chart(px.bar(totals, x="Ledger", y="Amount", title="Financial totals"), use_container_width=True)
with right:
    st.subheader("Discrepancy categories")
    disc = result["discrepancies"]
    if not disc.empty:
        counts = disc.category.value_counts().rename_axis("Category").reset_index(name="Count")
        st.plotly_chart(px.pie(counts, names="Category", values="Count", title="Discrepancy distribution"), use_container_width=True)
    else:
        st.success("No discrepancies found.")

st.subheader("Discrepancy investigation")
if not result["discrepancies"].empty:
    categories = ["All"] + sorted(result["discrepancies"].category.unique().tolist())
    selected = st.selectbox("Filter discrepancy type", categories)
    view = result["discrepancies"] if selected == "All" else result["discrepancies"][result["discrepancies"].category == selected]
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button("Download discrepancy report", view.to_csv(index=False).encode("utf-8"), "discrepancy_report.csv", "text/csv")
else:
    st.success("No discrepancies to investigate.")

st.subheader("Transaction-level reconciliation")
transaction_view = result["transactions"]
search = st.text_input("Search transaction ID")
if search:
    transaction_view = transaction_view[transaction_view.transaction_id.str.contains(search, case=False, na=False)]
st.dataframe(transaction_view, use_container_width=True, hide_index=True)
st.download_button("Download full reconciliation", result["transactions"].to_csv(index=False).encode("utf-8"), "transaction_reconciliation.csv", "text/csv")

st.subheader("Download sample datasets")
d1, d2 = st.columns(2)
d1.download_button("Platform sample CSV", platform.to_csv(index=False).encode("utf-8"), "platform_transactions.csv", "text/csv")
d2.download_button("Bank sample CSV", bank.to_csv(index=False).encode("utf-8"), "bank_settlements.csv", "text/csv")

with st.expander("Financial assumptions"):
    st.markdown((ROOT / "docs" / "assumptions.md").read_text(encoding="utf-8"))
