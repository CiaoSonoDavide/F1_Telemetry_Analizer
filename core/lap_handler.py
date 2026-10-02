def get_best_lap(session, driver_abbr: str):
    laps = session.laps.pick_driver(driver_abbr)

    if laps is None or laps.empty:
        return None

    return laps.pick_driver(driver_abbr).pick_fastest()

def get_telemetry_data(lap):
    if lap is None:
        return None
    return lap.get_telemetry()
