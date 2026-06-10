import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="AutoAdvisor AI", layout="wide")
st.title("AutoAdvisor AI")
st.caption("Lebanon-first, MENA-ready intelligent car-buying assistant")

st.info("The recommendation, comparison, image analysis, and dealer workflows are coming next.")

if st.button("Check backend connection"):
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        st.success(f"Backend status: {response.json()['status']}")
    except requests.RequestException as exc:
        st.error(f"Could not connect to the backend: {exc}")
