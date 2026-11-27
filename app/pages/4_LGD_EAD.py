import streamlit as st
from utils import load_csv

st.set_page_config(page_title="LGD & EAD", layout="wide")
st.title("LGD and EAD")

m = load_csv("lgd_ead_metrics.csv").set_index("metric")["value"]

st.subheader("LGD: two-stage model")
st.caption("Step 1: logistic regression (any recovery?). Step 2: linear regression (recovery rate, if any). LGD = 1 − P(recovery) × predicted rate.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Mean predicted LGD", f"{m['Mean pred LGD']:.3f}")
c2.metric("Mean actual LGD", f"{m['Mean actual LGD']:.3f}")
c3.metric("Step 1 Gini", f"{m['LGD step 1 Gini']:.3f}")
c4.metric("Step 2 R²", f"{m['LGD step 2 R2']:.3f}")

st.info("LGD is well calibrated at portfolio level but barely separates borrowers, so it behaves like a flat ~90% LGD. "
        "Lending Club sold charged-off loans to debt buyers, so recoveries are low and similar across borrowers. "
        "Credit losses on this book are driven by PD, not recovery.")

st.subheader("EAD: regression vs payment schedule")
st.caption("CCF = balance at default ÷ funded amount.")

c1, c2, c3 = st.columns(3)
c1.metric("Regression R²", f"{m['EAD R2']:.3f}")
c2.metric("Regression MAE", f"{m['EAD MAE']:.3f}")
c3.metric("Schedule MAE", f"{m['Schedule EAD MAE']:.3f}")

st.success("The payment schedule beats the regression (MAE 0.019 vs 0.143), so the ECL uses the amortization schedule for EAD. "
           "For fixed-rate amortizing loans, the schedule is the natural EAD.")
st.caption("The schedule benchmark uses the actual default month (hindsight). The lifetime ECL steps through each future month, so this is how the schedule is applied anyway.")