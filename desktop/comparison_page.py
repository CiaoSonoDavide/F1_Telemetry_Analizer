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


class ComparisonPage(QWidget):
    def __init__(self):
        super().__init__()

        self.driver1_combo = QComboBox()
        self.driver2_combo = QComboBox()

        self.lap_time1_label = QLabel("-")
        self.max_speed1_label = QLabel("-")
        self.lap_time2_label = QLabel("-")
        self.max_speed2_label = QLabel("-")

        self.chart_container = QVBoxLayout()

        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)

        drivers_group = QGroupBox("Drivers")
        drivers_layout = QFormLayout(drivers_group)

        drivers_layout.addRow(
            "Driver 1:",
            self.driver1_combo,
        )

        drivers_layout.addRow(
            "Driver 2:",
            self.driver2_combo,
        )

        metrics_group = QGroupBox("Metrics")
        metrics_layout = QFormLayout(metrics_group)

        metrics_layout.addRow(
            "Driver 1 Lap Time:",
            self.lap_time1_label,
        )

        metrics_layout.addRow(
            "Driver 1 Max Speed:",
            self.max_speed1_label,
        )

        metrics_layout.addRow(
            "Driver 2 Lap Time:",
            self.lap_time2_label,
        )

        metrics_layout.addRow(
            "Driver 2 Max Speed:",
            self.max_speed2_label,
        )

        main_layout.addWidget(drivers_group)
        main_layout.addWidget(metrics_group)
        main_layout.addLayout(self.chart_container, stretch=1)

    def set_drivers(self, drivers: list[str]):
        self.driver1_combo.clear()
        self.driver2_combo.clear()

        self.driver1_combo.addItems(drivers)
        self.driver2_combo.addItems(drivers)

        if len(drivers) > 1:
            self.driver2_combo.setCurrentIndex(1)

    def selected_drivers(self) -> tuple[str, str]:
        return (
            self.driver1_combo.currentText(),
            self.driver2_combo.currentText(),
        )

    def display_result(self, result: dict):
        self.lap_time1_label.setText(
            result["lap_time1"]
        )

        self.max_speed1_label.setText(
            f"{result['max_speed1']:.2f} km/h"
        )

        self.lap_time2_label.setText(
            result["lap_time2"]
        )

        self.max_speed2_label.setText(
            f"{result['max_speed2']:.2f} km/h"
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