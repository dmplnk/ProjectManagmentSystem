from PyQt6.QtCore import QTimer
from ui_assets import apply_window_icon
from ui_theme import (
    configure_table,
    content_margins,
    create_panel_header,
    resize_table_rows,
    section_label,
)
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class EmployeePanelWindow(QWidget):
    def __init__(self, db_connection, worker_id: int):
        super().__init__()
        self.db = db_connection
        self.worker_id = worker_id
        self.setWindowTitle("Панель сотрудника")
        # self.resize(1250, 700)
        self._build_ui()
        apply_window_icon(self)
        self._refresh_table()
        self.showMaximized()


    def _build_ui(self) -> None:
        layout = QVBoxLayout()
        content_margins(layout, 16, 12)
        layout.addWidget(
            create_panel_header(
                "Панель сотрудника",
                "Ваши задачи и отработанные часы",
                on_logout=self._logout,
            )
        )
        layout.addWidget(section_label("Мои задачи"))

        self._tasks_table = QTableWidget()
        configure_table(self._tasks_table)
        self._tasks_table.setColumnCount(5)
        self._tasks_table.setHorizontalHeaderLabels(
            ["Задача", "Проект", "Этап", "Статус задачи", "Часы работы"]
        )
        self._tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._tasks_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tasks_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._tasks_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._tasks_table.verticalHeader().setVisible(False)
        self._tasks_table.setWordWrap(True)
        self._tasks_table.setColumnWidth(0, 260)
        self._tasks_table.setColumnWidth(1, 260)
        self._tasks_table.setColumnWidth(2, 180)
        self._tasks_table.setColumnWidth(3, 120)
        self._tasks_table.setColumnWidth(4, 100)
        layout.addWidget(self._tasks_table)
        # layout.addStretch(1)

        self.setLayout(layout)

    def _logout(self):
        from audit_service import record_logout
        from windows.auth_window import AuthWindow

        username = self.db._active_config.get("user")
        if username:
            record_logout(self.db, username, "Выход (сотрудник)")
        self._auth_window = AuthWindow()
        self._auth_window.showMaximized()
        self.close()

    def _refresh_table(self) -> None:
        data = self.load_my_tasks()
        if data is None:
            data = []
        keys = ["task", "project", "stage", "status", "hours"]
        self._tasks_table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, key in enumerate(keys):
                self._tasks_table.setItem(
                    r, c, QTableWidgetItem(str(row.get(key, "")))
                )

        QTimer.singleShot(0, self._after_table_update)

    def _after_table_update(self):
        resize_table_rows(self._tasks_table)
        header = self._tasks_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)


    def load_my_tasks(self):
        if not self.worker_id:
            return []
        con = self.db.connect()
        if not con:
            return []
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(
                """
                select t.name, p.name, s.name, t.status, coalesce(sum(wl.hours_spent), 0) as hours_spent
                from task t
                join project_stage ps on ps.id = t.project_stage_id
                join project p on ps.project_id = p.id
                join stage s on s.id = ps.stage_id
                join work_log wl on wl.task_id = t.id
                where wl.worker_id = %s
                group by t.id, t.name, p.name, s.name, t.status
                order by field(t.status, 'В работе', 'Планируется', 'Завершена'), t.id;
                """,
                (self.worker_id,),
            )
            rows = cursor.fetchall()
            return [
                {"task": row[0], "project": row[1], "stage": row[2], "status": row[3], "hours": row[4]}
                for row in rows
            ]
        except Exception as exc:
            print(f"Ошибка загрузки задач сотрудника: {exc}")
            return []
        finally:
            if cursor:
                cursor.close()

