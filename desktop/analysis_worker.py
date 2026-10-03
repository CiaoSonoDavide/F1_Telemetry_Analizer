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

class AnalysisWorker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, operation: str, config: dict):
        super().__init__()

        self.operation = operation
        self.config = config

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
            print(error_details, flush=True)
            self.error.emit(f"{type(exc).__name__}: {exc}\n\n""Dettagli completi nella console di PyCharm.")

    def load_drivers(self):
        year = self.config.get("year")
        gp = self.config.get("gp")
        session_type = self.config.get("session_type")

        if not year or not gp or not session_type:
            raise ValueError("Configurazione sessione incompleta.")

        drivers = get_driver_by_session(year, gp, session_type)

        if not drivers:
            raise ValueError("FastF1 non ha restituito piloti per la sessione " f"{year} - {gp} - {session_type}.")

        return {
            "type": "drivers",
            "drivers": drivers,
        }

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
                f"Il pilota {driver} non ha giri validi"
            )

        telemetry = get_telemetry_data(best_lap)

        if telemetry is None or telemetry.empty:
            raise ValueError(
                f"Nessuna telemetria disponibile per {driver}"
            )

        figure = create_telemetry(
            telemetry=telemetry,
            driver_name=driver,
            session=session,
            channels=self.config["channels"],
            show_curves=self.config["show_curves"],
        )

        return {
            "type": "single",
            "figure": figure,
            "lap_time": self.format_lap_time(best_lap),
            "max_speed": float(telemetry["Speed"].max()),
        }

    def run_comparison_analysis(self):
        session = load_gp_session(
            self.config["year"],
            self.config["gp"],
            self.config["session_type"],
        )

        driver1 = self.config["driver1"]
        driver2 = self.config["driver2"]

        best_lap1 = get_best_lap(
            session,
            driver1,
        )

        best_lap2 = get_best_lap(
            session,
            driver2,
        )

        if best_lap1 is None:
            raise ValueError(
                f"Il pilota {driver1} non ha giri validi"
            )

        if best_lap2 is None:
            raise ValueError(
                f"Il pilota {driver2} non ha giri validi"
            )

        original_telemetry1 = get_telemetry_data(best_lap1)
        original_telemetry2 = get_telemetry_data(best_lap2)
        channels = self.config.get("channels")

        telemetry1, telemetry2 = (
            interpolate_telemetry_by_distance(
                telemetry1 = original_telemetry1,
                telemetry2 = original_telemetry2,
                channels = channels,
                step=1.0
            )
        )

        figure = create_dual_driver_comparison(
            telemetry_driver1=telemetry1,
            driver1_name=driver1,
            telemetry_driver2=telemetry2,
            driver2_name=driver2,
            session=session,
            channels=self.config["channels"],
            show_curves=self.config["show_curves"],
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