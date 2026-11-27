import numpy as np
import pandas as pd
import streamlit as st
from utils import load_csv, load_model, load_parquet

st.set_page_config(page_title="Scorecard", layout="wide")
st.title("Scorecard")
st.caption("600 points = 50:1 good:bad odds. Every 20 points doubles the odds (PDO = 20). Higher score = lower risk.")

art = load_model("pd_model.pkl")
edges, woe, features = art["edges"], art["woe"], art["features"]
scorecard = load_csv("scorecard.csv", keep_default_na=False)
points = scorecard.set_index(["feature", "bin"])["points"]
scores = load_parquet("pd_test_scores.parquet")

factor = 20 / np.log(2)
offset = 600 - factor * np.log(50)


def score_to_pd(s):
    return 1 / (1 + np.exp(-(offset - s) / factor))


# --- Points table ---
st.subheader("Points table")
feat = st.selectbox("Feature", features)
st.dataframe(scorecard[scorecard["feature"] == feat][["bin", "points"]],
             hide_index=True, use_container_width=True)

# --- Cut-off strategy ---
st.subheader("Cut-off strategy")


@st.cache_data
def cutoff_curve(df):
    rows = []
    for c in np.arange(df["score"].quantile(0.01), df["score"].quantile(0.99), 1.0):
        approved = df[df["score"] >= c]
        rows.append([c, len(approved) / len(df) * 100, approved["bad_12m"].mean() * 100])
    return pd.DataFrame(rows, columns=["Cut-off score", "Approval rate (%)", "Bad rate (%)"])


curve = cutoff_curve(scores)
cutoff = st.slider("Minimum score to approve", int(curve["Cut-off score"].min()),
                   int(curve["Cut-off score"].max()), 570)

approved = scores[scores["score"] >= cutoff]
c1, c2, c3 = st.columns(3)
c1.metric("Approval rate", f"{len(approved) / len(scores) * 100:.1f}%")
c2.metric("Bad rate (approved)", f"{approved['bad_12m'].mean() * 100:.2f}%")
c3.metric("Bad rate (all)", f"{scores['bad_12m'].mean() * 100:.2f}%")

c1, c2 = st.columns(2)
c1.line_chart(curve, x="Cut-off score", y="Approval rate (%)")
c2.line_chart(curve, x="Cut-off score", y="Bad rate (%)")
st.caption("Based on 2017 loans. Raising the cut-off lowers the bad rate but approves fewer borrowers.")

# --- Applicant scorer ---
st.subheader("Score an applicant")

defaults = {"int_rate": 12.0, "dti": 18.0, "credit_history_years": 15.0}
inputs = {}
cols = st.columns(3)
for i, col in enumerate(features):
    with cols[i % 3]:
        if col in edges:
            inputs[col] = st.number_input(col, value=defaults.get(col, 10.0))
        else:
            options = [o for o in woe[col].index if o != "nan"]
            inputs[col] = st.selectbox(col, options)

rows, total = [], 0
for col in features:
    if col in edges:
        label = str(pd.cut([inputs[col]], bins=edges[col])[0])
    else:
        label = inputs[col]
    p = points.get((col, label), 0)
    total += p
    rows.append([col, label, p])

pd_est = score_to_pd(total)
decision = "Approve" if total >= cutoff else "Decline"

c1, c2, c3 = st.columns(3)
c1.metric("Score", f"{total:.0f}")
c2.metric("12-month PD", f"{pd_est * 100:.2f}%")
c3.metric(f"Decision (cut-off {cutoff})", decision)

st.dataframe(pd.DataFrame(rows, columns=["Feature", "Bin", "Points"]),
             hide_index=True, use_container_width=True)
st.caption("The points breakdown shows the reasons behind each decision, which a lender needs for adverse action notices.")