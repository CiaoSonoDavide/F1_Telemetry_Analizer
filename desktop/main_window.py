from PySide6.QtCore import QThread, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from desktop.analysis_worker import AnalysisWorker
from desktop.comparison_page import ComparisonPage
from desktop.config_panel import ConfigPanel
from desktop.single_driver_page import SingleDriverPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "F1 Telemetry Analyzer"
        )

        self.resize(1500, 950)

        self.last_driver_config = None
        self.worker_thread = None
        self.worker = None

        self.config_panel = ConfigPanel()
        self.pages = QStackedWidget()
        self.status_label = QLabel()
        self.progress_bar = QProgressBar()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.addWidget(self.progress_bar)

        self.single_page = SingleDriverPage()
        self.comparison_page = ComparisonPage()

        self.pages.addWidget(self.single_page)
        self.pages.addWidget(self.comparison_page)

        self.build_ui()
        self.connect_signals()

    def build_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        content_layout = QHBoxLayout()

        content_layout.addWidget(
            self.config_panel,
            stretch=0,
        )

        content_layout.addWidget(
            self.pages,
            stretch=1,
        )

        main_layout.addLayout(
            content_layout,
            stretch=1,
        )

        self.setCentralWidget(central_widget)

        self.progress_bar.setVisible(False)
        self.status_label.setText(
            "Seleziona una sessione"
        )

    def connect_signals(self):
        self.config_panel.mode_changed.connect(
            self.on_mode_changed
        )

        self.config_panel.configuration_changed.connect(
            self.load_drivers
        )

        self.config_panel.load_requested.connect(
            self.start_analysis
        )

    @Slot(str)
    def on_mode_changed(self, mode: str):
        if mode == "Single Driver":
            self.pages.setCurrentWidget(
                self.single_page
            )
        else:
            self.pages.setCurrentWidget(
                self.comparison_page
            )

    @Slot(dict)
    def load_drivers(self, config: dict):
        if self.worker_thread is not None:
            return

        year = config.get("year")
        gp = config.get("gp")
        session_type = config.get("session_type")

        if not year or not gp or not session_type:
            return

        config_key = (year, gp, session_type)

        if config_key == self.last_driver_config:
            return

        self.status_label.setText("Download/caricamento dati FastF1...")
        self.last_driver_config = config_key

        self.start_worker(
            operation="drivers",
            config=config,
        )

    @Slot(dict)
    def start_analysis(self, config: dict):
        if self.worker_thread is not None:
            QMessageBox.warning(
                self,
                "Operazione in corso",
                "Attendi il completamento del caricamento attuale.",
            )
            return

        if config["mode"] == "Single Driver":
            driver = self.single_page.selected_driver()

            if not driver:
                QMessageBox.warning(
                    self,
                    "Pilota mancante",
                    "Seleziona un pilota.",
                )
                return

            config["driver"] = driver
            operation = "single"

        else:
            driver1, driver2 = (
                self.comparison_page.selected_drivers()
            )

            if not driver1 or not driver2:
                QMessageBox.warning(
                    self,
                    "Piloti mancanti",
                    "Seleziona due piloti.",
                )
                return

            if driver1 == driver2:
                QMessageBox.warning(
                    self,
                    "Piloti uguali",
                    "Seleziona due piloti diversi.",
                )
                return

            config["driver1"] = driver1
            config["driver2"] = driver2
            operation = "comparison"

        self.status_label.setText(
            "Caricamento sessione e generazione grafico..."
        )

        self.start_worker(
            operation=operation,
            config=config,
        )

    def start_worker(self, operation: str, config: dict):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Caricamento in corso...")

        thread = QThread(self)
        worker = AnalysisWorker(operation=operation, config=config)

        self.worker_thread = thread
        self.worker = worker

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.finished.connect(self.on_worker_finished)

        worker.error.connect(self.on_worker_error)

        worker.finished.connect(thread.quit)

        worker.error.connect(thread.quit)

        thread.finished.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)

        thread.finished.connect(self.on_worker_thread_finished)

        thread.start()

    @Slot(object)
    def on_worker_finished(self, result: dict):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        result_type = result.get("type")

        if result_type == "drivers":
            drivers = result["drivers"]

            self.single_page.set_drivers(drivers)
            self.comparison_page.set_drivers(drivers)

            if drivers:
                self.status_label.setText(
                    f"{len(drivers)} piloti caricati"
                )
            else:
                self.status_label.setText(
                    "Nessun pilota trovato"
                )

        elif result_type == "single":
            self.single_page.display_result(
                result
            )

            self.status_label.setText(
                "Analisi completata"
            )

        elif result_type == "comparison":
            self.comparison_page.display_result(
                result
            )

            self.status_label.setText(
                "Confronto completato"
            )

    @Slot(str)
    def on_worker_error(self, message: str):
        self.last_driver_config = None
        self.status_label.setText(
            "Errore durante l'operazione"
        )

        QMessageBox.critical(
            self,
            "Errore",
            message
        )

    @Slot()
    def on_worker_thread_finished(self):
        self.worker = None
        self.worker_thread = None

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)