import os
from datetime import date, datetime
from typing import Optional
import re

from datetime import datetime

from PyQt6.QtCore import QDate, Qt, QTimer, QRect
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from config import DB_CONFIG, DBA_USER
from db import (
    APP_ROLE_LABELS,
    MANAGEABLE_APP_ROLES,
    MySQLConnection,
    app_role_from_specialty_name,
    role_label_from_specialty_name,
)
from cryptography.fernet import Fernet

from windows.manager_panel_window import (
    MaterialAddActualDialog,
    MaterialCreateDialog,
    MaterialEditDialog,
    ProjectFormDialog,
    StageCreateDialog,
    WorkerSelectDialog,
    _fmt,
)
from audit_service import (
    EVENT_LABELS,
    log_data_change,
    log_data_declined,
    record_logout,
    write_audit_event,
)
from ui_assets import apply_window_icon
from ui_tables import wrap_widget_scroll
from ui_theme import (
    configure_table,
    content_margins,
    create_panel_header,
    compact_table_rows,
    resize_table_rows,
    section_label,
    stretch_table,
    table_show_rows,
    style_compact_button,
    style_danger_button,
    style_primary_button,
    style_secondary_button,
)
from zabbix_client import ZabbixClient

PROJECT_STATUSES = ["Планируется", "В работе", "Завершен"]
STAGE_STATUSES = ["Планируется", "В работе", "Завершен"]
TASK_STATUSES = ["Планируется", "В работе", "Завершена"]


def _admin_confirm(
    parent,
    text: str,
    *,
    db=None,
    actor: Optional[str] = None,
    audit_decline_details: Optional[str] = None,
) -> bool:
    msg = QMessageBox(parent)
    msg.setWindowTitle("Подтверждение")
    msg.setText(text)
    msg.setIcon(QMessageBox.Icon.Question)
    yes_btn = msg.addButton("Да", QMessageBox.ButtonRole.YesRole)
    no_btn = msg.addButton("Нет", QMessageBox.ButtonRole.NoRole)
    msg.setDefaultButton(yes_btn)
    msg.setEscapeButton(no_btn)
    msg.exec()
    ok = msg.clickedButton() == yes_btn
    if not ok and db and audit_decline_details:
        log_data_declined(db, audit_decline_details, actor_username=actor)
    return ok


def _password_row_widget(line_edit: QLineEdit) -> QWidget:
    row = QWidget()
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(line_edit, 1)
    show_btn = QPushButton("Показать пароль")
    hide_btn = QPushButton("Скрыть пароль")
    style_compact_button(show_btn)
    style_compact_button(hide_btn)
    hide_btn.setVisible(False)

    def show_password():
        line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        show_btn.setVisible(False)
        hide_btn.setVisible(True)

    def hide_password():
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        hide_btn.setVisible(False)
        show_btn.setVisible(True)

    show_btn.clicked.connect(show_password)
    hide_btn.clicked.connect(hide_password)
    lay.addWidget(show_btn)
    lay.addWidget(hide_btn)
    return row


class AdminDbSession:

    def __init__(self, db: MySQLConnection, dba_user: str, dba_password: str):
        self.db = db
        self.dba_user = dba_user
        self.dba_password = dba_password
        self.ensure()

    def ensure(self):
        self.db.ensure_connection_user(self.dba_user, self.dba_password)


def _configure_readonly_table(table: QTableWidget, *, sortable: bool = True):
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    configure_table(table, sortable=sortable)


def _style_toolbar_button(button: QPushButton, label: str) -> None:
    if label == "Добавить":
        style_primary_button(button)
    elif label == "Удалить":
        style_danger_button(button)
    else:
        style_secondary_button(button)


def _readonly_item(value) -> QTableWidgetItem:
    item = QTableWidgetItem(_fmt(value))
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item


def _password_table_cell(password_stored: str) -> QWidget:
    cell = QWidget()
    layout = QHBoxLayout(cell)
    layout.setContentsMargins(4, 2, 4, 2)
    layout.setSpacing(6)
    label = QLabel("••••••••")
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    show_btn = QPushButton("Показать")
    hide_btn = QPushButton("Скрыть")
    style_compact_button(show_btn)
    style_compact_button(hide_btn)
    hide_btn.setVisible(False)
    stored = str(password_stored or "")

    def plain_text() -> str:
        if not stored:
            return "—"
        fernet = Fernet(os.getenv("FERNET_KEY").encode())

        if stored.startswith("gAAAAA"):
            return fernet.decrypt(stored.encode()).decode()
        return stored

    def on_show():
        label.setText(plain_text())
        show_btn.setVisible(False)
        hide_btn.setVisible(True)

    def on_hide():
        label.setText("••••••••")
        hide_btn.setVisible(False)
        show_btn.setVisible(True)

    show_btn.clicked.connect(on_show)
    hide_btn.clicked.connect(on_hide)
    layout.addWidget(label, 1)
    layout.addWidget(show_btn)
    layout.addWidget(hide_btn)
    return cell


