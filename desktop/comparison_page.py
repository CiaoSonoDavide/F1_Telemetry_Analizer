from desktop.charts_canvas import ScrollableFigureCanvas
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget, QScrollArea,
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
        main_layout.addWidget(self.chart_scroll_area, stretch=1)

    def set_drivers(self, drivers: list[str]):
        self.driver1_combo.clear()
        self.driver2_combo.clear()

        self.driver1_combo.addItems(drivers)
        self.driver2_combo.addItems(drivers)

        self.driver1_combo.setEnabled(bool(drivers))
        self.driver2_combo.setEnabled(bool(drivers))

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

        canvas = ScrollableFigureCanvas(
            figure = result["figure"],
            scroll_area = self.chart_scroll_area
        )
        canvas.setMinimumHeight(1200)
        canvas.setMinimumWidth(900)

        self.chart_container.addWidget(canvas)

        canvas.draw()

    def clear_chart(self):
        while self.chart_container.count():
            item = self.chart_container.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()