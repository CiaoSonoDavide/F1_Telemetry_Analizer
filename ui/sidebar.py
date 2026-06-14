import streamlit as st
import pandas as pd
from data.fastf1_data import (
    get_available_years,
    get_gp_by_year,
    get_session_by_gp,
)


def render_sidebar():
    st.sidebar.header("Configuration")

    mode = st.sidebar.radio(
        "Select Mode",
        ["Single Driver", "Driver Comparision"],
        key="mode"
    )

    available_years = get_available_years()
    year = st.sidebar.selectbox(
        "Year",
        available_years,
        key="year"
    )

    gps = get_gp_by_year(year)
    gp = st.sidebar.selectbox(
        "Grand Prix",
        gps,
        key="gp"
    )

    sessions = get_session_by_gp(year, gp)
    session_type = st.sidebar.selectbox(
        "Session Type",
        sessions,
        key="session_type"
    )

    st.sidebar.subheader("Channels to Display")
    channels = []
    col1,col2 = st.sidebar.columns(2)
    with col1:
        if st.checkbox("Speed", value=True, key="ch_speed"):
            channels.append("Speed")
        if st.checkbox("RPM", value=True, key="ch_rpm"):
            channels.append("RPM")
        if st.checkbox("Throttle", value=True, key="ch_throttle"):
            channels.append("Throttle")
    with col2:
        if st.checkbox("Brake", value=True, key="ch_brake"):
            channels.append("Brake")
        if st.checkbox("DRS", value=True, key="ch_drs"):
            channels.append("DRS")
        if st.checkbox("nGear", value=True, key="ch_ngear"):
            channels.append("nGear")

    show_curves = st.sidebar.checkbox(
        "Show Curves Marker",
        value=True,
        key="show_curves"
    )

    st.sidebar.divider()

    return {
        'mode': mode,
        'year': year,
        'gp': gp,
        'session_type': session_type,
        'channels': channels if channels else None,
        'show_curves': show_curves
    }