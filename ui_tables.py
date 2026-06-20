
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

_SORT_ASC: dict[int, bool] = {}


def _normalize_sort_value(value: Any) -> tuple:
    if value is None or value == "":
        return (0, "")
    if isinstance(value, datetime):
        return (1, value.timestamp())
    if isinstance(value, date):
        return (1, datetime.combine(value, datetime.min.time()).timestamp())
    if isinstance(value, (int, float)):
        return (2, float(value))
    return (3, str(value).casefold())


def _cell_sort_key(table: QTableWidget, row: int, col: int) -> Any:
    item = table.item(row, col)
    if item is not None:
        data = item.data(Qt.ItemDataRole.UserRole)
        if data is not None:
            return data
        return item.text()
    widget = table.cellWidget(row, col)
    if widget is None:
        return ""
    from PyQt6.QtWidgets import QLabel

    labels = widget.findChildren(QLabel)
    return " ".join(label.text() for label in labels if label.text())


def sort_table_by_column(table: QTableWidget, column: int) -> None:
    ascending = _SORT_ASC.get(column, True)
    row_count = table.rowCount()
    col_count = table.columnCount()
    if row_count < 2:
        return

    keys = [_cell_sort_key(table, row, column) for row in range(row_count)]
    snapshot = []
    for row in range(row_count):
        row_cells = []
        for col in range(col_count):
            widget = table.cellWidget(row, col)
            if widget is not None:
                table.removeCellWidget(row, col)
            row_cells.append((table.takeItem(row, col), widget))
        snapshot.append(row_cells)

    order = sorted(
        range(row_count),
        key=lambda r: _normalize_sort_value(keys[r]),
        reverse=not ascending,
    )

    table.setRowCount(0)
    table.setRowCount(row_count)
    for new_row, old_row in enumerate(order):
        for col, (item, widget) in enumerate(snapshot[old_row]):
            if item is not None:
                table.setItem(new_row, col, item)
            if widget is not None:
                table.setCellWidget(new_row, col, widget)

    _SORT_ASC[column] = not ascending
    resize_table_rows(table)


def enable_header_sort(table: QTableWidget) -> None:
    header = table.horizontalHeader()
    header.setSectionsClickable(True)
    header.sectionClicked.connect(lambda col: sort_table_by_column(table, col))


def prepare_data_table(table: QTableWidget, *, sortable: bool = True) -> None:
    table.setWordWrap(True)
    table.setTextElideMode(Qt.TextElideMode.ElideNone)
    table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    table.horizontalHeader().setDefaultAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    )
    if sortable:
        enable_header_sort(table)


def resize_table_rows(table: QTableWidget) -> None:
    table.resizeRowsToContents()


def compact_table_rows(table: QTableWidget, *, line_height: int = 26) -> None:
    table.setStyleSheet("QTableWidget::item { padding: 1px 4px; }")
    table.verticalHeader().setDefaultSectionSize(line_height)
    table.resizeRowsToContents()
    for row in range(table.rowCount()):
        lines = 1
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                lines = max(lines, item.text().count("\n") + 1)
        table.setRowHeight(row, line_height * lines + 2)


def table_fit_content(table: QTableWidget) -> None:
    resize_table_rows(table)
    total = table.horizontalHeader().height() + 4
    for row in range(table.rowCount()):
        total += table.rowHeight(row)
    table.setFixedHeight(max(total, 48))
    table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


def table_show_rows(table: QTableWidget, visible_rows: int = 8) -> None:
    resize_table_rows(table)
    header_h = table.horizontalHeader().height() + 4
    total = header_h
    if table.rowCount() == 0:
        total += 36
    else:
        for i in range(min(visible_rows, table.rowCount())):
            total += table.rowHeight(i)
    table.setMinimumHeight(total)
    table.setMaximumHeight(total)


def stretch_table(table: QTableWidget) -> None:
    # table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    header.setStretchLastSection(True)


def wrap_widget_scroll(inner: QWidget) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setWidget(inner)
    return scroll


def readonly_item(value, sort_value: Any = None) -> QTableWidgetItem:
    text = value if value not in (None, "") else "-"
    if isinstance(value, (datetime, date)):
        text = (
            value.strftime("%Y-%m-%d")
            if isinstance(value, date) and not isinstance(value, datetime)
            else value.strftime("%Y-%m-%d %H:%M:%S")
        )
        sort_value = value
    item = QTableWidgetItem(str(text))
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    if sort_value is not None:
        item.setData(Qt.ItemDataRole.UserRole, sort_value)
    return item
