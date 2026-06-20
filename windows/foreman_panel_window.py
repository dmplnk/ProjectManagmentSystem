from typing import Optional

from audit_service import log_data_change, log_data_declined
from ui_assets import apply_window_icon
from ui_theme import (
    configure_table,
    content_margins,
    create_panel_header,
    resize_table_rows,
    section_label,
    style_primary_button,
    style_secondary_button,
)
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)



class AddHoursDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить часы")
        self.resize(360, 140)
        self._hours_edit = QLineEdit()

        form = QFormLayout()
        form.addRow("Добавить часы:", self._hours_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self) -> dict:
        return {"hours": self._hours_edit.text().strip()}


class ForemanPanelWindow(QWidget):
    def __init__(self, db_connection, worker_id: int):
        super().__init__()
        self.db = db_connection
        self.worker_id = worker_id
        self.setWindowTitle("Панель бригадира")
        # self.resize(1500, 760)
        self._brigade_name = self._load_foreman_brigade_name()
        self._build_ui()
        apply_window_icon(self)
        self._populate_tasks_table()
        self.showMaximized()

    def _build_ui(self) -> None:
        root = QVBoxLayout()
        content_margins(root, 16, 12)
        root.addWidget(
            create_panel_header(
                "Панель бригадира",
                f"Бригада: {self._brigade_name}",
                on_logout=self._logout,
            )
        )
        root.addWidget(section_label("Задачи бригады"))

        self._tasks_table = QTableWidget()
        configure_table(self._tasks_table)
        self._tasks_table.setColumnCount(10)
        self._tasks_table.setHorizontalHeaderLabels(
            [
                "id",
                "Задача",
                "Проект",
                "Этап",
                "Начало задачи",
                "Оконочание задачи",
                "Сотрудник",
                "Часы работы",
                "Статус задачи",
                "worker_id"
            ]
        )
        self._tasks_table.setColumnHidden(9, True)
        self._tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._tasks_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tasks_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._tasks_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._tasks_table.verticalHeader().setVisible(False)
        self._tasks_table.setWordWrap(True)
        self._tasks_table.setColumnWidth(0, 55)
        self._tasks_table.setColumnWidth(1, 220)
        self._tasks_table.setColumnWidth(2, 220)
        self._tasks_table.setColumnWidth(3, 180)
        self._tasks_table.setColumnWidth(4, 150)
        self._tasks_table.setColumnWidth(5, 150)
        self._tasks_table.setColumnWidth(6, 220)
        self._tasks_table.setColumnWidth(7, 90)
        self._tasks_table.setColumnWidth(8, 120)
        root.addWidget(self._tasks_table)

        actions = QHBoxLayout()
        actions.addStretch()
        add_hours_btn = QPushButton("Добавить часы")
        style_primary_button(add_hours_btn)
        add_hours_btn.clicked.connect(self._on_add_hours)
        actions.addWidget(add_hours_btn)

        complete_btn = QPushButton("Завершить задачу")
        style_secondary_button(complete_btn)
        complete_btn.clicked.connect(self._on_complete_task)
        actions.addWidget(complete_btn)
        root.addLayout(actions)
        # root.addStretch(1)

        self.setLayout(root)

    def _logout(self):
        from audit_service import record_logout
        from windows.auth_window import AuthWindow

        username = self.db._active_config.get("user")
        if username:
            record_logout(self.db, username, "Выход (бригадир)")
        self._auth_window = AuthWindow()
        self._auth_window.showMaximized()
        self.close()

    def _selected_row_dict(self) -> Optional[dict]:
        rows = self._tasks_table.selectionModel().selectedRows()
        if not rows:
            return None
        r = rows[0].row()
        headers = [
            self._tasks_table.horizontalHeaderItem(c).text()
            if self._tasks_table.horizontalHeaderItem(c)
            else ""
            for c in range(self._tasks_table.columnCount())
        ]
        out = {}
        for c, key in enumerate(headers):
            item = self._tasks_table.item(r, c)
            out[key] = item.text() if item else ""
        return out

    def _populate_tasks_table(self) -> None:
        data = self.load_tasks()
        if data is None:
            data = []
        keys = [
            "id",
            "task",
            "project",
            "stage",
            "start",
            "end",
            "employee",
            "hours",
            "status",
            "worker_id"
        ]
        self._tasks_table.setRowCount(len(data))
        for r, row_data in enumerate(data):
            for c, key in enumerate(keys):
                if key == "end":  # Обработка даты окончания
                    end_date = row_data.get("end")
                    if end_date is None or str(end_date).strip() in ("None", ""):
                        display_value = " - "  # или "" — пустая строка
                    else:
                        display_value = str(end_date)
                    self._tasks_table.setItem(r, c, QTableWidgetItem(display_value))
                else:
                    self._tasks_table.setItem(
                        r, c, QTableWidgetItem(str(row_data.get(key, "")))
                    )

        QTimer.singleShot(0, self._after_table_update)

    def _after_table_update(self):
        resize_table_rows(self._tasks_table)
        header = self._tasks_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)


    def _load_foreman_brigade_name(self) -> str:
        con = self.db.connect()
        if not con:
            return "-"
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(
                """
                select b.name
                from brigade b
                join brigade_composition bc on bc.brigade_id = b.id
                where bc.worker_id = %s
                limit 1;
                """,
                (self.worker_id,),
            )
            row = cursor.fetchone()
            return row[0] if row else "-"
        except Exception:
            return "-"
        finally:
            if cursor:
                cursor.close()

    def _on_add_hours(self) -> None:
        row = self._selected_row_dict()
        print(row)
        if not row:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу.")
            return
        if str(row.get("Статус задачи", "")).strip() != "В работе":
            QMessageBox.warning(
                self,
                "Ошибка",
                "Добавлять часы можно только для задач со статусом «В работе».",
            )
            return
        dlg = AddHoursDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        self.save_hours(dlg.get_data())
        self._populate_tasks_table()

    def _on_complete_task(self) -> None:
        row = self._selected_row_dict()
        if not row:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу.")
            return
        if str(row.get("Статус задачи", "")).strip() != "В работе":
            QMessageBox.warning(self, "Ошибка", "Завершить можно только задачу со статусом «В работе».")
            return
        if not self._confirm(
            "Завершить задачу?",
            audit_decline_details=f"Отмена завершения задачи id={row.get('id')}",
        ):
            return
        self.complete_task(row)
        self._populate_tasks_table()

    def load_tasks(self):
        con = self.db.connect()
        if not con:
            return []
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(
                """
                select t.id, t.name, p.name, s.name, t.actual_start_datetime, t.actual_end_datetime,
                       concat(w.surname, ' ', w.name) as worker_name,
                       coalesce(sum(wl.hours_spent), 0) as hours_spent, t.status, wl.worker_id
                from work_log wl
                join worker w on wl.worker_id = w.id
                join task t on wl.task_id = t.id
                join project_stage ps on t.project_stage_id = ps.id
                join stage s on ps.stage_id = s.id
                join project p on ps.project_id = p.id
                where ps.brigade_id in (
                    select bc.brigade_id
                    from brigade_composition bc
                    where bc.worker_id = %s
                )
                group by t.id, t.name, p.name, s.name, t.actual_start_datetime, t.actual_end_datetime, worker_name, t.status, wl.worker_id
                order by field(t.status, 'В работе', 'Планируется', 'Завершена'), t.id;
                """,
                (self.worker_id,),
            )
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(
                    {
                        "id": row[0],
                        "task": row[1],
                        "project": row[2],
                        "stage": row[3],
                        "start": row[4],
                        "end": row[5],
                        "employee": row[6] if row[6] else "-",
                        "hours": row[7],
                        "status": row[8],
                        "worker_id": row[9],
                    }
                )
            return result
        except Exception as exc:
            print(f"Ошибка загрузки задач: {exc}")
            return []
        finally:
            if cursor:
                cursor.close()

    def save_hours(self, data: dict):
        row = self._selected_row_dict()
        if not row:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу.")
            return
        try:
            hours = float(data.get("hours", ""))
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Часы должны быть числом.")
            return
        if hours <= 0:
            QMessageBox.warning(self, "Ошибка", "Часы должны быть больше нуля.")
            return

        con = self.db.connect()
        if not con:
            return
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(
                """
                SELECT 1 
                FROM work_log 
                WHERE task_id = %s AND worker_id = %s AND work_date = CURDATE()
                """,
                (row.get("id"), row.get("worker_id"))
            )

            exists_today = cursor.fetchone() is not None

            if exists_today:
                cursor.execute(
                    """
                    UPDATE work_log 
                    SET hours_spent = COALESCE(hours_spent, 0) + %s 
                    WHERE task_id = %s AND worker_id = %s AND work_date = CURDATE()
                    """,
                    (hours, row.get("id"), row.get("worker_id"))
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO work_log (task_id, worker_id, hours_spent, work_date) 
                    VALUES (%s, %s, %s, CURDATE())
                    """,
                    (row.get("id"), row.get("worker_id"), hours)
                )
            con.commit()
            log_data_change(
                self.db,
                f"Добавлено {hours} ч. к задаче id={row.get('id')} "
                f"(сотрудник worker_id={row.get('worker_id')})",
            )
        except Exception as exc:
            con.rollback()
            log_data_change(
                self.db,
                f"Ошибка добавления часов к задаче id={row.get('id')}: {exc}",
                success=False,
            )
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось добавить часы: {exc}")
        finally:
            if cursor:
                cursor.close()

    def complete_task(self, row: dict):
        con = self.db.connect()
        if not con:
            return
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(
                "update task set status = 'Завершена', actual_end_datetime = coalesce(actual_end_datetime, now()) where id = %s;",
                (row.get("id"),),
            )
            con.commit()
            log_data_change(
                self.db,
                f"Завершена задача id={row.get('id')} «{row.get('task')}»",
            )
        except Exception as exc:
            con.rollback()
            log_data_change(
                self.db,
                f"Ошибка завершения задачи id={row.get('id')}: {exc}",
                success=False,
            )
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось завершить задачу: {exc}")
        finally:
            if cursor:
                cursor.close()

    def _confirm(self, text, audit_decline_details: Optional[str] = None):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Question)

        # Создаём кастомные кнопки с русским текстом
        yes_button = msg_box.addButton("Да", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.ButtonRole.NoRole)

        # Устанавливаем кнопку по умолчанию (активируется по Enter)
        msg_box.setDefaultButton(yes_button)
        # Кнопка для Esc
        msg_box.setEscapeButton(no_button)

        # Показываем диалог и ждём ответа
        msg_box.exec()

        clicked_button = msg_box.clickedButton()
        ok = clicked_button == yes_button
        if not ok and audit_decline_details:
            log_data_declined(self.db, audit_decline_details)
        return ok