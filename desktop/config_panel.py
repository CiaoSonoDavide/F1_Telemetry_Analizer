from PySide6.QtCore import Signal, QSignalBlocker
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from data.fastf1_data import (
    get_available_years,
    get_gp_by_year,
    get_session_by_gp,
)


class ConfigPanel(QWidget):
    configuration_changed = Signal(dict)
    load_requested = Signal(dict)
    mode_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setMinimumWidth(260)
        self.setMaximumWidth(340)

        self.mode_single = QRadioButton("Single Driver")
        self.mode_comparison = QRadioButton("Driver Comparison")

        self.mode_single.setChecked(True)

        self.year_combo = QComboBox()
        self.gp_combo = QComboBox()
        self.session_combo = QComboBox()

        self.speed_checkbox = QCheckBox("Speed")
        self.rpm_checkbox = QCheckBox("RPM")
        self.throttle_checkbox = QCheckBox("Throttle")
        self.brake_checkbox = QCheckBox("Brake")
        self.drs_checkbox = QCheckBox("DRS")
        self.gear_checkbox = QCheckBox("nGear")
        self.curves_checkbox = QCheckBox(
            "Show Curve Markers"
        )

        for checkbox in (
            self.speed_checkbox,
            self.rpm_checkbox,
            self.throttle_checkbox,
            self.brake_checkbox,
            self.drs_checkbox,
            self.gear_checkbox,
            self.curves_checkbox,
        ):
            checkbox.setChecked(True)

        self.load_button = QPushButton("Load Analysis")

        self.build_ui()
        self.connect_signals()
        self.populate_years()

    def build_ui(self):
        main_layout = QVBoxLayout(self)

        mode_group = QGroupBox("Mode")
        mode_layout = QVBoxLayout(mode_group)

        mode_layout.addWidget(self.mode_single)
        mode_layout.addWidget(self.mode_comparison)

        session_group = QGroupBox("Session")
        session_layout = QVBoxLayout(session_group)

        session_layout.addWidget(QLabel("Year"))
        session_layout.addWidget(self.year_combo)

        session_layout.addWidget(QLabel("Grand Prix"))
        session_layout.addWidget(self.gp_combo)

        session_layout.addWidget(QLabel("Session Type"))
        session_layout.addWidget(self.session_combo)

        channels_group = QGroupBox("Telemetry Channels")
        channels_layout = QVBoxLayout(channels_group)

        channels_layout.addWidget(self.speed_checkbox)
        channels_layout.addWidget(self.rpm_checkbox)
        channels_layout.addWidget(self.throttle_checkbox)
        channels_layout.addWidget(self.brake_checkbox)
        channels_layout.addWidget(self.drs_checkbox)
        channels_layout.addWidget(self.gear_checkbox)
        channels_layout.addWidget(self.curves_checkbox)

        main_layout.addWidget(mode_group)
        main_layout.addWidget(session_group)
        main_layout.addWidget(channels_group)
        main_layout.addWidget(self.load_button)
        main_layout.addStretch()

    def connect_signals(self):
        self.mode_single.toggled.connect(
            self.on_mode_changed
        )

        self.mode_comparison.toggled.connect(
            self.on_mode_changed
        )

        self.year_combo.currentIndexChanged.connect(
            self.populate_gp
        )

        self.gp_combo.currentIndexChanged.connect(
            self.populate_sessions
        )

        self.session_combo.currentIndexChanged.connect(
            self.on_session_changed
        )

        self.load_button.clicked.connect(
            self.request_load
        )

    def populate_years(self):
        self.year_combo.clear()

        years = get_available_years()

        self.year_combo.addItems(
            [str(year) for year in years]
        )

        self.populate_gp()

    def populate_gp(self):
        with QSignalBlocker(self.gp_combo):
            self.gp_combo.clear()

            year_text = self.year_combo.currentText()

            if not year_text:
                return

            year = int(year_text)
            gps = get_gp_by_year(year)

            self.gp_combo.addItems(gps)
        self.populate_sessions()

    def populate_sessions(self):
        with QSignalBlocker(self.session_combo):
            self.session_combo.clear()

            year_text = self.year_combo.currentText()
            gp_name = self.gp_combo.currentText()

            if not year_text or not gp_name:
                return

            year = int(year_text)
            sessions = get_session_by_gp(year, gp_name)

            self.session_combo.addItems(sessions)

        if self.session_combo.count() > 0:
            self.on_session_changed(self.session_combo.currentIndex())

    def on_session_changed(self, index: int):
        if index < 0:
            return

        config = self.current_configuration()
        if(config["year"] and config["gp"] and config["session_type"]):
            self.configuration_changed.emit(config)

    def on_mode_changed(self, checked: bool):
        if not checked:
            return

        mode = self.current_mode()
        self.mode_changed.emit(mode)

    def current_mode(self) -> str:
        if self.mode_single.isChecked():
            return "Single Driver"

        return "Driver Comparison"

    def selected_channels(self):
        checkbox_mapping = [
            ("Speed", self.speed_checkbox),
            ("RPM", self.rpm_checkbox),
            ("Throttle", self.throttle_checkbox),
            ("Brake", self.brake_checkbox),
            ("DRS", self.drs_checkbox),
            ("nGear", self.gear_checkbox),
        ]

        channels = [
            name
            for name, checkbox in checkbox_mapping
            if checkbox.isChecked()
        ]

        return channels

    def current_configuration(self) -> dict:
        year_text = self.year_combo.currentText()

        return {
            "mode": self.current_mode(),
            "year": int(year_text) if year_text else None,
            "gp": self.gp_combo.currentText(),
            "session_type": self.session_combo.currentText(),
            "channels": self.selected_channels(),
            "show_curves": self.curves_checkbox.isChecked(),
        }

    def request_load(self):
        config = self.current_configuration()

        if not config["year"]:
            return

        if not config["gp"]:
            return

        if not config["session_type"]:
            return

        self.load_requested.emit(config)
