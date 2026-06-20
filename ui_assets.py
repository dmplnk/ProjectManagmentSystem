"""Пути к иконке, логотипу и установка иконки окон."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QWidget

PROJECT_ROOT = Path(__file__).resolve().parent

PRIMARY_COLOR = "#0099bc"
PRIMARY_DARK = "#007a96"
PRIMARY_LIGHT = "#33adcc"


def _first_existing(*candidates: Path) -> Path | None:
    for path in candidates:
        if path.is_file():
            return path
    return None


def icon_path() -> Path | None:
    return _first_existing(
        PROJECT_ROOT / "icon.ico",
        PROJECT_ROOT / "icon.png",
        PROJECT_ROOT / "data" / "icon.ico",
        PROJECT_ROOT / "data" / "icon.png",
    )


def logo_path() -> Path | None:
    return _first_existing(
        PROJECT_ROOT / "logo.png",
        PROJECT_ROOT / "logo.jpg",
        PROJECT_ROOT / "data" / "logo.png",
        PROJECT_ROOT / "data" / "logo.jpg",
    )


def apply_window_icon(widget: QWidget) -> None:
    path = icon_path()
    if path:
        widget.setWindowIcon(QIcon(str(path)))


def load_logo_pixmap(max_height: int = 72) -> QPixmap | None:
    path = logo_path()
    if not path:
        return None
    pix = QPixmap(str(path))
    if pix.isNull():
        return None
    if pix.height() > max_height:
        pix = pix.scaledToHeight(max_height)
    return pix
