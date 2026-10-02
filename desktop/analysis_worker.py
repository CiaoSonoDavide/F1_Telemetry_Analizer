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
            self.error.emit(str(exc))

    def load_drivers(self):
        drivers = get_driver_by_session(
            self.config["year"],
            self.config["gp"],
            self.config["session_type"],
        )

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

        telemetry1 = get_telemetry_data(best_lap1)
        telemetry2 = get_telemetry_data(best_lap2)

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

        if lap_time is None:
            return "N/A"

        return str(lap_time).split()[-1]