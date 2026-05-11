def get_best_lap(session, driver_abbr):
    lap = session.laps.pick_driver(driver_abbr).pick_fastest()
    return lap

def get_telemetry_data(lap):
    tel = lap.get_telemetry()
    return tel
