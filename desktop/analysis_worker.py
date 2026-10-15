""" Import necessary modules """
from PySide6.QtCore import QObject, Signal, Slot
from core.lap_handler import (
    get_best_lap,
    get_telemetry_data,
)
from core.session_manager import load_gp_session
from data.fastf1_data import get_driver_by_session
from visualization.charts import (
    create_dual_driver_comparison,
    create_telemetry,
)
from analytics.telemetry import (interpolate_telemetry_by_distance)
import pandas as pd
import traceback

""" AnalysisWorker class handles the analysis operations in a separate thread """
class AnalysisWorker(QObject):
    finished = Signal(object)
    error = Signal(str)

    """ Function to initialize the AnalysisWorker with the specified operation and configuration """
    def __init__(self, operation: str, config: dict):
        super().__init__()

        self.operation = operation
        self.config = config

    """ Function to run the analysis operation based on the specified operation type """
    @Slot()
    def run(self):
        try:
            if self.operation == "drivers":
                result = self.load_drivers()

            elif self.operation == "single":
                result = self.run_single_analysis()

            elif self.operation == "comparison":
                result = self.run_comparison_analysis()

            else:
                raise ValueError(
                    f"Unknown worker operation: {self.operation}"
                )

            self.finished.emit(result)

        except Exception as exc:
            error_details = traceback.format_exc()
            print(error_details, flush = True)
            self.error.emit(f"{type(exc).__name__}: {exc}\n\n""Complete details in the console output.")

    """ Function to load drivers for the specified session based on the configuration """
    def load_drivers(self):
        year = self.config.get("year")
        gp = self.config.get("gp")
        session_type = self.config.get("session_type")

        if not year or not gp or not session_type:
            raise ValueError("Incomplete session configuration\nYear, GP, and session type are required")

        drivers = get_driver_by_session(year, gp, session_type)

        if not drivers:
            raise ValueError("FastF1 doesn't return drivers for the session " f"{year} - {gp} - {session_type}.")

        return {
            "type": "drivers",
            "drivers": drivers,
        }

    """ Function to run a single driver analysis based on the specified configuration """
    def run_single_analysis(self):
        session = load_gp_session(
            self.config["year"],
            self.config["gp"],
            self.config["session_type"],
        )

        driver = self.config["driver"]

        best_lap = get_best_lap(
            session,
            driver,
        )

        if best_lap is None:
            raise ValueError(
                f"The driver {driver} has no valid laps"
            )

        telemetry = get_telemetry_data(best_lap)

        if telemetry is None or telemetry.empty:
            raise ValueError(
                f"No telemetry data available for {driver}"
            )

        figure = create_telemetry(
            telemetry = telemetry,
            driver_name = driver,
            session = session,
            channels = self.config["channels"],
            show_curves = self.config["show_curves"],
        )

        return {
            "type": "single",
            "figure": figure,
            "lap_time": self.format_lap_time(best_lap),
            "max_speed": float(telemetry["Speed"].max()),
        }

    """ Function to run a comparison analysis between two drivers based on the specified configuration """
    def run_comparison_analysis(self):
        session = load_gp_session(
            self.config["year"],
            self.config["gp"],
            self.config["session_type"],
        )

        driver1 = self.config["driver1"]
        driver2 = self.config["driver2"]

        best_lap1 = get_best_lap(session, driver1)
        best_lap2 = get_best_lap(session, driver2)

        if best_lap1 is None:
            raise ValueError(
                f"The driver {driver1} has no valid laps"
            )

        if best_lap2 is None:
            raise ValueError(
                f"The driver {driver2} has no valid laps"
            )

        original_telemetry1 = get_telemetry_data(best_lap1)
        original_telemetry2 = get_telemetry_data(best_lap2)
        channels = self.config.get("channels")

        telemetry1, telemetry2 = (
            interpolate_telemetry_by_distance(
                telemetry1 = original_telemetry1,
                telemetry2 = original_telemetry2,
                channels = channels,
                step = 1.0
            )
        )

        figure = create_dual_driver_comparison(
            telemetry_driver1 = telemetry1,
            driver1_name = driver1,
            telemetry_driver2 = telemetry2,
            driver2_name = driver2,
            session = session,
            channels = self.config["channels"],
            show_curves = self.config["show_curves"],
        )

        return {
            "type": "comparison",
            "figure": figure,
            "driver1": driver1,
            "driver2": driver2,
            "lap_time1": self.format_lap_time(best_lap1),
            "lap_time2": self.format_lap_time(best_lap2),
            "max_speed1": float(telemetry1["Speed"].max()),
            "max_speed2": float(telemetry2["Speed"].max()),
        }

    """ Static method to format the lap time into a string representation """
    @staticmethod
    def format_lap_time(lap) -> str:
        lap_time = lap["LapTime"]

        if lap_time is None or pd.isna(lap_time):
            return "N/A"

        try:
            total_milliseconds = round(pd.to_timedelta(lap_time).total_seconds() * 1000)
            minutes, remainder = divmod(total_milliseconds, 60_000)
            seconds, milliseconds = divmod(remainder, 1_000)

            return (f"{minutes}:"
                    f"{seconds:02d}:"
                    f"{milliseconds:03d}")
        except(TypeError, ValueError):
            return "N/A"