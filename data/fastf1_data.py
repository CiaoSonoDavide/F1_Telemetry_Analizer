""" Import necessary modules"""
import fastf1
import pandas as pd
from functools import lru_cache
from typing import List
from datetime import datetime

""" Define session mapping for different session types """
SESSION_MAPPING = {
    'Practice 1': 'FP1',
    'Practice 2': 'FP2',
    'Practice 3': 'FP3',
    'Sprint Qualifying': 'SQ',
    'Sprint Shootout': 'SS',
    'Sprint': 'S',
    'Qualifying': 'Q',
    'Race': 'R'
}

""" Define the columns for the session data """
SESSION_COLUMNS = ['Session1', 'Session2', 'Session3', 'Session4', 'Session5']

""" Function to get available years with FastF1 data """
@lru_cache(maxsize=128)
def get_available_years() -> List[int]:
    try:
        current_year = datetime.now().year
        years = set()

        for year in range(2018, current_year+ 1):
            try:
                schedule = fastf1.get_event_schedule(year)
                if schedule is not None and not schedule.empty:
                    years.add(year)
            except:
                pass
        return sorted(list(years), reverse = True)
    except:
        return list(range(2018, current_year + 1))


""" Function to get Grand Prix names for a specific year """
@lru_cache(maxsize=128)
def get_gp_by_year(year: int) -> List[str]:
    try:
        schedule = fastf1.get_event_schedule(year)
        return schedule['EventName'].tolist()
    except Exception as e:
        print(f"Error loading GPs for {year}: {e}")
        return []


""" Function to get session types for a specific Grand Prix in a given year """
@lru_cache(maxsize=128)
def get_session_by_gp(year: int, gp_name: str) -> List[str]:
    try:
        schedule = fastf1.get_event_schedule(year)
        event = schedule[schedule['EventName'] == gp_name].iloc[0]
        sessions =[]

        for col in SESSION_COLUMNS:
            if col in event.index and pd.notna(event[col]):
                session_full_name = event[col]

                if session_full_name in SESSION_MAPPING:
                    sessions.append(SESSION_MAPPING[session_full_name])

        return sessions
    except Exception as e:
        print(f"Error loading sessions for {year} {gp_name}: {e}")
        return ['FP1', 'FP2', 'FP3', 'SQ', 'SS', 'S', 'Q', 'R']


""" Function to get drivers for a specific session in a given year and Grand Prix """
@lru_cache(maxsize=128)
def get_driver_by_session(year: int, gp_name: str, session_type: str) -> List[str]:
    try:
        from core.session_manager import load_gp_session

        session = load_gp_session(year,gp_name,session_type)

        if session is None:
            raise ValueError("Empty session data")

        if session.laps is None or session.laps.empty:
            raise ValueError("Session laps data is empty")

        if "Driver" not in session.laps.columns:
            raise ValueError("Driver column not found")

        drivers = (session.laps["Driver"].dropna().astype(str).unique().tolist())

        return sorted(drivers)

    except Exception as exc:
        print(f"Error loading drivers for " f"{year} / {gp_name} / {session_type}:", flush = True)
        raise RuntimeError("Unable to load drivers for the session.") from exc


""" Function to clear the cache of the lru_cache decorated functions """
def clear_cache():
    get_available_years.cache_clear()
    get_gp_by_year.cache_clear()
    get_session_by_gp.cache_clear()
    get_driver_by_session.cache_clear()