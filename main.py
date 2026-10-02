import sys

import fastf1.plotting as plotting
from PySide6.QtWidgets import QApplication

from core.session_manager import setup_cache
from desktop.main_window import MainWindow


def main():
    plotting.setup_mpl(
        mpl_timedelta_support=True,
        color_scheme="fastf1",
    )

    setup_cache()

    app = QApplication(sys.argv)
    app.setApplicationName("F1 Telemetry Analyzer")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()