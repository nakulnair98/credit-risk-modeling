import numpy as np
import pandas as pd
import streamlit as st
from utils import load_csv, mn

st.set_page_config(page_title="ECL & Scenarios", layout="wide")
st.title("ECL scenarios and backtest")

grid = load_csv("ecl_scenario_grid.csv")
by_stage = load_csv("ecl_by_stage.csv", index_col=0)
backtest = load_csv("backtest_by_grade.csv", index_col=0)
total_ead = by_stage.loc["Total", "ead"]


def ecl_at(stage, mult):
    g = grid[grid["stage"] == stage]
    return np.interp(min(mult, 2.0), g["pd_mult"], g["ecl"])


def total_ecl(mult, s2_overlay):
    return ecl_at(1, mult) + ecl_at(2, mult * s2_overlay) + ecl_at(3, mult)


# --- Controls ---
st.subheader("Scenario settings")
c1, c2, c3 = st.columns(3)
with c1:
    up_mult = st.slider("Upside PD multiplier", 0.5, 1.0, 0.85, 0.05)
    up_w = st.slider("Upside weight", 0.0, 0.5, 0.10, 0.05)
with c2:
    down_mult = st.slider("Downside PD multiplier", 1.0, 2.0, 1.30, 0.05)
    down_w = st.slider("Downside weight", 0.0, 0.5, 0.30, 0.05)
with c3:
    s2_overlay = st.slider("Stage 2 PD overlay (post-model adjustment)", 1.0, 1.5, 1.0, 0.05)
    base_w = 1 - up_w - down_w
    st.metric("Base weight", f"{base_w:.0%}")

if base_w < 0:
    st.error("Upside and downside weights add up to more than 100%.")
    st.stop()

# --- Results ---
table = pd.DataFrame({
    "Scenario": ["Upside", "Base", "Downside"],
    "PD multiplier": [up_mult, 1.0, down_mult],
    "Weight": [up_w, base_w, down_w],
})
table["ECL"] = [total_ecl(m, s2_overlay) for m in table["PD multiplier"]]
weighted = (table["ECL"] * table["Weight"]).sum()
base = table.loc[1, "ECL"]

c1, c2, c3 = st.columns(3)
c1.metric("Base ECL", mn(base))
c2.metric("Probability-weighted ECL", mn(weighted), f"{(weighted / base - 1) * 100:+.1f}% vs base", delta_color="inverse")
c3.metric("Weighted coverage", f"{weighted / total_ead * 100:.2f}%")

table["ECL"] = table["ECL"].map(mn)
st.dataframe(table, hide_index=True, use_container_width=True)
st.caption("Multipliers and weights are illustrative. In practice they come from a macroeconomic model (unemployment, GDP, rates). "
           "The Stage 2 overlay reflects that Stage 2 loans keep their origination PD in this model.")

# --- Backtest ---
st.subheader("Backtest: predicted vs actual 12-month loss (2017 loans)")
bt = backtest[["pred_loss_%", "actual_loss_%"]].rename(columns={
    "pred_loss_%": "Predicted loss (%)", "actual_loss_%": "Actual loss (%)"})
st.bar_chart(bt.drop("Total"), stack=False)
st.dataframe(backtest[["pred_loss_%", "actual_loss_%", "pred / actual"]], use_container_width=True)
st.warning("Accurate for grades C–D (0.97–1.01) but understated for E–G (down to 0.76). "
           "Recommend a PD overlay for E–G until the model is recalibrated on more recent data.")