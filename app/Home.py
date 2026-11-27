import streamlit as st
from utils import load_csv, mn

st.set_page_config(page_title="Credit Risk Modeling", layout="wide")

st.title("Credit Risk Modeling on Lending Club Data")
st.caption("PD, LGD, EAD and Ind AS 109 / IFRS 9 expected credit loss")

m = load_csv("summary_metrics.csv").set_index("metric")["value"]
comp = load_csv("model_comparison.csv").set_index("model")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Outstanding book (EAD)", f"${m['total_ead'] / 1e9:,.2f}bn")
c2.metric("Base ECL", mn(m["base_ecl"]))
c3.metric("Coverage", f"{m['base_ecl'] / m['total_ead'] * 100:.2f}%")
c4.metric("Scorecard Gini (out-of-time)", f"{comp.loc['Scorecard (logistic)', 'test_gini']:.3f}")
c5.metric("Score PSI (2018)", f"{m['psi_2018']:.3f}")

st.divider()

left, right = st.columns([3, 2])

with left:
    st.subheader("Summary")
    st.markdown(f"""
**Question:** How much should a lender provision for its 2018 consumer loan book under Ind AS 109 / IFRS 9, and are its risk grades priced to cover expected losses?

**Approach:** Built PD (WoE logistic scorecard), LGD (two-stage) and EAD models on 2015–2017 Lending Club loans, validated them out-of-time on 2017, and combined them into a staged, discounted, scenario-weighted ECL for the 2018 book.

**Key results**
- ECL of **{mn(m['base_ecl'])}** on a **${m['total_ead'] / 1e9:,.2f}bn** book; **{mn(m['weighted_ecl'])}** after scenario weighting
- Scorecard holds up out of time (Gini 0.439 → 0.422) and beats a LightGBM challenger on stability
- Backtest: predicted vs actual 12-month loss of 0.92 overall, but grades E–G are under-provisioned by 13–24%
- Grade G's interest rate barely exceeds grade F's while its losses are ~3pp higher, so it isn't priced for its risk

**Recommendation:** Keep the scorecard as champion, apply a PD overlay to grades E–G until recalibration, and review grade G pricing or appetite.
""")

with right:
    st.subheader("Pages")
    st.markdown("""
- **Portfolio:** ECL by stage and grade, pricing vs risk
- **PD Model:** discrimination, calibration, champion vs challenger
- **Scorecard:** points table, applicant scorer, cut-off strategy
- **LGD & EAD:** model results and EAD method choice
- **ECL & Scenarios:** scenario sliders, Stage 2 overlay, backtest
- **Monitoring:** PSI, CSI and model limitations
""")
    st.info("Data: Lending Club 2015–2018 originations, snapshot March 2019. Models trained on 2015–2016, tested on 2017, applied to the 2018 book.")