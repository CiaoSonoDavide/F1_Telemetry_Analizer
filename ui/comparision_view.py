import streamlit as st
from streamlit import config

from core.session_manager import load_gp_session
from core.lap_handler import get_best_lap, get_telemetry_data
from visualization.charts import create_dual_driver_comparision
from data.fastf1_data import get_driver_by_session

def render_comparision(config):
    st.sidebar.subheader("Driver Selection")

    with st.spinner("Loading drivers..."):
        drivers = get_driver_by_session(
            config['year'],
            config['gp'],
            config['session_type']
        )

        if not drivers:
            st.error("No drivers found for the selected session")
            return

        col1,col2 = st.sidebar.columns(2)
        with col1:
            driver1 = st.selectbox(
                "Driver 1",
                drivers,
                key="driver1"
            )
        with col2:
            driver2 = st.selectbox(
                "Driver 2",
                drivers,
                index=1 if len(drivers) > 1 else 0,
                key="driver2"
            )

        if st.sidebar.button("Load Comparision", key="load_comparision"):
            with st.spinner("Loading session..."):
                try:
                    session = load_gp_session(
                        config['year'],
                        config['gp'],
                        config['session_type']
                    )

                    best_lap1 = get_best_lap(session, driver1)
                    if best_lap1 is None or best_lap1 is True:
                        st.error(f"Driver {driver1} not  found or has no valid laps")
                    else:
                        telemetry1 = get_telemetry_data(best_lap1)

                        best_lap2 = get_best_lap(session, driver2)
                        if best_lap2 is None or best_lap2 is True:
                            st.error(f"Driver {driver2} not  found or has no valid laps")
                        else:
                            telemetry2 = get_telemetry_data(best_lap2)

                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                lap_time1 = str(best_lap1['LapTime']).split()[-1][:8]
                                st.metric(f"{driver1} Lap Time", lap_time1)
                            with col2:
                                max_speed1 = telemetry1['Speed'].max()
                                st.metric(f"{driver1} Max Speed", f"{max_speed1} km/h")
                            with col3:
                                lap_time2 = str(best_lap2['LapTime']).split()[-1][:8]
                                st.metric(f"{driver2} Lap Time", lap_time2)
                            with col4:
                                max_speed2 = telemetry2['Speed'].max()
                                st.metric(f"{driver2} Max Speed", f"{max_speed2} km/h")

                            fig  = create_dual_driver_comparision(
                                telemetry1,
                                driver1,
                                telemetry2,
                                driver2,
                                session,
                                channels=config['channels'],
                                show_curves=config['show_curves']
                            )
                            st.pyplot(fig)
                except Exception as e:
                    st.error(f"Loading errror: {e}")