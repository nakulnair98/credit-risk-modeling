from pathlib import Path
import pandas as pd
import streamlit as st
import joblib

ART = Path(__file__).resolve().parents[1] / "artifacts"


@st.cache_data
def load_csv(name, **kwargs):
    return pd.read_csv(ART / name, **kwargs)


@st.cache_data
def load_parquet(name):
    return pd.read_parquet(ART / name)


@st.cache_resource
def load_model(name):
    return joblib.load(ART / name)


def mn(x):
    return f"${x / 1e6:,.1f}mn"