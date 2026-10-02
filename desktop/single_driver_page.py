from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class SingleDriverPage(QWidget):
    def __init__(self):
        super().__init__()

        self.driver_combo = QComboBox()

        self.lap_time_label = QLabel("-")
        self.max_speed_label = QLabel("-")

        self.chart_container = QVBoxLayout()

        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)

        driver_group = QGroupBox("Driver")
        driver_layout = QFormLayout(driver_group)

        driver_layout.addRow(
            "Driver:",
            self.driver_combo,
        )

        metrics_group = QGroupBox("Metrics")
        metrics_layout = QFormLayout(metrics_group)

        metrics_layout.addRow(
            "Lap Time:",
            self.lap_time_label,
        )

        metrics_layout.addRow(
            "Max Speed:",
            self.max_speed_label,
        )

        main_layout.addWidget(driver_group)
        main_layout.addWidget(metrics_group)
        main_layout.addLayout(self.chart_container, stretch=1)

    def set_drivers(self, drivers: list[str]):
        self.driver_combo.clear()
        self.driver_combo.addItems(drivers)

    def selected_driver(self) -> str:
        return self.driver_combo.currentText()

    def display_result(self, result: dict):
        self.lap_time_label.setText(
            result["lap_time"]
        )

        self.max_speed_label.setText(
            f"{result['max_speed']:.2f} km/h"
        )

        self.clear_chart()

        canvas = FigureCanvasQTAgg(result["figure"])
        canvas.setMinimumHeight(600)
        canvas.setMinimumWidth(800)
        canvas.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.chart_container.addWidget(canvas)
        canvas.draw()

    def clear_chart(self):
        while self.chart_container.count():
            item = self.chart_container.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()