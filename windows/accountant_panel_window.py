from PyQt6.QtCore import QDate, QTimer
from ui_assets import apply_window_icon
from ui_theme import (
    configure_table,
    content_margins,
    create_panel_header,
    resize_table_rows,
    section_label,
    stretch_table,
    style_primary_button,
)
from windows.report_dialogs import AccountantReportDialog
from PyQt6.QtWidgets import (
    QDateEdit,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class AccountantPanelWindow(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.setWindowTitle("Панель бухгалтера")
        self._build_ui()
        apply_window_icon(self)
        self._load_employees()
        self._employee_combo.setCurrentIndex(0)
        self._set_default_dates()
        self._refresh()
        self.showMaximized()

    def _build_ui(self) -> None:
        root = QVBoxLayout()
        content_margins(root, 16, 12)
        root.addWidget(
            create_panel_header(
                "Панель бухгалтера",
                "Отчёт по отработанным часам",
                on_logout=self._logout,
            )
        )

        period_row = QHBoxLayout()
        period_row.addWidget(QLabel("Период: дата от"))
        self._date_from = QDateEdit()
        self._date_from.setCalendarPopup(True)
        self._date_from.setDisplayFormat("dd.MM.yyyy")
        self._date_from.setDate(QDate.currentDate().addMonths(-1))
        period_row.addWidget(self._date_from)
        period_row.addWidget(QLabel("дата до"))
        self._date_to = QDateEdit()
        self._date_to.setCalendarPopup(True)
        self._date_to.setDisplayFormat("dd.MM.yyyy")
        self._date_to.setDate(QDate.currentDate())
        period_row.addWidget(self._date_to)
        period_row.addStretch()
        root.addLayout(period_row)

        emp_row = QHBoxLayout()
        emp_row.addWidget(QLabel("Сотрудник:"))
        self._employee_combo = QComboBox()
        emp_row.addWidget(self._employee_combo, stretch=1)
        root.addLayout(emp_row)

        root.addWidget(section_label("Детализация по задачам"))

        self._report_table = QTableWidget()
        configure_table(self._report_table)
        self._report_table.setColumnCount(6)
        self._report_table.setHorizontalHeaderLabels(
            ["Сотрудник", "Проект", "Этап", "Задача", "Часы", "Дата"]
        )
        self._report_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._report_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._report_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._report_table.verticalHeader().setVisible(False)
        self._report_table.setWordWrap(True)
        stretch_table(self._report_table)
        root.addWidget(self._report_table, 1)

        bottom = QHBoxLayout()
        self._total_label = QLabel("Всего часов: …")
        self._total_label.setObjectName("metricValue")
        bottom.addWidget(self._total_label)
        bottom.addStretch()
        report_btn = QPushButton("Сформировать отчёт")
        style_primary_button(report_btn)
        report_btn.clicked.connect(self._open_report_dialog)
        bottom.addWidget(report_btn)
        root.addLayout(bottom)

        self.setLayout(root)

        self._date_from.dateChanged.connect(self._refresh)
        self._date_to.dateChanged.connect(self._refresh)
        self._employee_combo.currentIndexChanged.connect(self._refresh)

    def _open_report_dialog(self):
        dlg = AccountantReportDialog(self, self)
        dlg.exec()

    def _logout(self):
        from audit_service import record_logout
        from windows.auth_window import AuthWindow

        username = self.db._active_config.get("user")
        if username:
            record_logout(self.db, username, "Выход (бухгалтер)")
        self._auth_window = AuthWindow()
        self._auth_window.showMaximized()
        self.close()

    def _period_filters(self) -> dict:
        return {
            "date_from": self._date_from.date().toString("yyyy-MM-dd"),
            "date_to": self._date_to.date().toString("yyyy-MM-dd"),
            "employee": self._employee_combo.currentData(),
        }

    def _refresh(self) -> None:
        data = self.load_data(self._period_filters())
        if data is None:
            data = []
        keys = ["employee", "project", "stage", "task", "hours", "date"]
        self._report_table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, key in enumerate(keys):
                self._report_table.setItem(
                    r, c, QTableWidgetItem(str(row.get(key, "")))
                )
        QTimer.singleShot(0, self._after_table_update)
        total = self.load_total_hours(self._period_filters())
        if total is None:
            self._total_label.setText("Всего часов: …")
        else:
            self._total_label.setText(f"Всего часов: {total}")

    def _after_table_update(self):
        resize_table_rows(self._report_table)

    def _fetch_all(self, query, params=(), as_dict=False):
        con = self.db.connect()
        if not con:
            return []
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            if not as_dict:
                return rows
            columns = [c[0] for c in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except Exception as exc:
            print(f"Ошибка запроса: {exc}")
            return []
        finally:
            if cursor:
                cursor.close()

    def load_data(self, filter):
        con = self.db.connect()
        if not con:
            return []
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(
                """
                SELECT 
                    CONCAT(w.surname, ' ', w.name) AS worker_name,
                    p.name AS project,
                    s.name AS stage_name,
                    t.name AS task,
                    wl.hours_spent,
                    wl.work_date
                FROM work_log wl
                JOIN task t ON wl.task_id = t.id
                JOIN project_stage ps ON t.project_stage_id = ps.id
                JOIN stage s ON ps.stage_id = s.id
                JOIN project p ON ps.project_id = p.id
                JOIN worker w ON wl.worker_id = w.id
                WHERE (%s IS NULL OR w.id = %s)
                AND wl.work_date BETWEEN 
                    COALESCE(%s, (SELECT MIN(work_date) FROM work_log))
                    AND
                    COALESCE(%s, (SELECT MAX(work_date) FROM work_log))
                ORDER BY work_date DESC;
                """,
                (filter["employee"], filter["employee"], filter["date_from"], filter["date_to"],),
            )
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(
                    {
                        "employee": row[0],
                        "project": row[1],
                        "stage": row[2],
                        "task": row[3],
                        "hours": row[4],
                        "date": row[5],
                    }
                )
            return result
        except Exception as exc:
            print(f"Ошибка загрузки данных: {exc}")
            return []
        finally:
            if cursor:
                cursor.close()

    def _load_employees(self):
        con = self.db.connect()
        if not con:
            return

        cursor = con.cursor()
        cursor.execute("""
            SELECT DISTINCT 
                w.id, 
                CONCAT(w.surname, ' ', w.name) AS worker_name
            FROM worker w
            JOIN work_log wl ON wl.worker_id = w.id
            ORDER BY worker_name;
        """)

        self._employee_combo.addItem("Все", None)

        for emp_id, name in cursor.fetchall():
            self._employee_combo.addItem(name, emp_id)

        cursor.close()

    def _set_default_dates(self):
        con = self.db.connect()
        if not con:
            return

        cursor = con.cursor()
        cursor.execute("SELECT MIN(work_date), MAX(work_date) FROM work_log")
        result = cursor.fetchone()

        if result:
            min_date, max_date = result
            if min_date:
                self._date_from.setDate(QDate.fromString(str(min_date), "yyyy-MM-dd"))
            if max_date:
                self._date_to.setDate(QDate.fromString(str(max_date), "yyyy-MM-dd"))

        cursor.close()

    def load_total_hours(self, filters: dict):
        con = self.db.connect()
        if not con:
            return None

        cursor = con.cursor()
        try:
            cursor.execute(
                """
                SELECT SUM(wl.hours_spent)
                FROM work_log wl
                JOIN worker w ON wl.worker_id = w.id
                WHERE (%s IS NULL OR w.id = %s)
                AND wl.work_date BETWEEN %s AND %s
                """,
                (
                    filters["employee"],
                    filters["employee"],
                    filters["date_from"],
                    filters["date_to"],
                ),
            )
            result = cursor.fetchone()
            return result[0] if result and result[0] else 0
        finally:
            cursor.close()
