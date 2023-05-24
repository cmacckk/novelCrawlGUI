from src.ui.home_ui import HomeUI


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = HomeUI()
    window.show()
    sys.exit(app.exec())