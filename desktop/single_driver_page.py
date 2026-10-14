from desktop.charts_canvas import ScrollableFigureCanvas
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget, QScrollArea,
)

from desktop.charts_canvas import ScrollableFigureCanvas


class SingleDriverPage(QWidget):
    def __init__(self):
        super().__init__()

        self.driver_combo = QComboBox()

        self.lap_time_label = QLabel("-")
        self.max_speed_label = QLabel("-")

        self.chart_widget = QWidget()
        self.chart_container = QVBoxLayout(self.chart_widget)

        self.chart_scroll_area = QScrollArea()
        self.chart_scroll_area.setWidget(self.chart_widget)
        self.chart_scroll_area.setWidgetResizable(True)
        self.chart_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.chart_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

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
        main_layout.addWidget(self.chart_scroll_area, stretch=1)

    def set_drivers(self, drivers: list[str]):
        self.driver_combo.clear()
        self.driver_combo.addItems(drivers)
        self.driver_combo.setEnabled(bool(drivers))

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

        canvas = ScrollableFigureCanvas(
            figure = result["figure"],
            scroll_area = self.chart_scroll_area
        )
        canvas.setMinimumHeight(1200)
        canvas.setMinimumWidth(800)

        self.chart_container.addWidget(canvas)

        canvas.draw()

    def clear_chart(self):
        while self.chart_container.count():
            item = self.chart_container.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()