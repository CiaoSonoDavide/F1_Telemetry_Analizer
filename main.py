import streamlit as st
from streamlit import sidebar
from fastf1 import plotting as pl

from core.session_manager import setup_cache, load_gp_session
from core.lap_handler import get_best_lap, get_telemetry_data
from visualization.charts import create_telemetry

pl.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')
st.set_page_config(page_title="F1 Analysis", layout="wide")
setup_cache()

st.title("F1 Telemetry Analyzer 🏎️")

st.sidebar.header("Configuration")
year = st.sidebar.number_input("Anno", min_value=1950, max_value=2024, value=2023)
gp = st.sidebar.text_input("Gran Premio", value="Monza")
driver = st.sidebar.text_input("Driver (Abbreviation)", value="LEC").upper()

if sidebar.button("Load analysis"):
    with st.spinner("Loading session..."):
        try:
            session = load_gp_session(year, gp, 'Q')
            best_lap = get_best_lap(session, driver)
            telemetry = get_telemetry_data(best_lap)

            col1, col2 = st.columns(2)
            col1.metric("Lap Time", f"{best_lap['LapTime']}".split()[-1][:8])
            col2.metric("Max speed", f"{telemetry['Speed'].max()} km/h)")

            fig = create_telemetry(telemetry, driver, session)
            st.pyplot(fig)
        except Exception as e:
            print(f"Error: {e}")
            st.error(f"Loading error: {e}")