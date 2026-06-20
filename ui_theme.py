
from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

APP_STYLESHEET = """
/* ---- База ---- */
QWidget {
    background-color: #f1f5f9;
    color: #0f172a;
    font-size: 11pt;
}

QDialog, QMessageBox {
    background-color: #ffffff;
}

/* ---- Карточка входа ---- */
QWidget#authWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #dceef5,
        stop:0.45 #f1f5f9,
        stop:1 #e8f4fc
    );
}

QFrame#authCard {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 16px;
    min-width: 400px;
    max-width: 440px;
}

QLabel#authTitle {
    font-size: 22pt;
    font-weight: 700;
    color: #007a96;
    padding-bottom: 4px;
}

QLabel#authSubtitle {
    font-size: 10pt;
    color: #64748b;
    padding-bottom: 12px;
}

/* ---- Шапка панелей ---- */
QFrame#panelHeader {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

QLabel#panelTitle {
    font-size: 16pt;
    font-weight: 700;
    color: #007a96;
}

QLabel#panelSubtitle {
    font-size: 10pt;
    color: #64748b;
}

QFrame#metricsCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 4px;
}

QFrame#metricCard {
    background-color: #ffffff;
    border: 1px solid #cce9f2;
    border-radius: 10px;
    min-width: 120px;
}

QLabel#metricValue {
    font-size: 22pt;
    font-weight: 700;
    color: #0099bc;
}

QLabel#metricCaption {
    font-size: 9pt;
    color: #64748b;
}

QLabel#sectionTitle {
    font-size: 12pt;
    font-weight: 600;
    color: #334155;
    padding: 8px 0 4px 0;
}

QLabel#mutedHint {
    font-size: 10pt;
    color: #64748b;
}

QLabel#emptyState {
    color: #64748b;
    background-color: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 8px;
    padding: 8px 14px;
}

QLabel#errorText {
    color: #b91c1c;
    font-size: 10pt;
}

QLabel#statusOnTime {
    color: #15803d;
    font-weight: 500;
}

QLabel#statusLate {
    color: #b91c1c;
    font-weight: 500;
}

/* ---- Поля ввода ---- */
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 20px;
    selection-background-color: #99d4e8;
    selection-color: #003d4d;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
    border: 2px solid #33adcc;
    padding: 7px 11px;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    selection-background-color: #cce9f2;
    selection-color: #003d4d;
    padding: 4px;
}

/* ---- Кнопки ---- */
QPushButton {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 18px;
    min-height: 20px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
}

QPushButton:pressed {
    background-color: #e2e8f0;
}

QPushButton:disabled {
    color: #94a3b8;
    background-color: #f1f5f9;
    border-color: #e2e8f0;
}

QPushButton#primaryButton {
    background-color: #0099bc;
    color: #ffffff;
    border: 1px solid #007a96;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #33adcc;
    border-color: #0099bc;
}

QPushButton#primaryButton:pressed {
    background-color: #007a96;
}

QPushButton#secondaryButton {
    background-color: #ffffff;
    color: #007a96;
    border: 1px solid #99d4e8;
}

QPushButton#secondaryButton:hover {
    background-color: #e8f6fa;
    border-color: #66c2da;
}

QPushButton#dangerButton {
    background-color: #ffffff;
    color: #b91c1c;
    border: 1px solid #fecaca;
}

QPushButton#dangerButton:hover {
    background-color: #fef2f2;
    border-color: #f87171;
}

QPushButton#compactButton {
    padding: 4px 10px;
    min-height: 16px;
    font-size: 9pt;
}

/* ---- Вкладки ---- */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 0 0 12px 12px;
    background-color: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background-color: #e2e8f0;
    color: #475569;
    border: 1px solid #cbd5e1;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 4px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #007a96;
    font-weight: 600;
    border-bottom: 2px solid #33adcc;
}

QTabBar::tab:hover:!selected {
    background-color: #f1f5f9;
    color: #334155;
}

/* ---- Таблицы ---- */
QTableWidget, QTableView {
    background-color: #ffffff;
    alternate-background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    gridline-color: #e2e8f0;
    selection-background-color: #cce9f2;
    selection-color: #003d4d;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #475569;
    padding: 10px 8px;
    border: none;
    border-bottom: 2px solid #cbd5e1;
    border-right: 1px solid #e2e8f0;
    font-weight: 600;
    font-size: 10pt;
}

QTableWidget::item {
    padding: 6px 4px;
}

QScrollBar:vertical {
    background: #f1f5f9;
    width: 10px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar:horizontal {
    background: #f1f5f9;
    height: 10px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 5px;
    min-width: 24px;
}

/* ---- Группы и прокрутка ---- */
QGroupBox {
    font-weight: 600;
    color: #334155;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 16px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: #007a96;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

/* ---- Формы ---- */
QFormLayout QLabel {
    color: #475569;
    font-weight: 500;
}

QDialogButtonBox QPushButton {
    min-width: 96px;
}

QDialogButtonBox QPushButton[text="Сохранить"],
QDialogButtonBox QPushButton[text="OK"],
QDialogButtonBox QPushButton[text="Да"] {
    background-color: #0099bc;
    color: #ffffff;
    border: 1px solid #007a96;
    font-weight: 600;
}
"""


