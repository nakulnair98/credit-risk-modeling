import streamlit as st
from utils import load_csv

st.set_page_config(page_title="Portfolio", layout="wide")
st.title("Portfolio: ECL by stage and grade")

by_stage = load_csv("ecl_by_stage.csv", index_col=0)
by_grade = load_csv("ecl_by_grade.csv", index_col=0)
pricing = load_csv("pricing_by_grade.csv", index_col=0)

# --- Stage table ---
st.subheader("ECL by stage")
stage_view = by_stage[["loans", "ead_mn", "ecl_mn", "coverage_%"]].rename(columns={
    "loans": "Loans", "ead_mn": "EAD ($mn)", "ecl_mn": "ECL ($mn)", "coverage_%": "Coverage (%)"})
st.dataframe(stage_view, use_container_width=True)

st.caption("Stage 1: 12-month ECL · Stage 2: lifetime ECL (1–30 DPD, or FICO down 60+ pts and now below 640) · Stage 3: 31+ DPD, ECL = LGD × EAD")

# --- By grade ---
st.subheader("ECL by grade")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**ECL ($mn)**")
    st.bar_chart(by_grade["ecl"] / 1e6)
with c2:
    st.markdown("**Coverage (%)**")
    st.bar_chart(by_grade["coverage_%"])

# --- Pricing ---
st.subheader("Is each grade priced for its risk?")
st.bar_chart(pricing[["interest_rate_%", "actual_loss_%"]].rename(columns={
    "interest_rate_%": "Interest rate (%)", "actual_loss_%": "First-year loss (%)"}), stack=False)

st.dataframe(pricing.rename(columns={
    "interest_rate_%": "Interest rate (%)", "expected_loss_%": "Predicted loss (%)",
    "actual_loss_%": "Actual loss (%)", "risk_adj_yield_%": "Risk-adjusted yield (%)",
    "loss_share_of_yield_%": "Loss as % of yield"}), use_container_width=True)

st.warning("Grade G earns a lower risk-adjusted yield than grade F: its rate is only ~1pp higher (pricing nears a ~31% ceiling) while first-year losses are ~3pp higher. Losses absorb 56% of grade G's interest income vs 13% for grade A.")
st.caption("Based on 2017 loans. First-year loss is a proxy for annual loss. Excludes funding, servicing and operating costs.")