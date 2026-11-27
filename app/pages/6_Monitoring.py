import streamlit as st
from utils import load_csv

st.set_page_config(page_title="Monitoring", layout="wide")
st.title("Monitoring: model stability")

m = load_csv("summary_metrics.csv").set_index("metric")["value"]
dist = load_csv("psi_score_distribution.csv", index_col=0) * 100
csi = load_csv("csi.csv", index_col=0)


def light(x):
    return "🟢 Stable" if x < 0.10 else ("🟡 Monitor" if x < 0.25 else "🔴 Significant shift")


st.subheader("Population Stability Index (score)")
c1, c2 = st.columns(2)
c1.metric("PSI 2017 vs development", f"{m['psi_2017']:.3f}", light(m["psi_2017"]), delta_color="off")
c2.metric("PSI 2018 vs development", f"{m['psi_2018']:.3f}", light(m["psi_2018"]), delta_color="off")

st.bar_chart(dist.rename(columns={"train_%": "Development (2015–16)", "test_2017_%": "2017",
                                  "live_2018_%": "2018"}), stack=False)
st.caption("Share of loans in each development-sample score decile. The 2018 book shifted toward higher (safer) scores.")

st.subheader("Characteristic Stability Index (by feature)")
st.dataframe(csi.round(3), use_container_width=True)
st.info("int_rate and grade are amber, reflecting Lending Club's shift toward better-quality borrowers in 2018. "
        "Overall score PSI is green, so the model remains fit for use. These features should be watched, not acted on.")

st.subheader("Model limitations")
st.markdown("""
- **Origination PD only:** no monthly payment history, so Stage 2 loans keep their origination PD and their lifetime ECL is likely understated.
- **Illustrative scenarios:** PD multipliers and weights are assumptions, not outputs of a macroeconomic model.
- **LGD:** reflects Lending Club's debt sales, not a bank's in-house collections, and is undiscounted.
- **12-month default flag:** inferred from the last payment date.
- **Backtest:** one year (2017) in a benign credit environment.
- **Yields:** exclude funding, servicing and operating costs.
""")