def apply_app_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 11)
    if not font.exactMatch():
        font = QFont("Inter", 11)
    app.setFont(font)
    app.setStyleSheet(APP_STYLESHEET)


def content_margins(layout, margin: int = 20, spacing: int = 14) -> None:
    layout.setContentsMargins(margin, margin, margin, margin)
    layout.setSpacing(spacing)


def configure_table(table: QTableWidget, *, sortable: bool = True) -> None:
    from ui_tables import prepare_data_table

    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    table.verticalHeader().setDefaultSectionSize(36)
    prepare_data_table(table, sortable=sortable)


def resize_table_rows(table: QTableWidget) -> None:
    from ui_tables import resize_table_rows as _resize

    _resize(table)


def compact_table_rows(table: QTableWidget, *, line_height: int = 26) -> None:
    from ui_tables import compact_table_rows as _compact

    _compact(table, line_height=line_height)


def table_fit_content(table: QTableWidget) -> None:
    from ui_tables import table_fit_content as _fit

    _fit(table)


def table_show_rows(table: QTableWidget, visible_rows: int = 8) -> None:
    from ui_tables import table_show_rows as _show

    _show(table, visible_rows)


def stretch_table(table: QTableWidget) -> None:
    from ui_tables import stretch_table as _stretch

    _stretch(table)


def style_primary_button(button: QPushButton) -> None:
    button.setObjectName("primaryButton")
    button.setCursor(Qt.CursorShape.PointingHandCursor)


def style_secondary_button(button: QPushButton) -> None:
    button.setObjectName("secondaryButton")
    button.setCursor(Qt.CursorShape.PointingHandCursor)


def style_danger_button(button: QPushButton) -> None:
    button.setObjectName("dangerButton")
    button.setCursor(Qt.CursorShape.PointingHandCursor)


def style_compact_button(button: QPushButton) -> None:
    button.setObjectName("compactButton")
    button.setCursor(Qt.CursorShape.PointingHandCursor)


def section_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("sectionTitle")
    return label


def empty_state_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("emptyState")
    return label


def create_panel_header(
    title: str,
    subtitle: str = "",
    on_logout: Optional[Callable[[], None]] = None,
) -> QFrame:
    frame = QFrame()
    frame.setObjectName("panelHeader")
    row = QHBoxLayout(frame)
    row.setContentsMargins(20, 14, 20, 14)
    row.setSpacing(16)

    titles = QVBoxLayout()
    titles.setSpacing(2)
    title_lbl = QLabel(title)
    title_lbl.setObjectName("panelTitle")
    titles.addWidget(title_lbl)
    if subtitle:
        sub = QLabel(subtitle)
        sub.setObjectName("panelSubtitle")
        titles.addWidget(sub)
    row.addLayout(titles, 1)
    row.addStretch()

    if on_logout is not None:
        logout_btn = QPushButton("Выход")
        style_secondary_button(logout_btn)
        logout_btn.clicked.connect(on_logout)
        row.addWidget(logout_btn)

    return frame


def metric_card(caption: str) -> tuple[QFrame, QLabel]:
    card = QFrame()
    card.setObjectName("metricCard")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(12, 10, 12, 10)
    lay.setSpacing(2)
    value_lbl = QLabel("—")
    value_lbl.setObjectName("metricValue")
    cap_lbl = QLabel(caption)
    cap_lbl.setObjectName("metricCaption")
    lay.addWidget(value_lbl)
    lay.addWidget(cap_lbl)
    return card, value_lbl


def wrap_content_card(inner: QWidget) -> QFrame:
    card = QFrame()
    card.setObjectName("metricsCard")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(10)
    lay.addWidget(inner)
    return card
