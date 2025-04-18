# main.py
import sys
import os
from PySide6.QtWidgets import QApplication
import logging
from gui.main_window import MainWindow


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
           level=logging.DEBUG,
           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
       )


    app = QApplication(sys.argv)

    # Set application style and metadata
    app.setApplicationName("Git Backup Tool")
    app.setOrganizationName("YourOrganization")

    # Create main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
