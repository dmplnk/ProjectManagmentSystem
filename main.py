import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from ui_assets import icon_path
from ui_theme import apply_app_theme
from windows.auth_window import AuthWindow


def main() -> None:
    app = QApplication(sys.argv)
    apply_app_theme(app)
    icon = icon_path()
    if icon:
        app.setWindowIcon(QIcon(str(icon)))
    window = AuthWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
