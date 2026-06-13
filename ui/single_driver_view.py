import streamlit as st
from core.session_manager import load_gp_session
from core.lap_handler import get_best_lap, get_telemetry_data
from visualization.charts import create_telemetry
from data.fastf1_data import get_driver_by_session

def render_single_driver(config):
    st.sidebar.subheader('Driver Selection')

    with st.spinner('Loading drivers...'):
        drivers = get_driver_by_session(
            config['year'],
            config['gp'],
            config['session_type']
        )

    if not drivers:
        st.error("No drivers found for the selected session")
        return

    driver = st.sidebar.selectbox(
        "Driver",
        drivers,
        key='driver_single'
    )

    if st.sidebar.button("Load Analysis", key="load_single"):
        with st.spinner("Loadind session..."):
            try:
                session = load_gp_session(
                    config['year'],
                    config['gp'],
                    config['session_type']
                )
                best_lap = get_best_lap(session, driver)

                if best_lap is None or best_lap is True:
                    st.error(f"Driver {driver} not  found or has no valid laps")
                else:
                    telemetry = get_telemetry_data(best_lap)

                    col1, col2 = st.columns(2)
                    with col1:
                        lap_time = str(best_lap['LapTime']).split()[-1][:8]
                        st.metric("Lap Time", lap_time)
                    with col2:
                        max_speed = telemetry['Speed'].max()
                        st.metric("Max Speed", f"{max_speed} km/h")

                    fig = create_telemetry(
                        telemetry,
                        driver,
                        session,
                        channels = config['channels'],
                        show_curves= config['show_curves']
                    )
                    st.pyplot(fig)
            except Exception as e:
                st.error(f"Loading error: {e}")