class UserFormDialog(QDialog):
    def __init__(
        self,
        parent,
        workers_without_account: list[dict],
        initial: Optional[dict] = None,
        edit_mode: bool = False,
    ):
        super().__init__(parent)
        self._initial = initial or {}
        self._edit_mode = edit_mode
        self.setWindowTitle("Изменение пользователя" if edit_mode else "Добавление пользователя")

        self._login = QLineEdit(str(self._initial.get("username", "")))
        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.setPlaceholderText("Оставьте пустым, чтобы не менять" if edit_mode else "")

        self._worker = QComboBox()
        self._worker.addItem("— не привязан —", None)
        self._worker_specialties: dict = {}
        for w in workers_without_account:
            specialty = (w.get("specialty_name") or "").strip() or "—"
            self._worker.addItem(f"{w['full_name']} — {specialty}", w["worker_id"])
            self._worker_specialties[w["worker_id"]] = w.get("specialty_name")
        if edit_mode and self._initial.get("worker_id"):
            specialty = (self._initial.get("specialty_name") or "").strip() or "—"
            self._worker.addItem(
                f"{self._initial.get('full_name', f'Сотрудник #{self._initial['worker_id']}')} — {specialty}",
                self._initial["worker_id"],
            )
            self._worker_specialties[self._initial["worker_id"]] = self._initial.get(
                "specialty_name"
            )
            idx = self._worker.findData(self._initial["worker_id"])
            if idx >= 0:
                self._worker.setCurrentIndex(idx)
        if edit_mode:
            self._worker.setEnabled(False)

        self._role_hint = QLabel()
        self._role_hint.setObjectName("mutedHint")
        self._update_role_hint()
        if not edit_mode:
            self._worker.currentIndexChanged.connect(self._update_role_hint)

        form = QFormLayout()
        form.addRow("Логин:", self._login)
        form.addRow("Пароль:", _password_row_widget(self._password))
        if not edit_mode:
            form.addRow("Сотрудник:", self._worker)
            form.addRow("Роль:", self._role_hint)
        else:
            form.addRow("Сотрудник:", self._worker)
            form.addRow("Роль:", self._role_hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(buttons)

    def _resolve_app_role(self):
        worker_id = self._worker.currentData()
        if worker_id is None:
            return self._initial.get("app_role") if self._edit_mode else None
        return app_role_from_specialty_name(self._worker_specialties.get(worker_id))

    def _update_role_hint(self):
        app_role = self._resolve_app_role()
        if app_role:
            self._role_hint.setText(APP_ROLE_LABELS.get(app_role, app_role))
        else:
            self._role_hint.setText("не определена (выберите сотрудника)")

    def _on_save(self):
        if not self._login.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите логин.")
            return
        if not self._edit_mode and not self._password.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите пароль.")
            return
        if not self._edit_mode and self._worker.currentData() is None:
            QMessageBox.warning(self, "Ошибка", "Выберите сотрудника для новой учётной записи.")
            return
        self.accept()

    def get_data(self):
        return {
            "username": self._login.text().strip(),
            "password": self._password.text().strip(),
            "app_role": self._resolve_app_role(),
            "worker_id": self._worker.currentData(),
        }


class AdminTaskFormDialog(QDialog):
    def __init__(
        self,
        parent,
        workers: list[dict],
        initial: Optional[dict] = None,
        stage_planned_start: Optional[str] = None,
    ):
        super().__init__(parent)
        self._initial = initial or {}
        self._workers = workers
        self._worker_ids = []
        self._delete_requested = False
        self.setWindowTitle("Изменение задачи" if initial else "Добавление задачи")

        self._name = QLineEdit(str(self._initial.get("task_name", "")))
        self._description = QLineEdit(str(self._initial.get("task_description", "")))
        self._planned_start = QDateEdit()
        self._planned_end = QDateEdit()
        self._planned_start.setCalendarPopup(True)
        self._planned_end.setCalendarPopup(True)
        self._planned_start.setDisplayFormat("yyyy-MM-dd")
        self._planned_end.setDisplayFormat("yyyy-MM-dd")
        self._planned_start.setDate(QDate.currentDate())
        self._planned_end.setDate(QDate.currentDate())
        if stage_planned_start:
            min_qdate = QDate.fromString(str(stage_planned_start)[:10], "yyyy-MM-dd")
            if min_qdate.isValid():
                self._planned_start.setMinimumDate(min_qdate)
                self._planned_end.setMinimumDate(min_qdate)
        if self._initial.get("planned_start"):
            self._planned_start.setDate(
                QDate.fromString(str(self._initial["planned_start"])[:10], "yyyy-MM-dd")
            )
        if self._initial.get("planned_end"):
            self._planned_end.setDate(
                QDate.fromString(str(self._initial["planned_end"])[:10], "yyyy-MM-dd")
            )

        self._workers_label = QLabel("Сотрудники: не выбраны")
        self._pick_workers_btn = QPushButton("Выбрать сотрудников")
        self._pick_workers_btn.clicked.connect(self._pick_workers)

        self._status_combo = None
        form = QFormLayout()
        form.addRow("Название:", self._name)
        form.addRow("Описание:", self._description)
        form.addRow("Плановая дата начала:", self._planned_start)
        form.addRow("Плановая дата окончания:", self._planned_end)
        if initial:
            self._status_combo = QComboBox()
            for status in TASK_STATUSES:
                self._status_combo.addItem(status)
            idx = self._status_combo.findText(self._initial.get("task_status", "Планируется"))
            if idx >= 0:
                self._status_combo.setCurrentIndex(idx)
            form.addRow("Статус:", self._status_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(self._pick_workers_btn)
        root.addWidget(self._workers_label)
        if initial:
            delete_btn = QPushButton("Удалить задачу")
            delete_btn.clicked.connect(self._on_delete)
            root.addWidget(delete_btn)
        root.addWidget(buttons)

    def set_selected_workers(self, ids):
        self._worker_ids = ids
        self._workers_label.setText(f"Сотрудники: {len(ids)}")

    def _pick_workers(self):
        dlg = WorkerSelectDialog(self, self._workers, self._worker_ids)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.set_selected_workers(dlg.selected_ids())

    def _on_delete(self):
        self._delete_requested = True
        self.accept()

    def _on_save(self):
        if self._delete_requested:
            return
        if not self._name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название задачи.")
            return
        if not self._worker_ids:
            QMessageBox.warning(self, "Ошибка", "Сотрудники обязательны.")
            return
        if self._planned_start.date() > self._planned_end.date():
            QMessageBox.warning(self, "Ошибка", "План старт должен быть не позже план конца.")
            return
        self.accept()

    def get_data(self):
        status = self._status_combo.currentText() if self._status_combo else "Планируется"
        return {
            "name": self._name.text().strip(),
            "description": self._description.text().strip() or None,
            "planned_start": self._planned_start.date().toString("yyyy-MM-dd") + " 09:00:00",
            "planned_end": self._planned_end.date().toString("yyyy-MM-dd") + " 18:00:00",
            "worker_ids": self._worker_ids,
            "status": status,
        }


class AdminStageViewWidget(QWidget):
    def __init__(self, parent_dialog, stage: dict):
        super().__init__()
        self.dialog = parent_dialog
        self.stage = stage
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(2)
        root.setContentsMargins(4, 4, 4, 4)

        head = QHBoxLayout()
        head.addWidget(QLabel("Этап:"))
        head.addWidget(QLabel(str(self.stage["stage_name"])))
        head.addSpacing(20)
        self._status_combo = QComboBox()
        for s in STAGE_STATUSES:
            self._status_combo.addItem(s)
        idx = self._status_combo.findText(self.stage["stage_status"])
        if idx >= 0:
            self._status_combo.setCurrentIndex(idx)
        apply_btn = QPushButton("Применить статус")
        apply_btn.clicked.connect(self._apply_status)
        head.addWidget(QLabel("Статус:"))
        head.addWidget(self._status_combo)
        head.addWidget(apply_btn)
        head.addStretch()
        root.addLayout(head)
        root.addSpacing(12)

        dates_row = QHBoxLayout()
        plan_col = QVBoxLayout()
        plan_col.addWidget(QLabel(f"Плановая дата начала: {_fmt(self.stage['planned_start'])}"))
        plan_col.addWidget(QLabel(f"Плановая дата окончания: {_fmt(self.stage['planned_end'])}"))
        dates_row.addLayout(plan_col)
        dates_row.addSpacing(20)
        fact_col = QVBoxLayout()
        fact_col.addWidget(QLabel(f"Фактическая дата начала: {_fmt(self.stage['actual_start'])}"))
        fact_col.addWidget(QLabel(f"Фактическая дата окончания: {_fmt(self.stage['actual_end'])}"))
        dates_row.addLayout(fact_col)
        dates_row.addStretch()
        root.addLayout(dates_row)
        root.addSpacing(12)

        brig_row = QHBoxLayout()
        brig_row.addWidget(QLabel("Бригада:"))
        self.brigade_combo = QComboBox()
        for b in self.dialog.brigades:
            self.brigade_combo.addItem(str(b["name"]), b["id"])
        bidx = self.brigade_combo.findData(self.stage["brigade_id"])
        if bidx >= 0:
            self.brigade_combo.setCurrentIndex(bidx)
        self.brigade_combo.currentIndexChanged.connect(self._on_brigade_changed)
        brig_row.addWidget(self.brigade_combo)
        brig_row.addWidget(QLabel(f"Бригадир: {_fmt(self.stage.get('foreman_full_name'))}"))
        brig_row.addStretch()
        root.addLayout(brig_row)
        root.addSpacing(12)

        tasks_head = QHBoxLayout()
        tasks_head.addWidget(QLabel("Задачи"))
        plus_task = QPushButton("+")
        plus_task.clicked.connect(
            lambda: self.dialog.add_task(self.stage["project_stage_id"])
        )
        tasks_head.addWidget(plus_task)
        tasks_head.addStretch()
        root.addLayout(tasks_head)
        root.addWidget(self._tasks_table())
        root.addSpacing(12)

        mats_head = QHBoxLayout()
        mats_head.addWidget(QLabel("Материалы"))
        plus_mat = QPushButton("+")
        plus_mat.clicked.connect(
            lambda: self.dialog.add_material(self.stage["project_stage_id"])
        )
        mats_head.addWidget(plus_mat)
        mats_head.addStretch()
        root.addLayout(mats_head)
        root.addWidget(self._materials_table())

    def _apply_status(self):
        new_status = self._status_combo.currentText()
        self.dialog.set_stage_status(self.stage, new_status)

    def _tasks_table(self):
        table = QTableWidget()
        _configure_readonly_table(table)
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels(
            [
                "id", "Задача", "Описание", "Статус", "План дата начала",
                "Факт дата начала", "Сотрудники", "План дата окончания", "Факт дата окончания",
            ]
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        tasks = self.stage.get("tasks", [])
        table.setRowCount(len(tasks))
        for r, t in enumerate(tasks):
            values = [
                t.get("task_id"), t.get("task_name"), t.get("task_description"),
                t.get("task_status"), t.get("planned_start"), t.get("actual_start"),
                t.get("workers_assigned"), t.get("planned_end"), t.get("actual_end"),
            ]
            for c, v in enumerate(values):
                table.setItem(r, c, _readonly_item(v))
        table.itemDoubleClicked.connect(
            lambda item: self.dialog.edit_task(
                self.stage["project_stage_id"], table.item(item.row(), 0).text()
            )
        )
        compact_table_rows(table)
        return table

    def _materials_table(self):
        table = QTableWidget()
        _configure_readonly_table(table)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(
            ["Используемый материал", "Плановое количество", "Фактическое количество"]
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        materials = self.stage.get("materials", [])
        table.setRowCount(len(materials))
        for r, m in enumerate(materials):
            for c, v in enumerate(
                [m.get("material_name"), m.get("planned_quantity"), m.get("actual_quantity")]
            ):
                table.setItem(r, c, _readonly_item(v))
        stage = self.stage
        table.itemDoubleClicked.connect(
            lambda item: self.dialog.edit_material(
                stage["project_stage_id"], stage, item.row()
            )
        )
        compact_table_rows(table)
        return table

    def _on_brigade_changed(self):
        self.dialog.change_brigade(
            self.stage["project_stage_id"], self.brigade_combo.currentData()
        )


class AdminStagesDialog(QDialog):
    def __init__(self, parent, projects_tab: "AdminProjectsTab", project: dict):
        super().__init__(parent)
        self.projects_tab = projects_tab
        self.projects_tab.session.ensure()
        self.project = project
        self.brigades = projects_tab._fetch_all(
            "select id,name from brigade order by name;", as_dict=True
        )
        self.setWindowTitle(f"Этапы проекта {project.get('name')}")
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
        )
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self._suppress = False
        self.tabs.currentChanged.connect(self._on_tab_changed)
        root = QVBoxLayout(self)
        root.addWidget(self.tabs)
        self.reload()

    def reload(self, keep_tab=False):
        current_index = self.tabs.currentIndex() if keep_tab else 0
        self._suppress = True
        self.tabs.clear()
        self.stages = self.projects_tab.load_project_stages(self.project["project_id"])
        for st in self.stages:
            inner = AdminStageViewWidget(self, st)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(inner)
            self.tabs.addTab(scroll, f"{st['stage_name']} [{st['stage_status']}]")
        next_stage = self.projects_tab.get_next_missing_stage(self.project["project_id"])
        if next_stage:
            placeholder = QWidget()
            lay = QVBoxLayout(placeholder)
            lay.addWidget(QLabel(f"Создать этап: {next_stage['name']}"))
            lay.addStretch()
            self.tabs.addTab(placeholder, f"+ {next_stage['name']}")
        self._suppress = False
        if keep_tab and 0 <= current_index < self.tabs.count():
            self.tabs.setCurrentIndex(current_index)
        if not self.stages and next_stage:
            QTimer.singleShot(0, self._create_next_stage)

    def _on_tab_changed(self, index):
        if self._suppress or index < 0:
            return
        if index == self.tabs.count() - 1:
            if self.projects_tab.get_next_missing_stage(self.project["project_id"]):
                self._create_next_stage()

    def _create_next_stage(self):
        next_stage = self.projects_tab.get_next_missing_stage(self.project["project_id"])
        if not next_stage:
            return
        prev_end_rows = self.projects_tab._fetch_all(
            "select max(planned_end_date) from project_stage where project_id=%s;",
            (self.project["project_id"],),
        )
        min_start = (
            prev_end_rows[0][0].strftime("%Y-%m-%d")
            if prev_end_rows and prev_end_rows[0][0]
            else None
        )
        dlg = StageCreateDialog(self, next_stage["name"], self.brigades, min_start)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            self.reload()
            return
        actor = self.projects_tab.session.dba_user
        if not _admin_confirm(
            self,
            "Создать этап?",
            db=self.projects_tab.db,
            actor=actor,
            audit_decline_details=f"Отмена создания этапа «{next_stage['name']}»",
        ):
            self.reload()
            return
        data = dlg.get_data()
        ok = self.projects_tab._execute(
            """
            insert into project_stage(stage_id,project_id,planned_start_date,planned_end_date,status,brigade_id)
            values(%s,%s,%s,%s,'Планируется',%s);
            """,
            (
                next_stage["id"], self.project["project_id"],
                data["planned_start_date"], data["planned_end_date"], data["brigade_id"],
            ),
        )
        log_data_change(
            self.projects_tab.db,
            f"Этап «{next_stage['name']}» в проекте id={self.project['project_id']}",
            actor_username=actor,
            success=ok,
        )
        self.reload()

    def set_stage_status(self, stage, new_status: str):
        actor = self.projects_tab.session.dba_user
        if not _admin_confirm(
            self,
            f"Изменить статус этапа на «{new_status}»?",
            db=self.projects_tab.db,
            actor=actor,
            audit_decline_details=(
                f"Отмена смены статуса этапа «{stage['stage_name']}» на «{new_status}»"
            ),
        ):
            return
        sid = stage["project_stage_id"]
        if new_status == "В работе":
            ok = self.projects_tab._execute(
                "update project_stage set status=%s, actual_start_date=coalesce(actual_start_date,current_date()), "
                "actual_end_date=null where id=%s;",
                (new_status, sid),
            )
        elif new_status == "Завершен":
            ok = self.projects_tab._execute(
                "update project_stage set status=%s, actual_end_date=coalesce(actual_end_date,current_date()) "
                "where id=%s;",
                (new_status, sid),
            )
        else:
            ok = self.projects_tab._execute(
                "update project_stage set status=%s, actual_start_date=null, actual_end_date=null where id=%s;",
                (new_status, sid),
            )
        log_data_change(
            self.projects_tab.db,
            f"Этап id={sid} «{stage['stage_name']}»: статус → «{new_status}»",
            actor_username=actor,
            success=ok,
        )
        self.reload(keep_tab=True)

    def change_brigade(self, project_stage_id, brigade_id):
        actor = self.projects_tab.session.dba_user
        if not _admin_confirm(
            self,
            "Подтвердить смену бригады?",
            db=self.projects_tab.db,
            actor=actor,
            audit_decline_details=f"Отмена смены бригады на этапе id={project_stage_id}",
        ):
            self.reload(keep_tab=True)
            return
        ok = self.projects_tab._execute(
            "update project_stage set brigade_id=%s where id=%s;",
            (brigade_id, project_stage_id),
        )
        log_data_change(
            self.projects_tab.db,
            f"Смена бригады на этапе id={project_stage_id}",
            actor_username=actor,
            success=ok,
        )
        self.reload(keep_tab=True)

    def _get_stage(self, project_stage_id):
        for st in self.stages:
            if st["project_stage_id"] == project_stage_id:
                return st
        return {}

    def add_task(self, project_stage_id):
        stage = self._get_stage(project_stage_id)
        workers = self.projects_tab.load_workers_for_stage(project_stage_id)
        dlg = AdminTaskFormDialog(self, workers, stage_planned_start=stage.get("planned_start"))
        if workers:
            dlg.set_selected_workers([workers[0]["id"]])
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        actor = self.projects_tab.session.dba_user
        if not _admin_confirm(
            self,
            "Добавить задачу?",
            db=self.projects_tab.db,
            actor=actor,
            audit_decline_details="Отмена добавления задачи",
        ):
            return
        payload = dlg.get_data()
        self.projects_tab.create_task(project_stage_id, payload)
        log_data_change(
            self.projects_tab.db,
            f"Добавлена задача «{payload['name']}» на этапе id={project_stage_id}",
            actor_username=actor,
        )
        self.reload(keep_tab=True)

    def edit_task(self, project_stage_id, task_id_text):
        task_id = int(task_id_text)
        task = self.projects_tab.get_task(task_id)
        if not task:
            return
        stage = self._get_stage(project_stage_id)
        workers = self.projects_tab.load_workers_for_stage(project_stage_id)
        dlg = AdminTaskFormDialog(self, workers, task, stage_planned_start=stage.get("planned_start"))
        dlg.set_selected_workers(self.projects_tab.get_task_worker_ids(task_id))
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        actor = self.projects_tab.session.dba_user
        if dlg._delete_requested:
            if not _admin_confirm(
                self,
                "Удалить задачу?",
                db=self.projects_tab.db,
                actor=actor,
                audit_decline_details=f"Отмена удаления задачи id={task_id}",
            ):
                return
            self.projects_tab._execute("delete from work_log where task_id=%s;", (task_id,))
            ok = self.projects_tab._execute("delete from task where id=%s;", (task_id,))
            log_data_change(
                self.projects_tab.db,
                f"Удалена задача id={task_id}",
                actor_username=actor,
                success=ok,
            )
            self.reload(keep_tab=True)
            return
        if not _admin_confirm(
            self,
            "Сохранить изменения задачи?",
            db=self.projects_tab.db,
            actor=actor,
            audit_decline_details=f"Отмена изменения задачи id={task_id}",
        ):
            return
        payload = dlg.get_data()
        self.projects_tab.update_task(task_id, payload)
        log_data_change(
            self.projects_tab.db,
            f"Изменена задача id={task_id} «{payload['name']}»",
            actor_username=actor,
        )
        self.reload(keep_tab=True)

    def add_material(self, project_stage_id):
        all_materials = self.projects_tab._fetch_all(
            "select id,name from material order by name;", as_dict=True
        )
        used_rows = self.projects_tab._fetch_all(
            "select material_id from stage_material where project_stage_id=%s;",
            (project_stage_id,),
        )
        used_ids = {r[0] for r in used_rows}
        materials = [m for m in all_materials if m["id"] not in used_ids]
        if not materials:
            QMessageBox.information(self, "Информация", "Все материалы уже добавлены к этапу.")
            return
        dlg = MaterialCreateDialog(self, materials)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        actor = self.projects_tab.session.dba_user
        if not _admin_confirm(
            self,
            "Добавить материал?",
            db=self.projects_tab.db,
            actor=actor,
            audit_decline_details="Отмена добавления материала к этапу",
        ):
            return
        payload = dlg.get_data()
        ok = self.projects_tab._execute(
            "insert into stage_material(project_stage_id,material_id,planned_quantity,actual_quantity) "
            "values(%s,%s,%s,null);",
            (project_stage_id, payload["material_id"], payload["planned_quantity"]),
        )
        log_data_change(
            self.projects_tab.db,
            f"Материал id={payload['material_id']} на этапе id={project_stage_id}",
            actor_username=actor,
            success=ok,
        )
        self.reload(keep_tab=True)

    def edit_material(self, project_stage_id, stage, row_index):
        materials = stage.get("materials", [])
        if row_index < 0 or row_index >= len(materials):
            return
        material = materials[row_index]
        dlg = MaterialEditDialog(self, self.projects_tab, material)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        actor = self.projects_tab.session.dba_user
        if dlg._delete_requested:
            if not _admin_confirm(
                self,
                "Удалить материал из этапа?",
                db=self.projects_tab.db,
                actor=actor,
                audit_decline_details=(
                    f"Отмена удаления материала «{material.get('material_name')}»"
                ),
            ):
                return
            ok = self.projects_tab._execute(
                "delete from stage_material where id=%s;",
                (material["stage_material_id"],),
            )
            log_data_change(
                self.projects_tab.db,
                f"Удалён материал этапа id={material['stage_material_id']}",
                actor_username=actor,
                success=ok,
            )
            self.reload(keep_tab=True)
            return
        new_planned = dlg.get_planned_quantity()
        ok = self.projects_tab._execute(
            "update stage_material set planned_quantity=%s where id=%s;",
            (new_planned, material["stage_material_id"]),
        )
        log_data_change(
            self.projects_tab.db,
            f"Плановое кол-во материала id={material['stage_material_id']} → {new_planned}",
            actor_username=actor,
            success=ok,
        )
        self.reload(keep_tab=True)


class AdminProjectsTab(QWidget):
    def __init__(self, session: AdminDbSession):
        super().__init__()
        self.session = session
        self.db = session.db
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)
        self.projects_table = QTableWidget()
        _configure_readonly_table(self.projects_table, sortable=False)
        self.projects_table.setColumnCount(6)
        self.projects_table.setHorizontalHeaderLabels(
            ["Название", "Адрес", "Дата начала", "Дата окончания", "Статус", "Текущий этап"]
        )
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.projects_table.verticalHeader().setVisible(False)
        stretch_table(self.projects_table)
        root.addWidget(self.projects_table, 1)
        header = self.projects_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Даты — по содержимому
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        actions = QHBoxLayout()
        actions.addStretch(1)
        for text, slot in [
            ("Добавить", self._add_project),
            ("Изменить", self._edit_project),
            ("Удалить", self._delete_project),
        ]:
            btn = QPushButton(text)
            _style_toolbar_button(btn, text)
            btn.clicked.connect(slot)
            actions.addWidget(btn)
        root.addLayout(actions)

    def _fetch_all(self, query, params=(), as_dict=False):
        self.session.ensure()
        con = self.db.connect()
        if not con:
            return []
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            while cursor.nextset():
                pass
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

    def _execute(self, query, params=()):
        self.session.ensure()
        con = self.db.connect()
        if not con:
            return False
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(query, params)
            con.commit()
            return True
        except Exception as exc:
            print(f"Ошибка выполнения: {exc}")
            con.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def load_projects(self):
        return self._fetch_all(
            """
            select
                p.id as project_id, p.name, p.address, p.start_date, p.end_date, p.status,
                coalesce(
                    case
                        when p.status = 'Планируется' then '-'
                        when exists (
                            select 1 from project_stage ps2
                            where ps2.project_id = p.id and ps2.status = 'В работе'
                        ) then (
                            select concat(s.name, ' (', ps3.status, ')')
                            from project_stage ps3 join stage s on s.id = ps3.stage_id
                            where ps3.project_id = p.id and ps3.status = 'В работе' limit 1
                        )
                        else (
                            select concat(s.name, ' (', ps4.status, ')')
                            from project_stage ps4 join stage s on s.id = ps4.stage_id
                            where ps4.project_id = p.id and ps4.actual_end_date is not null
                            order by ps4.actual_end_date desc limit 1
                        )
                    end, '-'
                ) as stage_info
            from project p order by p.id;
            """,
            as_dict=True,
        )

    def _refresh(self):
        projects = self.load_projects()
        self.projects_table.setRowCount(len(projects))
        for r, p in enumerate(projects):
            self.projects_table.setItem(r, 0, _readonly_item(p["name"]))
            self.projects_table.setItem(r, 1, _readonly_item(p["address"]))
            self.projects_table.setItem(r, 2, _readonly_item(p["start_date"]))
            self.projects_table.setItem(r, 3, _readonly_item(p["end_date"]))
            self.projects_table.setItem(r, 4, _readonly_item(p["status"]))

            stage_w = QWidget()
            stage_l = QHBoxLayout(stage_w)
            stage_l.setContentsMargins(4, 2, 4, 2)
            stage_l.addWidget(QLabel(_fmt(p["stage_info"])), 1)
            plus = QPushButton("...")
            plus.clicked.connect(lambda _=False, project=p: self._open_stages(project))
            stage_l.addWidget(plus)
            self.projects_table.setCellWidget(r, 5, stage_w)
        QTimer.singleShot(0, lambda: resize_table_rows(self.projects_table))

    def _update_project_status(self, project, new_status: str) -> bool:
        pid = project["project_id"]
        if new_status == "В работе":
            return self._execute(
                "update project set status='В работе', start_date=coalesce(start_date,%s), end_date=null "
                "where id=%s;",
                (date.today().isoformat(), pid),
            )
        if new_status == "Завершен":
            return self._execute(
                "update project set status='Завершен', end_date=%s where id=%s;",
                (date.today().isoformat(), pid),
            )
        return self._execute(
            "update project set status='Планируется', start_date=null, end_date=null where id=%s;",
            (pid,),
        )

    def _apply_project_status(self, project, new_status: str):
        self.session.ensure()
        if new_status == project["status"]:
            return
        actor = self.session.dba_user
        if not _admin_confirm(
            self,
            f"Изменить статус проекта на «{new_status}»?",
            db=self.db,
            actor=actor,
            audit_decline_details=(
                f"Отмена смены статуса проекта «{project['name']}» на «{new_status}»"
            ),
        ):
            self._refresh()
            return
        ok = self._update_project_status(project, new_status)
        log_data_change(
            self.db,
            f"Проект id={project['project_id']} «{project['name']}»: статус → «{new_status}»",
            actor_username=actor,
            success=ok,
        )
        self._refresh()

    def _selected_project(self):
        rows = self.projects_table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        name = self.projects_table.item(row, 0).text()
        projects = self._fetch_all(
            "select id as project_id, name, address, start_date, end_date, status "
            "from project where name=%s limit 1;",
            (name,),
            as_dict=True,
        )
        return projects[0] if projects else None

    def _add_project(self):
        dlg = ProjectFormDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        actor = self.session.dba_user
        if not _admin_confirm(
            self,
            "Добавить проект?",
            db=self.db,
            actor=actor,
            audit_decline_details=f"Отмена создания проекта «{dlg.get_data()['name']}»",
        ):
            return
        payload = dlg.get_data()
        if not self._execute(
            "insert into project(name,address,start_date,end_date,status) values(%s,%s,NULL,%s,%s);",
            (payload["name"], payload["address"], None, payload["status"]),
        ):
            log_data_change(
                self.db,
                f"Ошибка создания проекта «{payload['name']}»",
                actor_username=actor,
                success=False,
            )
            return
        log_data_change(
            self.db,
            f"Создан проект «{payload['name']}»",
            actor_username=actor,
        )
        project_id = self._fetch_all("select id from project order by id desc limit 1;")[0][0]
        first_stage = self._fetch_all("select id,name from stage order by id limit 1;", as_dict=True)
        brigades = self._fetch_all("select id,name from brigade order by name;", as_dict=True)
        if first_stage:
            sdlg = StageCreateDialog(self, first_stage[0]["name"], brigades, None)
            if sdlg.exec() == QDialog.DialogCode.Accepted and _admin_confirm(self, "Создать первый этап?"):
                data = sdlg.get_data()
                self._execute(
                    """
                    insert into project_stage(stage_id,project_id,planned_start_date,planned_end_date,status,brigade_id)
                    values(%s,%s,%s,%s,'Планируется',%s);
                    """,
                    (
                        first_stage[0]["id"], project_id,
                        data["planned_start_date"], data["planned_end_date"], data["brigade_id"],
                    ),
                )
        self._refresh()

    def _edit_project(self):
        project = self._selected_project()
        if not project:
            QMessageBox.warning(self, "Изменение", "Выберите проект.")
            return
        dlg = ProjectFormDialog(self, project, allow_status_edit=True)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        actor = self.session.dba_user
        if not _admin_confirm(
            self,
            "Сохранить изменения проекта?",
            db=self.db,
            actor=actor,
            audit_decline_details=f"Отмена изменения проекта «{project['name']}»",
        ):
            return
        payload = dlg.get_data()
        ok = self._execute(
            "update project set name=%s, address=%s where id=%s;",
            (payload["name"], payload["address"], project["project_id"]),
        )
        if ok and payload["status"] != project["status"]:
            ok = self._update_project_status(
                {**project, "name": payload["name"]}, payload["status"]
            )
        log_data_change(
            self.db,
            f"Изменён проект id={project['project_id']}: «{payload['name']}», статус «{payload['status']}»",
            actor_username=actor,
            success=ok,
        )
        self._refresh()

    def _delete_project(self):
        project = self._selected_project()
        if not project:
            QMessageBox.warning(self, "Удаление", "Выберите проект.")
            return
        actor = self.session.dba_user
        if not _admin_confirm(
            self,
            "Удалить проект и все связанные данные?",
            db=self.db,
            actor=actor,
            audit_decline_details=f"Отмена удаления проекта «{project['name']}»",
        ):
            return
        pid = project["project_id"]
        for (sid,) in self._fetch_all(
            "select id from project_stage where project_id=%s;", (pid,)
        ):
            for (tid,) in self._fetch_all(
                "select id from task where project_stage_id=%s;", (sid,)
            ):
                self._execute("delete from work_log where task_id=%s;", (tid,))
            self._execute("delete from task where project_stage_id=%s;", (sid,))
            self._execute("delete from stage_material where project_stage_id=%s;", (sid,))
        self._execute("delete from project_stage where project_id=%s;", (pid,))
        ok = self._execute("delete from project where id=%s;", (pid,))
        log_data_change(
            self.db,
            f"Удалён проект id={pid} «{project['name']}»",
            actor_username=actor,
            success=ok,
        )
        self._refresh()

    def _open_stages(self, project):
        top = self.window()
        dlg = AdminStagesDialog(top, self, project)
        dlg.exec()
        self._refresh()

    def get_next_missing_stage(self, project_id):
        rows = self._fetch_all(
            """
            select s.id, s.name from stage s
            where s.id not in (
                select ps.stage_id from project_stage ps where ps.project_id=%s
            )
            order by s.id limit 1;
            """,
            (project_id,),
            as_dict=True,
        )
        return rows[0] if rows else None

    def load_project_stages(self, project_id):
        stages = self._fetch_all(
            """
            select
                ps.id as project_stage_id, ps.brigade_id, s.name as stage_name,
                ps.status as stage_status, ps.planned_start_date as planned_start,
                ps.planned_end_date as planned_end, ps.actual_start_date as actual_start,
                ps.actual_end_date as actual_end, b.name as brigade_name,
                (select concat(w.surname,' ',w.name,' ',ifnull(w.patronymic,''))
                 from worker w join brigade_composition bc on w.id=bc.worker_id
                 where bc.brigade_id=b.id and w.specialty_id=1 limit 1) as foreman_full_name
            from project_stage ps
            join stage s on ps.stage_id=s.id
            left join brigade b on ps.brigade_id=b.id
            where ps.project_id=%s
            order by ps.planned_start_date;
            """,
            (project_id,),
            as_dict=True,
        )
        for st in stages:
            sid = st["project_stage_id"]
            st["tasks"] = self._fetch_all(
                """
                select t.id as task_id, t.name as task_name, t.description as task_description,
                    t.status as task_status, t.planned_start_datetime as planned_start,
                    t.actual_start_datetime as actual_start, t.planned_end_datetime as planned_end,
                    t.actual_end_datetime as actual_end,
                    group_concat(distinct concat(w.surname,' ',w.name,' ',ifnull(w.patronymic,''))
                        order by w.surname separator '\n') as workers_assigned
                from task t
                left join work_log wl on wl.task_id=t.id
                left join worker w on w.id=wl.worker_id
                where t.project_stage_id=%s
                group by t.id,t.name,t.description,t.status,t.planned_start_datetime,
                    t.actual_start_datetime,t.planned_end_datetime,t.actual_end_datetime
                order by t.planned_start_datetime;
                """,
                (sid,),
                as_dict=True,
            )
            st["materials"] = self._fetch_all(
                """
                select sm.id as stage_material_id, sm.material_id, m.name as material_name,
                    sm.planned_quantity, sm.actual_quantity
                from stage_material sm join material m on m.id=sm.material_id
                where sm.project_stage_id=%s order by m.name;
                """,
                (sid,),
                as_dict=True,
            )
        return stages

    def load_workers_for_stage(self, project_stage_id):
        return self._fetch_all(
            """
            select w.id, concat(w.surname,' ',w.name,' ',ifnull(w.patronymic,'')) as worker_name
            from project_stage ps
            join brigade_composition bc on bc.brigade_id=ps.brigade_id
            join worker w on w.id=bc.worker_id
            where ps.id=%s order by w.surname, w.name;
            """,
            (project_stage_id,),
            as_dict=True,
        )

    def create_task(self, project_stage_id, payload):
        if not self._execute(
            """
            insert into task(name,description,project_stage_id,planned_start_datetime,planned_end_datetime,status)
            values(%s,%s,%s,%s,%s,%s);
            """,
            (
                payload["name"], payload["description"], project_stage_id,
                payload["planned_start"], payload["planned_end"], payload.get("status", "Планируется"),
            ),
        ):
            return
        task_id = self._fetch_all("select id from task order by id desc limit 1;")[0][0]
        for worker_id in payload["worker_ids"]:
            self._execute(
                "insert into work_log(task_id,worker_id,hours_spent,work_date) values(%s,%s,0,current_date());",
                (task_id, worker_id),
            )

    def get_task(self, task_id):
        rows = self._fetch_all(
            """
            select t.id as task_id, t.name as task_name, t.description as task_description,
                t.status as task_status, t.planned_start_datetime as planned_start,
                t.planned_end_datetime as planned_end
            from task t where t.id=%s limit 1;
            """,
            (task_id,),
            as_dict=True,
        )
        return rows[0] if rows else None

    def get_task_worker_ids(self, task_id):
        return [x[0] for x in self._fetch_all(
            "select distinct worker_id from work_log where task_id=%s;", (task_id,)
        )]

    def update_task(self, task_id, payload):
        self._execute(
            """
            update task set name=%s, description=%s, planned_start_datetime=%s, planned_end_datetime=%s
            where id=%s;
            """,
            (
                payload["name"], payload["description"],
                payload["planned_start"], payload["planned_end"], task_id,
            ),
        )
        status = payload.get("status", "Планируется")
        if status == "В работе":
            self._execute(
                "update task set status=%s, actual_start_datetime=coalesce(actual_start_datetime,now()), "
                "actual_end_datetime=null where id=%s;",
                (status, task_id),
            )
        elif status == "Завершена":
            self._execute(
                "update task set status=%s, actual_end_datetime=coalesce(actual_end_datetime,now()) where id=%s;",
                (status, task_id),
            )
        else:
            self._execute(
                "update task set status=%s, actual_start_datetime=null, actual_end_datetime=null where id=%s;",
                (status, task_id),
            )
        self._execute("delete from work_log where task_id=%s;", (task_id,))
        for worker_id in payload["worker_ids"]:
            self._execute(
                "insert into work_log(task_id,worker_id,hours_spent,work_date) values(%s,%s,0,current_date());",
                (task_id, worker_id),
            )


def _metric_stats(points: list[tuple[int, float]], unit: str = "") -> str:
    if not points:
        return "last: —  min: —  avg: —  max: —"
    values = [v for _, v in points]
    last_v = values[-1]
    min_v = min(values)
    max_v = max(values)
    avg_v = sum(values) / len(values)
    suffix = f" {unit}" if unit else ""
    return (
        f"last: {last_v:.2f}{suffix}  |  min: {min_v:.2f}{suffix}  |  "
        f"avg: {avg_v:.2f}{suffix}  |  max: {max_v:.2f}{suffix}"
    )


class _LineChartCanvas(QWidget):
    def __init__(self, points: list[tuple[int, float]], parent=None):
        super().__init__(parent)
        self._points = points
        self.setMinimumHeight(150)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(8, 8, -8, -8)
        painter.fillRect(rect, QColor(250, 252, 255))
        painter.setPen(QPen(QColor(200, 210, 220)))
        painter.drawRect(rect)

        if len(self._points) < 1:
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Нет данных за 24 ч")
            return

        values = [v for _, v in self._points]
        vmin, vmax = min(values), max(values)
        if vmax == vmin:
            vmax = vmin + 1.0

        chart = rect.adjusted(36, 10, -8, -22)
        painter.setPen(QPen(QColor(220, 225, 230)))
        for i in range(5):
            y = chart.top() + int(chart.height() * i / 4)
            painter.drawLine(chart.left(), y, chart.right(), y)

        n = len(self._points)
        pts = []
        for i, (_, val) in enumerate(self._points):
            x = chart.left() + int(chart.width() * i / max(n - 1, 1))
            y = chart.bottom() - int((val - vmin) / (vmax - vmin) * chart.height())
            pts.append((x, y))

        painter.setPen(QPen(QColor(30, 100, 200), 2))
        for i in range(1, len(pts)):
            painter.drawLine(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1])

        painter.setPen(QPen(QColor(30, 100, 200)))
        painter.setBrush(QColor(30, 100, 200))
        for x, y in pts:
            painter.drawEllipse(x - 2, y - 2, 4, 4)

        painter.setPen(QColor(80, 90, 100))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(
            QRect(rect.left(), rect.top(), 48, 18),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            f"{vmax:.1f}",
        )
        painter.drawText(
            QRect(rect.left(), rect.bottom() - 36, 48, 18),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
            f"{vmin:.1f}",
        )
        if self._points:
            t0 = datetime.fromtimestamp(self._points[0][0]).strftime("%d.%m %H:%M")
            t1 = datetime.fromtimestamp(self._points[-1][0]).strftime("%d.%m %H:%M")
            painter.drawText(
                chart.left(),
                rect.bottom() - 18,
                chart.width(),
                16,
                Qt.AlignmentFlag.AlignHCenter,
                f"{t0} — {t1}",
            )


class MetricChartCard(QWidget):
    def __init__(self, metric: dict, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        head = QLabel(f"{metric.get('title', '')}  [{metric.get('key', '')}]")
        head.setWordWrap(True)
        layout.addWidget(head)
        if metric.get("host"):
            layout.addWidget(QLabel(f"Хост Zabbix: {metric['host']}"))
        layout.addWidget(_LineChartCanvas(metric.get("points", [])))
        stats = QLabel(_metric_stats(metric.get("points", []), metric.get("unit", "")))
        stats.setWordWrap(True)
        stats.setObjectName("mutedHint")
        layout.addWidget(stats)


class AdminUsersTab(QWidget):
    def __init__(self, session: AdminDbSession):
        super().__init__()
        self.session = session
        self.db = session.db
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)
        self.table = QTableWidget()
        _configure_readonly_table(self.table, sortable=False)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ФИО", "Роль", "Логин", "Статус", "Пароль"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(self.table)

        actions = QHBoxLayout()
        for text, slot in [
            ("Добавить", self._add_user),
            ("Изменить", self._edit_user),
            ("Удалить", self._delete_user),
        ]:
            btn = QPushButton(text)
            _style_toolbar_button(btn, text)
            btn.clicked.connect(slot)
            actions.addWidget(btn)
        actions.addStretch()
        root.addLayout(actions)


        logs_title = section_label("Журнал событий")
        logs_title.setStyleSheet("padding: 0; margin: 0;")
        root.addWidget(logs_title)
        self.logs_table = QTableWidget()
        _configure_readonly_table(self.logs_table)
        self.logs_table.setColumnCount(4)
        self.logs_table.setHorizontalHeaderLabels(
            ["Время", "Событие", "Кто", "Детали"]
        )
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.logs_table.verticalHeader().setVisible(False)
        root.addWidget(self.logs_table)

        refresh_btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Обновить")
        _style_toolbar_button(refresh_btn, "Обновить")
        refresh_btn.clicked.connect(self.refresh)
        refresh_btn_layout.addWidget(refresh_btn)
        root.addLayout(refresh_btn_layout)

    def _fetch_all(self, query, params=(), as_dict=False):
        self.session.ensure()
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

    def _execute(self, query, params=()):
        self.session.ensure()
        con = self.db.connect()
        if not con:
            return False
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(query, params)
            con.commit()
            return True
        except Exception as exc:
            print(f"Ошибка выполнения: {exc}")
            con.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def load_users(self):
        self.session.ensure()
        rows = self._fetch_all(
            """
            select u.username, u.password, u.worker_id,
                concat(coalesce(w.surname,''),' ',coalesce(w.name,''),' ',coalesce(w.patronymic,'')) as full_name,
                coalesce(p.is_online, 0) as is_online,
                sp.name as specialty_name
            from users u
            left join worker w on w.id=u.worker_id
            left join specialty sp on sp.id=w.specialty_id
            left join user_presence p on p.user_id=u.id
            order by u.username;
            """,
            as_dict=True,
        )
        for row in rows:
            row["role_label"] = role_label_from_specialty_name(row.get("specialty_name"))
            row["full_name"] = (row.get("full_name") or "").strip() or "—"
        return rows

    def refresh(self):
        self.session.ensure()
        users = self.load_users()
        self._users_cache = users
        self.table.setRowCount(len(users))
        for r, u in enumerate(users):
            self.table.setItem(r, 0, _readonly_item(u["full_name"]))
            self.table.setItem(r, 1, _readonly_item(u.get("role_label", "не определена")))
            self.table.setItem(r, 2, _readonly_item(u["username"]))
            online = bool(u.get("is_online"))
            status_item = _readonly_item("Онлайн" if online else "Офлайн")
            status_item.setForeground(
                QColor(0, 140, 0) if online else QColor(160, 0, 0)
            )
            self.table.setItem(r, 3, status_item)
            self.table.setCellWidget(r, 4, _password_table_cell(u.get("password", "")))
        resize_table_rows(self.table)
        self.table.resizeRowsToContents()

        height = self.table.horizontalHeader().height()

        for row in range(self.table.rowCount()):
            height += self.table.rowHeight(row)

        height += 2 * self.table.frameWidth()

        self.table.setFixedHeight(height)
        self.refresh_logs()

    def refresh_logs(self):
        rows = self._fetch_all(
            """
            select event_time, event_type, actor_username, target_username, details, success
            from audit_log
            order by event_time desc
            limit 300;
            """,
            as_dict=True,
        )
        self.logs_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            et = row.get("event_type", "")
            event_label = EVENT_LABELS.get(et, et)
            t = row.get("event_time")
            if hasattr(t, "strftime"):
                t = t.strftime("%Y-%m-%d %H:%M:%S")
            self.logs_table.setItem(r, 0, _readonly_item(t))
            self.logs_table.setItem(r, 1, _readonly_item(event_label))
            self.logs_table.setItem(r, 2, _readonly_item(row.get("actor_username")))
            self.logs_table.setItem(r, 3, _readonly_item(row.get("details")))
        table_show_rows(self.logs_table, 8)

    def _selected_user(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        login = self.table.item(rows[0].row(), 2).text()
        return next((u for u in self._users_cache if u["username"] == login), None)

    def _workers_without_account(self):
        return self._fetch_all(
            """
            select w.id as worker_id,
                concat(w.surname,' ',w.name,' ',ifnull(w.patronymic,'')) as full_name,
                sp.name as specialty_name
            from worker w
            left join specialty sp on sp.id = w.specialty_id
            where w.id not in (select worker_id from users where worker_id is not null)
            order by w.surname, w.name;
            """,
            as_dict=True,
        )

    def _add_user(self):
        self.session.ensure()
        workers = self._workers_without_account()
        if not workers:
            QMessageBox.information(self, "Информация", "Нет сотрудников без учётной записи.")
            return
        dlg = UserFormDialog(self, workers)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        data = dlg.get_data()
        if not _admin_confirm(
            self,
            f"Создать пользователя «{data['username']}»?",
            db=self.db,
            actor=self.session.dba_user,
            audit_decline_details=f"Отмена создания пользователя «{data['username']}»",
        ):
            return
        try:
            self.session.ensure()
            self.db.create_mysql_account(data["username"], data["password"], data["app_role"])
            if not self._execute(
                "insert into users(username, password, worker_id) values(%s,%s,%s);",
                (data["username"], data["password"], data["worker_id"]),
            ):
                write_audit_event(
                    self.db,
                    "user_create",
                    actor_username=self.session.dba_user,
                    target_username=data["username"],
                    details="Не удалось сохранить в users",
                    success=False,
                )
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить в users.")
                return
        except RuntimeError as exc:
            write_audit_event(
                self.db,
                "user_create",
                actor_username=self.session.dba_user,
                target_username=data["username"],
                details=str(exc),
                success=False,
            )
            QMessageBox.critical(self, "Ошибка", str(exc))
            return
        write_audit_event(
            self.db,
            "user_create",
            actor_username=self.session.dba_user,
            target_username=data["username"],
            details=f"Роль: {data['app_role']}, worker_id: {data.get('worker_id')}",
        )
        QMessageBox.information(self, "Успех", "Пользователь создан.")
        self.refresh()

    def _edit_user(self):
        self.session.ensure()
        user = self._selected_user()
        if not user:
            QMessageBox.warning(self, "Изменение", "Выберите пользователя.")
            return
        user_for_form = dict(user)
        user_for_form["app_role"] = (
            app_role_from_specialty_name(user.get("specialty_name"))
            or self.db.get_mysql_role_for_login(user["username"])
        )
        dlg = UserFormDialog(self, [], user_for_form, edit_mode=True)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        data = dlg.get_data()
        old_login = user["username"]
        if not _admin_confirm(
            self,
            f"Сохранить изменения для «{old_login}»?",
            db=self.db,
            actor=self.session.dba_user,
            audit_decline_details=f"Отмена изменения пользователя «{old_login}»",
        ):
            return
        try:
            self.session.ensure()
            if data["username"] != old_login:
                self.db.rename_mysql_account(old_login, data["username"])
            if data["password"]:
                self.db.update_mysql_password(data["username"], data["password"])
                self._execute(
                    "update users set password=%s where username=%s;",
                    (data["password"], data["username"]),
                )
            old_role = self.db.get_mysql_role_for_login(old_login)
            if data["app_role"] and data["app_role"] != old_role:
                self.db.change_mysql_role(data["username"], data["app_role"])
            if data["username"] != old_login:
                self._execute(
                    "update users set username=%s where username=%s;",
                    (data["username"], old_login),
                )
        except RuntimeError as exc:
            write_audit_event(
                self.db,
                "user_update",
                actor_username=self.session.dba_user,
                target_username=data["username"],
                details=str(exc),
                success=False,
            )
            QMessageBox.critical(self, "Ошибка", str(exc))
            return
        write_audit_event(
            self.db,
            "user_update",
            actor_username=self.session.dba_user,
            target_username=data["username"],
            details=f"Логин был: {old_login}; роль: {data['app_role']}",
        )
        QMessageBox.information(self, "Успех", "Данные обновлены.")
        self.refresh()

    def _delete_user(self):
        self.session.ensure()
        user = self._selected_user()
        if not user:
            QMessageBox.warning(self, "Удаление", "Выберите пользователя.")
            return
        if not _admin_confirm(
            self,
            f"Удалить пользователя «{user['username']}»?",
            db=self.db,
            actor=self.session.dba_user,
            audit_decline_details=f"Отмена удаления пользователя «{user['username']}»",
        ):
            return
        try:
            self.session.ensure()
            self.db.drop_mysql_account(user["username"])
            self._execute("delete from users where username=%s;", (user["username"],))
        except RuntimeError as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
            return
        write_audit_event(
            self.db,
            "user_delete",
            actor_username=self.session.dba_user,
            target_username=user["username"],
        )
        QMessageBox.information(self, "Успех", "Пользователь удалён.")
        self.refresh()


class AdminTimeTab(QWidget):

    def __init__(self, session: AdminDbSession):
        super().__init__()
        self.session = session
        self.db = session.db
        self._rows_cache: list[dict] = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)
        title = QLabel("Учёт рабочего времени")
        title.setObjectName("sectionTitle")
        title.setStyleSheet("padding: 0; margin: 0;")
        root.addWidget(title)

        self.table = QTableWidget()
        _configure_readonly_table(self.table)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                "ID задачи",
                "Задача",
                "Проект",
                "Этап",
                "Сотрудник",
                "Статус",
                "Часы",
                "worker_id",
            ]
        )
        self.table.setColumnHidden(7, True)
        self.table.verticalHeader().setVisible(False)
        stretch_table(self.table)
        root.addWidget(self.table, 1)

        actions = QHBoxLayout()
        actions.addStretch()
        add_btn = QPushButton("Добавить часы")
        style_primary_button(add_btn)
        add_btn.clicked.connect(self._add_hours)
        actions.addWidget(add_btn)
        edit_btn = QPushButton("Изменить часы")
        style_secondary_button(edit_btn)
        edit_btn.clicked.connect(self._edit_hours)
        actions.addWidget(edit_btn)
        root.addLayout(actions)

    def _fetch_all(self, query, params=(), as_dict=False):
        self.session.ensure()
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

    def _execute(self, query, params=()):
        self.session.ensure()
        con = self.db.connect()
        if not con:
            return False
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(query, params)
            con.commit()
            return True
        except Exception as exc:
            print(f"Ошибка выполнения: {exc}")
            con.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def load_rows(self):
        return self._fetch_all(
            """
            select
                t.id as task_id,
                t.name as task_name,
                p.name as project_name,
                s.name as stage_name,
                concat(w.surname, ' ', w.name, ' ', ifnull(w.patronymic, '')) as worker_name,
                t.status as task_status,
                coalesce(wl.hours_spent, 0) as hours,
                wl.worker_id,
                wl.id as work_log_id,
                wl.work_date
            from work_log wl
            join worker w on w.id = wl.worker_id
            join task t on t.id = wl.task_id
            join project_stage ps on ps.id = t.project_stage_id
            join stage s on s.id = ps.stage_id
            join project p on p.id = ps.project_id
            order by p.name, s.name, t.name, w.surname;
            """,
            as_dict=True,
        )

    def refresh(self):
        self._rows_cache = self.load_rows()
        self.table.setRowCount(len(self._rows_cache))
        for r, row in enumerate(self._rows_cache):
            self.table.setItem(r, 0, _readonly_item(row.get("task_id")))
            self.table.setItem(r, 1, _readonly_item(row.get("task_name")))
            self.table.setItem(r, 2, _readonly_item(row.get("project_name")))
            self.table.setItem(r, 3, _readonly_item(row.get("stage_name")))
            self.table.setItem(r, 4, _readonly_item(row.get("worker_name")))
            self.table.setItem(r, 5, _readonly_item(row.get("task_status")))
            self.table.setItem(r, 6, _readonly_item(row.get("hours")))
            self.table.setItem(r, 7, _readonly_item(row.get("worker_id")))
        resize_table_rows(self.table)

    def _selected_row(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        idx = rows[0].row()
        if 0 <= idx < len(self._rows_cache):
            return self._rows_cache[idx]
        return None

    def _add_hours(self):
        from windows.foreman_panel_window import AddHoursDialog

        row = self._selected_row()
        if not row:
            QMessageBox.warning(self, "Учёт времени", "Выберите строку в таблице.")
            return
        dlg = AddHoursDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            hours = float(dlg.get_data().get("hours", ""))
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Часы должны быть числом.")
            return
        if hours <= 0:
            QMessageBox.warning(self, "Ошибка", "Часы должны быть больше нуля.")
            return
        wl_id = row.get("work_log_id")
        if wl_id:
            self._execute(
                "update work_log set hours_spent = coalesce(hours_spent, 0) + %s where id = %s;",
                (hours, wl_id),
            )
        else:
            self._execute(
                """
                insert into work_log (task_id, worker_id, hours_spent, work_date)
                values (%s, %s, %s, curdate());
                """,
                (row["task_id"], row["worker_id"], hours),
            )
        log_data_change(
            self.db,
            f"Добавлено {hours} ч. (задача id={row['task_id']})",
            actor_username=self.session.dba_user,
        )
        self.refresh()

    def _edit_hours(self):
        row = self._selected_row()
        if not row:
            QMessageBox.warning(self, "Учёт времени", "Выберите строку.")
            return
        from PyQt6.QtWidgets import QInputDialog

        value, ok = QInputDialog.getDouble(
            self,
            "Изменить часы",
            "Новое значение часов:",
            float(row.get("hours") or 0),
            0,
            100000,
            2,
        )
        if not ok:
            return
        wl_id = row.get("work_log_id")
        if not wl_id:
            QMessageBox.warning(self, "Ошибка", "Запись work_log не найдена.")
            return
        if self._execute(
            "update work_log set hours_spent=%s where id=%s;",
            (value, wl_id),
        ):
            log_data_change(
                self.db,
                f"Часы изменены на {value} (work_log id={wl_id})",
                actor_username=self.session.dba_user,
            )
        self.refresh()


class AdminSystemTab(QWidget):
    def __init__(self, session: AdminDbSession):
        super().__init__()
        self.session = session
        self.db = session.db
        self._stat_labels = {}
        self._info_label = QLabel("")
        self._zabbix_status = QLabel("")
        self._stats_error = QLabel("")
        self._build_ui()
        self.refresh()
        QTimer.singleShot(0, self._load_zabbix)

    def _build_ui(self):
        root = QVBoxLayout(self)
        content_margins(root, 12, 10)

        top = QHBoxLayout()
        self._info_label.setWordWrap(True)
        self._info_label.setObjectName("mutedHint")
        top.addWidget(self._info_label, 1)
        refresh_btn = QPushButton("Обновить")
        style_secondary_button(refresh_btn)
        refresh_btn.clicked.connect(self.refresh)
        top.addWidget(refresh_btn)
        root.addLayout(top)

        self._stats_line = QLabel("...")
        self._stats_line.setWordWrap(True)
        root.addWidget(self._stats_line)

        self._stats_error.setObjectName("errorText")
        self._stats_error.setWordWrap(True)
        root.addWidget(self._stats_error)

        self._zabbix_status = QLabel("Zabbix: загрузка…")
        self._zabbix_status.setWordWrap(True)
        root.addWidget(self._zabbix_status)

        self._zabbix_mysql_scroll = QScrollArea()
        self._zabbix_mysql_scroll.setWidgetResizable(True)
        self._zabbix_mysql_container = QWidget()
        self._zabbix_mysql_layout = QVBoxLayout(self._zabbix_mysql_container)
        self._zabbix_mysql_scroll.setWidget(self._zabbix_mysql_container)
        root.addWidget(self._zabbix_mysql_scroll, 1)

    def _fetch_scalar(self, query):
        self.session.ensure()
        con = self.db.connect()
        if not con:
            return None, "Нет подключения к БД"
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            return (row[0] if row else 0), None
        except Exception as exc:
            return None, str(exc)
        finally:
            if cursor:
                cursor.close()

    def refresh(self):
        self.session.ensure()
        self._stats_error.setText("")
        version, ver_err = self._fetch_scalar("select version();")
        self._info_label.setText(
            f"БД { _fmt(DB_CONFIG.get('database')) } @ { _fmt(DB_CONFIG.get('host')) }  |  "
            f"подключение: { _fmt(self.db._active_config.get('user')) }  |  "
            f"MySQL { _fmt(version) }"
        )
        if ver_err:
            self._stats_error.setText(ver_err)
        stat_parts = []
        errors = []
        labels = {
            "users": "пользователей",
            "workers": "сотрудников",
            "projects": "проектов",
            "stages": "этапов",
            "tasks": "задач",
            "materials": "материалов",
        }
        queries = {
            "users": "select count(*) from users;",
            "workers": "select count(*) from worker;",
            "projects": "select count(*) from project;",
            "stages": "select count(*) from project_stage;",
            "tasks": "select count(*) from task;",
            "materials": "select count(*) from material;",
        }
        for key, query in queries.items():
            val, err = self._fetch_scalar(query)
            if err:
                errors.append(labels[key])
            else:
                stat_parts.append(f"{labels[key]}: {val if val is not None else 0}")
        self._stats_line.setText("  ·  ".join(stat_parts) if stat_parts else "—")
        self._load_zabbix()
        if errors:
            self._stats_error.setText("Ошибка подсчёта: " + ", ".join(errors))

    def _clear_mysql_charts(self):
        while self._zabbix_mysql_layout.count():
            item = self._zabbix_mysql_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _render_mysql_metrics(self, metrics: list[dict]):
        self._clear_mysql_charts()
        if not metrics:
            self._zabbix_mysql_layout.addWidget(
                QLabel("Нет метрик MySQL за последние 24 часа.")
            )
            return
        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        for i, metric in enumerate(metrics):
            grid.addWidget(MetricChartCard(metric), i // 2, i % 2)
        self._zabbix_mysql_layout.addWidget(grid_host)
        self._zabbix_mysql_layout.addStretch()

    def _load_zabbix(self):
        client = ZabbixClient()
        if not client.is_configured():
            self._zabbix_status.setText(
                "Zabbix: не настроен (укажите ZABBIX_URL, ZABBIX_USER, ZABBIX_PASSWORD в .env)."
            )
            self._clear_mysql_charts()
            return
        try:
            metrics = client.fetch_mysql_metrics_last_day()
        except RuntimeError as exc:
            self._zabbix_status.setText(f"Zabbix: ошибка — {exc}")
            self._clear_mysql_charts()
            return
        self._zabbix_status.setText(
            f"Zabbix: метрики MySQL за 24 ч, {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        self._render_mysql_metrics(metrics)


class AdminPanelWindow(QWidget):

    def __init__(self, db_connection: MySQLConnection, dba_user: str, dba_password: str):
        super().__init__()
        self.db = db_connection
        self.session = AdminDbSession(self.db, dba_user, dba_password)
        self.setWindowTitle("Панель администратора")
        self._build_ui()
        apply_window_icon(self)
        self.showMaximized()

    def _build_ui(self):
        root = QVBoxLayout(self)
        content_margins(root, 16, 12)
        root.addWidget(
            create_panel_header(
                "Панель администратора",
                f"Подключение к БД: {self.session.dba_user}",
                on_logout=self._logout,
            )
        )

        tabs = QTabWidget()
        tabs.addTab(AdminProjectsTab(self.session), "Проекты")
        tabs.addTab(AdminTimeTab(self.session), "Учёт времени")
        tabs.addTab(wrap_widget_scroll(AdminUsersTab(self.session)), "Пользователи")
        tabs.addTab(wrap_widget_scroll(AdminSystemTab(self.session)), "Система")
        tabs.currentChanged.connect(lambda _: self.session.ensure())
        root.addWidget(tabs, 1)

    def _logout(self):
        from windows.auth_window import AuthWindow

        record_logout(
            self.db,
            self.session.dba_user,
            "Выход из панели администратора",
        )
        self._auth_window = AuthWindow()
        self._auth_window.showMaximized()
        self.close()
