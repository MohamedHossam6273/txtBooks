import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    """
    Entry point for HeliumNotes app.
    Initializes the Qt application and launches the main window.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("HeliumNotes")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()