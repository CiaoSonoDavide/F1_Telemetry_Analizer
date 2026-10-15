""" Import necessary modules """
import sys

import fastf1.plotting as plotting
from PySide6.QtWidgets import QApplication

from core.session_manager import setup_cache
from desktop.main_window import MainWindow

""" Main function to run the application """
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

""" Entry point of the application """
if __name__ == "__main__":
    main()