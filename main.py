import streamlit as st
from fastf1 import plotting as pl
from core.session_manager import setup_cache
from ui.sidebar import render_sidebar
from ui.single_driver_view import render_single_driver
from ui.comparision_view import render_comparision

pl.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')
st.set_page_config(page_title="F1 Analysis", layout="wide")
setup_cache()

st.title("F1 Telemetry Analyzer 🏎️")

config = render_sidebar()

if config['mode'] == "Single Driver":
    render_single_driver(config)
else:
    render_comparision(config)