import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import roc_curve
from utils import load_csv, load_parquet

st.set_page_config(page_title="PD Model", layout="wide")
st.title("PD Model: WoE logistic scorecard")
st.caption("Target: default within 12 months. Trained on 2015–2016, tested out-of-time on 2017.")

scores = load_parquet("pd_test_scores.parquet")
comp = load_csv("model_comparison.csv")


@st.cache_data
def curves(df):
    y, p = df["bad_12m"].values, df["pd_12m"].values

    fpr, tpr, _ = roc_curve(y, p)
    idx = np.linspace(0, len(fpr) - 1, 200).astype(int)
    roc = pd.DataFrame({"False positive rate": fpr[idx], "Model": tpr[idx], "Random": fpr[idx]})

    d = df.sort_values("pd_12m", ascending=False)
    cum_bad = d["bad_12m"].cumsum() / d["bad_12m"].sum()
    cum_good = (1 - d["bad_12m"]).cumsum() / (1 - d["bad_12m"]).sum()
    idx = np.linspace(0, len(d) - 1, 200).astype(int)
    ks = pd.DataFrame({"Population (%)": np.arange(1, len(d) + 1)[idx] / len(d) * 100,
                       "Cumulative bads": cum_bad.values[idx],
                       "Cumulative goods": cum_good.values[idx]})

    cal = df.assign(decile=pd.qcut(df["pd_12m"], 10, labels=False) + 1)
    cal = cal.groupby("decile")[["pd_12m", "bad_12m"]].mean() * 100
    cal.columns = ["Predicted PD (%)", "Actual default rate (%)"]
    return roc, ks, cal


roc, ks, cal = curves(scores)

# --- Champion vs challenger ---
st.subheader("Champion vs challenger")
st.dataframe(comp.rename(columns={"model": "Model", "train_gini": "Train Gini",
                                  "test_gini": "Test Gini", "test_ks": "Test KS"}),
             hide_index=True, use_container_width=True)
st.info("LightGBM adds only 2 Gini points out of time and drops 6 points from train to test (overfitting). "
        "The scorecard is kept as champion: it is stable, transparent and easy to explain to borrowers and regulators.")

# --- Discrimination ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("ROC curve")
    st.line_chart(roc, x="False positive rate", y=["Model", "Random"])
with c2:
    st.subheader(f"KS = {(ks['Cumulative bads'] - ks['Cumulative goods']).max():.3f}")
    st.line_chart(ks, x="Population (%)", y=["Cumulative bads", "Cumulative goods"])

# --- Calibration ---
st.subheader("Calibration by PD decile (2017)")
st.bar_chart(cal, stack=False)
st.dataframe(cal.round(2), use_container_width=True)
st.caption("Deciles ranked from lowest to highest predicted PD. Close bars mean the model's PDs match actual default rates.")