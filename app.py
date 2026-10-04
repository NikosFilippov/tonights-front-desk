import json
from pathlib import Path

import pandas as pd
import streamlit as st

from portable import Model


# -----------------------------
# Configuration
# -----------------------------

MODEL_DIR = Path(__file__).parent / "model"


# -----------------------------
# Load model
# -----------------------------

@st.cache_resource
def load_model():

    model = Model(MODEL_DIR)

    with open(MODEL_DIR / "config.json") as f:
        config = json.load(f)

    return model, config


model, config = load_model()


# -----------------------------
# Page
# -----------------------------

st.set_page_config(
    page_title="Student Support",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Support Risk Dashboard")

st.write(
    """
    This tool helps the study office identify students who may
    benefit from support.
    """
)
