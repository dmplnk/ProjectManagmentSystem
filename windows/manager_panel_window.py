from datetime import date, datetime
from typing import Optional
import re

from PyQt6.QtCore import QDate, Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
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
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from audit_service import log_data_change, log_data_declined
from ui_assets import apply_window_icon
from ui_theme import (
    configure_table,
    content_margins,
    create_panel_header,
    compact_table_rows,
    resize_table_rows,
    section_label,
    style_danger_button,
    style_primary_button,
    style_secondary_button,
)
from windows.report_dialogs import ManagerReportDialog

PROJECT_STATUSES = ["Планируется", "В работе", "Завершен"]


def _fmt(value):
    if value in (None, ""):
        return "-"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


class ProjectFormDialog(QDialog):
    def __init__(
        self,
        parent=None,
        initial: Optional[dict] = None,
        allow_status_edit: bool = False,
    ):
        super().__init__(parent)
        self._initial = initial or {}
        self._allow_status_edit = allow_status_edit
        self.setWindowTitle("Изменение проекта" if initial else "Добавление проекта")
        self.resize(400, 200)

        self._name = QLineEdit(str(self._initial.get("name", "")))
        self._address = QLineEdit(str(self._initial.get("address", "")))
        if allow_status_edit:
            self._status = QComboBox()
            for s in PROJECT_STATUSES:
                self._status.addItem(s)
            idx = self._status.findText(str(self._initial.get("status", "Планируется")))
            if idx >= 0:
                self._status.setCurrentIndex(idx)
        else:
            self._status = QLabel(str(self._initial.get("status", "Планируется")))

        form = QFormLayout()
        form.addRow("Название:", self._name)
        form.addRow("Адрес:", self._address)
        form.addRow("Статус:", self._status)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(buttons)

    def _on_save(self):
        if not self._name.text().strip() or not self._address.text().strip():
            QMessageBox.warning(self, "Ошибка", "Название и адрес обязательны.")
            return
        if not re.match(r"^\s*[^,]+,\s*[^,]+,\s*[^,]+\s*$", self._address.text().strip()):
            QMessageBox.warning(self, "Ошибка", "Адрес должен быть в формате: Город, Улица, Дом.")
            return
        self.accept()

    def get_data(self):
        if self._allow_status_edit:
            status = self._status.currentText()
        else:
            status = self._status.text() if hasattr(self._status, "text") else str(self._status)
        return {
            "name": self._name.text().strip(),
            "address": self._address.text().strip(),
            "status": status,
        }


class StageCreateDialog(QDialog):
    def __init__(self, parent, stage_name: str, brigades: list[dict], min_start_date: Optional[str] = None):
        super().__init__(parent)
        self.setWindowTitle(f"Создание этапа: {stage_name}")
        self._start = QDateEdit()
        self._end = QDateEdit()
        self._start.setCalendarPopup(True)
        self._end.setCalendarPopup(True)
        self._start.setDisplayFormat("yyyy-MM-dd")
        self._end.setDisplayFormat("yyyy-MM-dd")
        self._start.setDate(QDate.currentDate())
        self._end.setDate(QDate.currentDate())
        if min_start_date:
            min_qdate = QDate.fromString(min_start_date, "yyyy-MM-dd")
            if min_qdate.isValid():
                self._start.setMinimumDate(min_qdate)
                self._end.setMinimumDate(min_qdate)
                self._start.setDate(min_qdate)
                self._end.setDate(min_qdate)
        self._brigade = QComboBox()
        for b in brigades:
            self._brigade.addItem(str(b["name"]), b["id"])

        form = QFormLayout()
        form.addRow("Этап:", QLabel(stage_name))
        form.addRow("Плановая дата начала:", self._start)
        form.addRow("Плановая дата окончания:", self._end)
        form.addRow("Бригада:", self._brigade)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(buttons)

    def _on_save(self):
        if self._start.date() > self._end.date():
            QMessageBox.warning(self, "Ошибка", "Плановая дата начала должна быть не позже плановой даты окончания.")
            return
        self.accept()

    def get_data(self):
        return {
            "planned_start_date": self._start.date().toString("yyyy-MM-dd"),
            "planned_end_date": self._end.date().toString("yyyy-MM-dd"),
            "brigade_id": self._brigade.currentData(),
        }


class WorkerSelectDialog(QDialog):
    def __init__(self, parent, workers: list[dict], selected_ids=None):
        super().__init__(parent)
        self.setWindowTitle("Сотрудники")
        self._workers = workers
        self._selectors = []
        box = QVBoxLayout()
        add_btn = QPushButton("+ сотрудник")
        add_btn.clicked.connect(lambda: self._add_selector())
        root = QVBoxLayout(self)
        root.addWidget(add_btn)
        root.addLayout(box)
        self._box = box
        if selected_ids:
            for wid in selected_ids:
                self._add_selector(wid)
        else:
            self._add_selector()
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _add_selector(self, worker_id=None):
        combo = QComboBox()
        for w in self._workers:
            combo.addItem(str(w["worker_name"]), w["id"])
        if worker_id is not None:
            idx = combo.findData(worker_id)
            if idx >= 0:
                combo.setCurrentIndex(idx)
        self._box.addWidget(combo)
        self._selectors.append(combo)

    def selected_ids(self):
        return list(dict.fromkeys([s.currentData() for s in self._selectors if s.currentData()]))


class TaskFormDialog(QDialog):
    def __init__(self, parent, workers: list[dict], initial: Optional[dict] = None,
                 stage_status: str = "Планируется", stage_planned_start: Optional[str] = None,
                 has_hours: bool = False):
        super().__init__(parent)
        self._initial = initial or {}
        self._workers = workers
        self._worker_ids = []
        self._status_action = None
        self._delete_requested = False
        self._stage_status = stage_status
        self.setWindowTitle("Изменение задачи" if initial else "Добавление задачи")

        task_status = self._initial.get("task_status", "Планируется")
        is_done = (task_status == "Завершена")

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

        # Минимальная дата план старт = план старт этапа
        if stage_planned_start:
            min_qdate = QDate.fromString(str(stage_planned_start)[:10], "yyyy-MM-dd")
            if min_qdate.isValid():
                self._planned_start.setMinimumDate(min_qdate)
                self._planned_end.setMinimumDate(min_qdate)

        if self._initial.get("planned_start"):
            self._planned_start.setDate(QDate.fromString(str(self._initial["planned_start"])[:10], "yyyy-MM-dd"))
        if self._initial.get("planned_end"):
            self._planned_end.setDate(QDate.fromString(str(self._initial["planned_end"])[:10], "yyyy-MM-dd"))

        # Если задача завершена — поля только для чтения
        if is_done:
            self._name.setReadOnly(True)
            self._description.setReadOnly(True)
            self._planned_start.setReadOnly(True)
            self._planned_end.setReadOnly(True)

        self._workers_label = QLabel("Сотрудники: не выбраны")
        self._pick_workers_btn = QPushButton("Выбрать сотрудников")
        self._pick_workers_btn.clicked.connect(self._pick_workers)
        if is_done:
            self._pick_workers_btn.setEnabled(False)

        status_row = QHBoxLayout()
        self._status_label = QLabel(f"Статус: {task_status}")
        status_row.addWidget(self._status_label)
        status_row.addStretch()

        # Кнопка статуса: одна кнопка в зависимости от текущего статуса задачи
        self._status_btn = None
        if not initial:
            # Создание задачи — кнопок смены статуса нет
            pass
        elif task_status == "Планируется":
            self._status_btn = QPushButton("В работу")
            self._status_btn.clicked.connect(lambda: self._set_status_action("В работе"))
            status_row.addWidget(self._status_btn)
        elif task_status == "В работе":
            self._status_btn = QPushButton("Завершить")
            self._status_btn.clicked.connect(lambda: self._set_status_action("Завершена"))
            status_row.addWidget(self._status_btn)
        # task_status == "Завершена" — кнопки нет

        # Кнопка статуса активна только если этап «В работе»
        if self._status_btn is not None and stage_status != "В работе":
            self._status_btn.setEnabled(False)
            self._status_btn.setToolTip("Недоступно: этап не находится в статусе 'В работе'")

        form = QFormLayout()
        form.addRow("Название:", self._name)
        form.addRow("Описание:", self._description)
        form.addRow("Плановая дата начала:", self._planned_start)
        form.addRow("Плановая дата окончания:", self._planned_end)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(self._pick_workers_btn)
        root.addWidget(self._workers_label)
        root.addLayout(status_row)
        # Кнопка удаления: только при редактировании и когда нет залогированных часов
        if initial and not has_hours:
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

    def _set_status_action(self, status):
        self._status_action = status
        self._status_label.setText(f"Статус: {status}")

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
        return {
            "name": self._name.text().strip(),
            "description": self._description.text().strip() or None,
            "planned_start": self._planned_start.date().toString("yyyy-MM-dd") + " 09:00:00",
            "planned_end": self._planned_end.date().toString("yyyy-MM-dd") + " 18:00:00",
            "worker_ids": self._worker_ids,
            "status_action": self._status_action,
        }


class MaterialCreateDialog(QDialog):
    def __init__(self, parent, materials: list[dict]):
        super().__init__(parent)
        self.setWindowTitle("Добавление материала")
        self._material = QComboBox()
        for m in materials:
            self._material.addItem(str(m["name"]), m["id"])
        self._planned = QLineEdit()
        form = QFormLayout()
        form.addRow("Материал:", self._material)
        form.addRow("Плановое количество:", self._planned)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(buttons)

    def _on_save(self):
        try:
            if float(self._planned.text().strip().replace(",", ".")) <= 0:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Введите число > 0.")
            return
        self.accept()

    def get_data(self):
        return {"material_id": self._material.currentData(), "planned_quantity": float(self._planned.text().strip().replace(",", "."))}


class MaterialAddActualDialog(QDialog):
    """Мини-форма: добавить фактическое количество со склада."""

    def __init__(self, parent, available: float, unit: str):
        super().__init__(parent)
        self.setWindowTitle("Добавить со склада")
        self._available = available
        self._amount = QLineEdit()
        form = QFormLayout()
        form.addRow(f"Доступно на складе:", QLabel(f"{available} {unit}"))
        form.addRow("Добавить количество:", self._amount)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Добавить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(buttons)

    def _on_save(self):
        try:
            val = float(self._amount.text().strip().replace(",", "."))
            if val <= 0:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Введите число > 0.")
            return
        if val > self._available:
            QMessageBox.warning(self, "Ошибка", f"Нельзя добавить больше, чем доступно на складе ({self._available}).")
            return
        self.accept()

    def get_amount(self) -> float:
        return float(self._amount.text().strip().replace(",", "."))


class MaterialEditDialog(QDialog):
    """Диалог редактирования материала этапа (двойной клик)."""

    def __init__(self, parent, manager, material: dict):
        super().__init__(parent)
        self._manager = manager
        self._material = material
        self.setWindowTitle(f"Материал: {material.get('material_name', '')}")

        planned = material.get("planned_quantity", 0) or 0
        self._planned = QLineEdit(str(planned))
        self._planned.setReadOnly(True)

        actual = material.get("actual_quantity")
        actual_text = str(actual) if actual is not None else "-"
        self._actual_label = QLabel(actual_text)

        form = QFormLayout()
        form.addRow("Материал:", QLabel(str(material.get("material_name", ""))))
        form.addRow("Плановое количество:", self._planned)

        actual_row = QHBoxLayout()
        actual_row.addWidget(self._actual_label)
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self._add_actual)
        actual_row.addWidget(add_btn)
        actual_row.addStretch()
        form.addRow("Фактическое количество:", actual_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Сохранить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)

        self._delete_requested = False
        root = QVBoxLayout(self)
        root.addLayout(form)
        # Кнопка удаления: только если фактического количества нет
        if actual is None or actual == 0:
            del_btn = QPushButton("Удалить материал")
            del_btn.clicked.connect(self._on_delete)
            root.addWidget(del_btn)
        root.addWidget(buttons)

    def _on_delete(self):
        self._delete_requested = True
        self.accept()

    def _add_actual(self):
        material_id = self._material.get("material_id")
        stage_material_id = self._material.get("stage_material_id")
        stock_rows = self._manager._fetch_all(
            "select quantity_in_stock, unit_of_measurement from material where id=%s;",
            (material_id,),
        )
        if not stock_rows:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить данные со склада.")
            return
        available = float(stock_rows[0][0] or 0)
        unit = str(stock_rows[0][1] or "")
        dlg = MaterialAddActualDialog(self, available, unit)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        amount = dlg.get_amount()
        current_actual = self._material.get("actual_quantity") or 0
        new_actual = float(current_actual) + amount
        ok1 = self._manager._execute(
            "update stage_material set actual_quantity=%s where id=%s;",
            (new_actual, stage_material_id),
        )
        ok2 = self._manager._execute(
            "update material set quantity_in_stock = quantity_in_stock - %s where id=%s;",
            (amount, material_id),
        )
        log_data_change(
            self._manager.db,
            f"Фактическое кол-во материала id={material_id} +{amount} (этап sm={stage_material_id})",
            success=ok1 and ok2,
        )
        self._material["actual_quantity"] = new_actual
        self._actual_label.setText(str(new_actual))
        QMessageBox.information(self, "Успешно", f"Добавлено {amount} {unit}. Фактическое количество: {new_actual}.")

    def _on_save(self):
        try:
            val = float(self._planned.text().strip().replace(",", "."))
            if val <= 0:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Введите число > 0.")
            return
        self.accept()

    def get_planned_quantity(self) -> float:
        return float(self._planned.text().strip().replace(",", "."))


class StageViewWidget(QWidget):
    def __init__(self, parent_dialog, stage: dict):
        super().__init__()
        self.dialog = parent_dialog
        self.stage = stage
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(2)
        root.setContentsMargins(4, 4, 4, 4)

        stage_status = self.stage["stage_status"]
        is_done = (stage_status == "Завершен")

        head = QHBoxLayout()
        head.addWidget(QLabel("Этап:"))
        head.addWidget(QLabel(str(self.stage["stage_name"])))
        head.setSpacing(20)
        head.addWidget(QLabel(f"Статус: {stage_status}"))
        # Кнопка смены статуса: только если этап НЕ завершён
        if not is_done:
            status_btn_label = "Перевести в работу" if stage_status == "Планируется" else "Завершить"
            status_btn = QPushButton(status_btn_label)
            status_btn.clicked.connect(lambda: self.dialog.change_stage_status(self.stage))
            head.addWidget(status_btn)
        head.addStretch()
        root.addLayout(head)
        root.addSpacing(20)

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
        root.addSpacing(20)

        brig_row = QHBoxLayout()
        brig_row.addWidget(QLabel("Бригада:"))
        self.brigade_combo = QComboBox()
        for b in self.dialog.brigades:
            self.brigade_combo.addItem(str(b["name"]), b["id"])
        idx = self.brigade_combo.findData(self.stage["brigade_id"])
        if idx >= 0:
            self.brigade_combo.setCurrentIndex(idx)
        # Если этап завершён — нельзя менять бригаду
        if is_done:
            self.brigade_combo.setEnabled(False)
        else:
            self.brigade_combo.currentIndexChanged.connect(self._on_brigade_changed)
        brig_row.addWidget(self.brigade_combo)
        brig_row.addWidget(QLabel(f"Бригадир: {_fmt(self.stage.get('foreman_full_name'))}"))
        brig_row.addStretch()
        root.addLayout(brig_row)
        root.addSpacing(20)

        tasks_head = QHBoxLayout()
        tasks_head.addWidget(QLabel("Задачи"))
        # Кнопка добавления задачи: только если этап НЕ завершён
        if not is_done:
            plus_task = QPushButton("+")
            plus_task.clicked.connect(lambda: self.dialog.add_task(self.stage["project_stage_id"]))
            tasks_head.addWidget(plus_task)
        tasks_head.addStretch()
        root.addLayout(tasks_head)
        root.addWidget(self._tasks_table())
        root.addSpacing(20)

        mats_head = QHBoxLayout()
        mats_head.addWidget(QLabel("Материалы"))
        # Кнопка добавления материала: только если этап НЕ завершён
        if not is_done:
            plus_mat = QPushButton("+")
            plus_mat.clicked.connect(lambda: self.dialog.add_material(self.stage["project_stage_id"]))
            mats_head.addWidget(plus_mat)
        mats_head.addStretch()
        root.addLayout(mats_head)
        root.addWidget(self._materials_table())
        root.addStretch()

    def _tasks_table(self):
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels(
            ["id", "Задача", "Описание", "Статус", "План дата начала", "Факт дата начала", "Сотрудники", "План дата окончания", "Факт дата окончания"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setWordWrap(True)
        tasks = self.stage.get("tasks", [])
        table.setRowCount(len(tasks))
        for r, t in enumerate(tasks):
            values = [
                t.get("task_id"),
                t.get("task_name"),
                t.get("task_description"),
                t.get("task_status"),
                t.get("planned_start"),
                t.get("actual_start"),
                t.get("workers_assigned"),
                t.get("planned_end"),
                t.get("actual_end"),
            ]
            for c, v in enumerate(values):
                item = QTableWidgetItem(_fmt(v))
                if c == 0:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(r, c, item)
        compact_table_rows(table)
        total_h = table.horizontalHeader().height() + 8
        for i in range(table.rowCount()):
            total_h += table.rowHeight(i)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        target_h = min(max(total_h, 52), 320)
        table.setMinimumHeight(target_h)
        table.setMaximumHeight(target_h)
        table.itemDoubleClicked.connect(
            lambda item: self.dialog.edit_task(self.stage["project_stage_id"], table.item(item.row(), 0).text())
        )
        return table

    def _materials_table(self):
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Используемый материал", "Плановое количество", "Фактическое количество"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setWordWrap(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        materials = self.stage.get("materials", [])
        table.setRowCount(len(materials))
        for r, m in enumerate(materials):
            values = [m.get("material_name"), m.get("planned_quantity"), m.get("actual_quantity")]
            for c, v in enumerate(values):
                item = QTableWidgetItem(_fmt(v))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(r, c, item)
        stage = self.stage
        table.itemDoubleClicked.connect(
            lambda item: self.dialog.edit_material(stage["project_stage_id"], stage, item.row())
        )
        compact_table_rows(table)
        total_h = table.horizontalHeader().height() + 8
        for i in range(table.rowCount()):
            total_h += table.rowHeight(i)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        target_h = min(max(total_h, 52), 280)
        table.setMinimumHeight(target_h)
        table.setMaximumHeight(target_h)
        return table

    def _on_brigade_changed(self):
        self.dialog.change_brigade(self.stage["project_stage_id"], self.brigade_combo.currentData())


class ManagerStagesDialog(QDialog):
    def __init__(self, parent, manager, project: dict):
        super().__init__(parent)
        self.manager = manager
        self.project = project
        self.brigades = self.manager._fetch_all("select id,name from brigade order by name;", as_dict=True)
        self.tabs = QTabWidget()
        self._suppress = False
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setWindowTitle(f"Этапы проекта {project.get('name')}")
        self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)
        root = QVBoxLayout(self)
        root.addWidget(self.tabs)
        self.reload()

    def reload(self, keep_tab=False):
        current_index = self.tabs.currentIndex() if keep_tab else 0
        self._suppress = True
        self.tabs.clear()
        self.stages = self.manager.load_project_stages(self.project["project_id"])
        for st in self.stages:
            self.tabs.addTab(StageViewWidget(self, st), f"{st['stage_name']} [{st['stage_status']}]")
        next_stage = self.manager.get_next_missing_stage(self.project["project_id"])
        if next_stage:
            placeholder = QWidget()
            lay = QVBoxLayout(placeholder)
            lay.addWidget(QLabel(f"Создать этап: {next_stage['name']}"))
            lay.addStretch()
            self.tabs.addTab(placeholder, f"+ {next_stage['name']}")
        self._suppress = False
        if keep_tab and 0 <= current_index < self.tabs.count():
            self.tabs.setCurrentIndex(current_index)
        # Если этапов нет — единственная вкладка уже активна (index=0),
        # currentChanged не сработает повторно, открываем форму вручную через singleShot
        if not self.stages and next_stage:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._open_first_stage_form())

    def _open_first_stage_form(self):
        """Открывает форму создания этапа; вызывается когда этапов ещё нет."""
        if not self.stages:
            self._create_next_stage()

    def _create_next_stage(self):
        """Общая логика создания следующего (или первого) этапа."""
        next_stage = self.manager.get_next_missing_stage(self.project["project_id"])
        if not next_stage:
            return
        prev_end_rows = self.manager._fetch_all(
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
        if not self.manager._confirm(
            "Создать этап?",
            audit_decline_details=f"Отмена создания этапа «{next_stage['name']}»",
        ):
            self.reload()
            return
        data = dlg.get_data()
        ok = self.manager._execute(
            """
            insert into project_stage(stage_id,project_id,planned_start_date,planned_end_date,status,brigade_id)
            values(%s,%s,%s,%s,'Планируется',%s);
            """,
            (next_stage["id"], self.project["project_id"], data["planned_start_date"], data["planned_end_date"],
             data["brigade_id"]),
        )
        log_data_change(
            self.manager.db,
            f"Этап «{next_stage['name']}» в проекте id={self.project['project_id']}",
            success=ok,
        )
        self.reload()

    def _on_tab_changed(self, index):
        if self._suppress or index < 0:
            return
        if index == self.tabs.count() - 1:
            next_stage = self.manager.get_next_missing_stage(self.project["project_id"])
            if not next_stage:
                return
            self._create_next_stage()

    def change_stage_status(self, stage):
        if self.project.get("status") == "Планируется":
            QMessageBox.warning(
                self,
                "Ошибка",
                'Нельзя менять статус этапа, пока проект в статусе «Планируется».',
            )
            return
        new_status = "В работе" if stage["stage_status"] == "Планируется" else "Завершен"
        if new_status == "В работе":
            # Находим индекс текущего этапа в списке (отсортированном по planned_start)
            stage_ids = [st["project_stage_id"] for st in self.stages]
            current_index = stage_ids.index(stage["project_stage_id"]) if stage["project_stage_id"] in stage_ids else -1
            if current_index > 0:
                prev_stage = self.stages[current_index - 1]
                if prev_stage["stage_status"] != "Завершен":
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        f"Нельзя начать этап: предыдущий этап «{prev_stage['stage_name']}» ещё не завершён.",
                    )
                    return
        if new_status == "Завершен":
            not_done = self.manager._fetch_all(
                "select id from task where project_stage_id=%s and status<>'Завершена' limit 1;",
                (stage["project_stage_id"],),
            )
            if not_done:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Нельзя завершить этап: есть незавершенные задачи.",
                )
                return
        if not self.manager._confirm(
            f"Изменить статус этапа на «{new_status}»?",
            audit_decline_details=(
                f"Отмена смены статуса этапа «{stage['stage_name']}» на «{new_status}»"
            ),
        ):
            return
        if new_status == "В работе":
            ok = self.manager._execute(
                "update project_stage set status=%s, actual_start_date=coalesce(actual_start_date,current_date()) where id=%s;",
                (new_status, stage["project_stage_id"]),
            )
        else:
            ok = self.manager._execute(
                "update project_stage set status=%s, actual_end_date=coalesce(actual_end_date,current_date()) where id=%s;",
                (new_status, stage["project_stage_id"]),
            )
        log_data_change(
            self.manager.db,
            f"Этап id={stage['project_stage_id']} «{stage['stage_name']}»: статус → «{new_status}»",
            success=ok,
        )
        self.reload(keep_tab=True)

    def change_brigade(self, project_stage_id, brigade_id):
        if not self.manager._confirm(
            "Подтвердить смену бригады?",
            audit_decline_details=f"Отмена смены бригады на этапе id={project_stage_id}",
        ):
            self.reload(keep_tab=True)
            return
        ok = self.manager._execute(
            "update project_stage set brigade_id=%s where id=%s;",
            (brigade_id, project_stage_id),
        )
        log_data_change(
            self.manager.db,
            f"Смена бригады на этапе id={project_stage_id}",
            success=ok,
        )
        self.reload(keep_tab=True)

    def _get_stage_by_project_stage_id(self, project_stage_id):
        for st in self.stages:
            if st["project_stage_id"] == project_stage_id:
                return st
        return {}

    def add_task(self, project_stage_id):
        stage = self._get_stage_by_project_stage_id(project_stage_id)
        stage_status = stage.get("stage_status", "Планируется")
        stage_planned_start = stage.get("planned_start")
        workers = self.manager.load_workers_for_stage(project_stage_id)
        dlg = TaskFormDialog(self, workers, stage_status=stage_status, stage_planned_start=stage_planned_start)
        if workers:
            dlg.set_selected_workers([workers[0]["id"]])
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        if not self.manager._confirm(
            "Добавить задачу?",
            audit_decline_details="Отмена добавления задачи",
        ):
            return
        payload = dlg.get_data()
        self.manager.create_task(project_stage_id, payload)
        log_data_change(
            self.manager.db,
            f"Добавлена задача «{payload['name']}» на этапе id={project_stage_id}",
        )
        self.reload(keep_tab=True)

    def edit_task(self, project_stage_id, task_id_text):
        task_id = int(task_id_text)
        task = self.manager.get_task(task_id)
        if not task:
            return
        stage = self._get_stage_by_project_stage_id(project_stage_id)
        stage_status = stage.get("stage_status", "Планируется")
        stage_planned_start = stage.get("planned_start")
        workers = self.manager.load_workers_for_stage(project_stage_id)
        # Проверяем: есть ли залогированные часы у задачи
        hours_rows = self.manager._fetch_all(
            "select coalesce(sum(hours_spent), 0) from work_log where task_id=%s;",
            (task_id,),
        )
        has_hours = bool(hours_rows and hours_rows[0][0] and float(hours_rows[0][0]) != 0)
        dlg = TaskFormDialog(self, workers, task, stage_status=stage_status,
                             stage_planned_start=stage_planned_start, has_hours=has_hours)
        dlg.set_selected_workers(self.manager.get_task_worker_ids(task_id))
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        if dlg._delete_requested:
            if not self.manager._confirm(
                "Удалить задачу?",
                audit_decline_details=f"Отмена удаления задачи id={task_id}",
            ):
                return
            self.manager._execute("delete from work_log where task_id=%s;", (task_id,))
            ok = self.manager._execute("delete from task where id=%s;", (task_id,))
            log_data_change(
                self.manager.db,
                f"Удалена задача id={task_id}",
                success=ok,
            )
            self.reload(keep_tab=True)
            return
        if not self.manager._confirm(
            "Сохранить изменения задачи?",
            audit_decline_details=f"Отмена изменения задачи id={task_id}",
        ):
            return
        payload = dlg.get_data()
        self.manager.update_task(task_id, payload)
        log_data_change(
            self.manager.db,
            f"Изменена задача id={task_id} «{payload['name']}»",
        )
        self.reload(keep_tab=True)

    def add_material(self, project_stage_id):
        all_materials = self.manager._fetch_all("select id,name from material order by name;", as_dict=True)
        # Убираем уже добавленные материалы для этого этапа
        used_rows = self.manager._fetch_all(
            "select material_id from stage_material where project_stage_id=%s;",
            (project_stage_id,),
        )
        used_ids = {r[0] for r in used_rows}
        materials = [m for m in all_materials if m["id"] not in used_ids]
        if not materials:
            QMessageBox.information(self, "Информация", "Все доступные материалы уже добавлены к этому этапу.")
            return
        dlg = MaterialCreateDialog(self, materials)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        if not self.manager._confirm(
            "Добавить материал?",
            audit_decline_details="Отмена добавления материала к этапу",
        ):
            return
        payload = dlg.get_data()
        stock_rows = self.manager._fetch_all(
            "select quantity_in_stock from material where id=%s;",
            (payload["material_id"],),
        )
        # stock_qty = stock_rows[0][0] if stock_rows else 0
        #
        # if payload["planned_quantity"] > stock_qty:
        #     QMessageBox.warning(self, "Ошибка", "Недостаточно материала на складе.")
        #     return
        ok = self.manager._execute(
            "insert into stage_material(project_stage_id,material_id,planned_quantity,actual_quantity) values(%s,%s,%s,null);",
            (project_stage_id, payload["material_id"], payload["planned_quantity"]),
        )
        log_data_change(
            self.manager.db,
            f"Материал id={payload['material_id']} на этапе id={project_stage_id}",
            success=ok,
        )
        self.reload(keep_tab=True)

    def edit_material(self, project_stage_id, stage, row_index):
        materials = stage.get("materials", [])
        if row_index < 0 or row_index >= len(materials):
            return
        material = materials[row_index]
        dlg = MaterialEditDialog(self, self.manager, material)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        if dlg._delete_requested:
            if not self.manager._confirm(
                "Удалить материал из этапа?",
                audit_decline_details=(
                    f"Отмена удаления материала «{material.get('material_name')}»"
                ),
            ):
                return
            ok = self.manager._execute(
                "delete from stage_material where id=%s;",
                (material["stage_material_id"],),
            )
            log_data_change(
                self.manager.db,
                f"Удалён материал этапа id={material['stage_material_id']}",
                success=ok,
            )
            self.reload(keep_tab=True)
            return
        new_planned = dlg.get_planned_quantity()
        ok = self.manager._execute(
            "update stage_material set planned_quantity=%s where id=%s;",
            (new_planned, material["stage_material_id"]),
        )
        log_data_change(
            self.manager.db,
            f"Плановое кол-во материала id={material['stage_material_id']} → {new_planned}",
            success=ok,
        )
        self.reload(keep_tab=True)

class ManagerPanelWindow(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self._stages_dialog = None
        self.setWindowTitle("Панель менеджера")
        self._build_ui()
        apply_window_icon(self)
        self._refresh()
        self.showMaximized()

    def _build_ui(self):
        root = QVBoxLayout(self)
        content_margins(root, 16, 12)
        root.addWidget(
            create_panel_header(
                "Панель менеджера проектов",
                "Проекты, этапы, задачи и материалы",
                on_logout=self._logout,
            )
        )
        title = section_label("Список проектов")
        title.setStyleSheet("padding: 0; margin: 0;")
        root.addWidget(title)
        self.projects_table = QTableWidget()
        configure_table(self.projects_table, sortable=False)
        self.projects_table.setColumnCount(6)
        self.projects_table.setHorizontalHeaderLabels(
            ["Название", "Адрес", "Дата начала", "Дата окончания", "Статус", "Текущий этап"])
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.projects_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.projects_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.projects_table.verticalHeader().setVisible(False)
        self.projects_table.setWordWrap(True)
        self.projects_table.setColumnWidth(0, 260)
        self.projects_table.setColumnWidth(1, 280)
        self.projects_table.setColumnWidth(2, 120)
        self.projects_table.setColumnWidth(3, 120)
        self.projects_table.setColumnWidth(4, 260)
        self.projects_table.setColumnWidth(5, 280)
        root.addWidget(self.projects_table)

        bottom = QHBoxLayout()
        report_btn = QPushButton("Сформировать отчёт")
        style_primary_button(report_btn)
        report_btn.clicked.connect(self._open_report_dialog)
        bottom.addWidget(report_btn)
        bottom.addStretch()
        add_btn = QPushButton("Добавить")
        edit_btn = QPushButton("Изменить")
        del_btn = QPushButton("Удалить")
        style_primary_button(add_btn)
        style_secondary_button(edit_btn)
        style_danger_button(del_btn)
        add_btn.clicked.connect(self._add_project)
        edit_btn.clicked.connect(self._edit_project)
        del_btn.clicked.connect(self._delete_project)
        bottom.addWidget(add_btn)
        bottom.addWidget(edit_btn)
        bottom.addWidget(del_btn)
        root.addLayout(bottom)
        # root.addStretch(1)

    def _logout(self):
        from audit_service import record_logout
        from windows.auth_window import AuthWindow

        username = self.db._active_config.get("user")
        if username:
            record_logout(self.db, username, "Выход (руководитель проекта)")
        self._auth_window = AuthWindow()
        self._auth_window.showMaximized()
        self.close()

    def _confirm(self, text, audit_decline_details: Optional[str] = None):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Question)

        yes_button = msg_box.addButton("Да", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.ButtonRole.NoRole)

        msg_box.setDefaultButton(yes_button)
        msg_box.setEscapeButton(no_button)

        msg_box.exec()

        clicked_button = msg_box.clickedButton()
        ok = clicked_button == yes_button
        if not ok and audit_decline_details:
            log_data_declined(self.db, audit_decline_details)
        return ok

    def _fetch_all(self, query, params=(), as_dict=False):
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
                        when exists (select 1 from project_stage ps2 where ps2.project_id = p.id and ps2.status = 'В работе')
                            then (select concat(s.name, ' (', ps3.status, ')')
                                  from project_stage ps3 join stage s on s.id = ps3.stage_id
                                  where ps3.project_id = p.id and ps3.status = 'В работе'
                                  limit 1)
                        else (select concat(s.name, ' (', ps4.status, ')')
                              from project_stage ps4 join stage s on s.id = ps4.stage_id
                              where ps4.project_id = p.id and ps4.actual_end_date is not null
                              order by ps4.actual_end_date desc
                              limit 1)
                    end, '-') as stage_info
            from project p
            order by p.id;
            """,
            as_dict=True,
        )

    def _refresh(self):
        projects = self.load_projects()
        self.projects_table.setRowCount(len(projects))
        for r, p in enumerate(projects):
            self.projects_table.setItem(r, 0, QTableWidgetItem(_fmt(p["name"])))
            self.projects_table.setItem(r, 1, QTableWidgetItem(_fmt(p["address"])))
            self.projects_table.setItem(r, 2, QTableWidgetItem(_fmt(p["start_date"])))
            self.projects_table.setItem(r, 3, QTableWidgetItem(_fmt(p["end_date"])))

            status_w = QWidget()
            status_l = QHBoxLayout(status_w)
            status_l.setContentsMargins(4, 2, 4, 2)
            status_l.setSpacing(4)
            status_l.addWidget(QLabel(_fmt(p["status"])))
            if p["status"] != "Завершен":
                act_btn = QPushButton(
                    "Перевести в работу" if p["status"] == "Планируется" else "Завершить"
                )
                act_btn.setMinimumWidth(150)
                style_secondary_button(act_btn)
                act_btn.clicked.connect(
                    lambda _=False, project=p: self._advance_project_status(project)
                )
                status_l.addWidget(act_btn)
            self.projects_table.setCellWidget(r, 4, status_w)

            stage_w = QWidget()
            stage_l = QHBoxLayout(stage_w)
            stage_l.setContentsMargins(4, 2, 4, 2)
            stage_l.addWidget(QLabel(_fmt(p["stage_info"])), 1)
            plus = QPushButton("...")
            plus.clicked.connect(lambda _=False, project=p: self._open_stages(project))
            stage_l.addWidget(plus)
            self.projects_table.setCellWidget(r, 5, stage_w)

        QTimer.singleShot(0, self._after_table_update)

    def _after_table_update(self):
        header = self.projects_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Даты — по содержимому
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        resize_table_rows(self.projects_table)
        for row in range(self.projects_table.rowCount()):
            self.projects_table.setRowHeight(
                row, max(self.projects_table.rowHeight(row), 72)
            )

    def _open_report_dialog(self):
        dlg = ManagerReportDialog(self, self)
        dlg.exec()

    def _selected_project(self):
        rows = self.projects_table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        name = self.projects_table.item(row, 0).text()
        projects = self._fetch_all(
            "select id as project_id, name, address, start_date, end_date, status from project where name=%s limit 1;",
            (name,),
            as_dict=True,
        )
        return projects[0] if projects else None

    def _add_project(self):
        dlg = ProjectFormDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        payload = dlg.get_data()
        if not self._confirm(
            "Добавить проект?",
            audit_decline_details=f"Отмена создания проекта «{payload['name']}»",
        ):
            return
        if not self._execute(
                "insert into project(name,address,start_date,end_date,status) values(%s,%s,NULL,%s,%s);",
                (payload["name"], payload["address"], None, payload["status"]),
        ):
            log_data_change(self.db, f"Ошибка создания проекта «{payload['name']}»", success=False)
            return
        log_data_change(self.db, f"Создан проект «{payload['name']}»")
        project_id = self._fetch_all("select id from project order by id desc limit 1;")[0][0]
        first_stage = self._fetch_all("select id,name from stage order by id limit 1;", as_dict=True)
        brigades = self._fetch_all("select id,name from brigade order by name;", as_dict=True)
        if first_stage:
            sdlg = StageCreateDialog(self, first_stage[0]["name"], brigades, None)
            if sdlg.exec() == QDialog.DialogCode.Accepted and self._confirm("Создать первый этап?"):
                data = sdlg.get_data()
                self._execute(
                    """
                    insert into project_stage(stage_id,project_id,planned_start_date,planned_end_date,status,brigade_id)
                    values(%s,%s,%s,%s,'Планируется',%s);
                    """,
                    (first_stage[0]["id"], project_id, data["planned_start_date"], data["planned_end_date"],
                     data["brigade_id"]),
                )
        self._refresh()

    def _edit_project(self):
        project = self._selected_project()
        if not project:
            QMessageBox.warning(self, "Изменение", "Выберите проект.")
            return
        dlg = ProjectFormDialog(self, project)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        if not self._confirm(
            "Сохранить изменения проекта?",
            audit_decline_details=f"Отмена изменения проекта «{project['name']}»",
        ):
            return
        payload = dlg.get_data()
        end_date = None
        if payload["status"] == "Завершен":
            not_done = self._fetch_all(
                "select id from project_stage where project_id=%s and status<>'Завершен' limit 1;",
                (project["project_id"],),
            )
            if not_done:
                QMessageBox.warning(self, "Ошибка", "Нельзя завершить проект: не все этапы завершены.")
                return
            end_date = date.today().isoformat()
        ok = self._execute(
            "update project set name=%s,address=%s,status=%s,end_date=%s where id=%s;",
            (payload["name"], payload["address"], payload["status"], end_date,
             project["project_id"]),
        )
        log_data_change(
            self.db,
            f"Изменён проект id={project['project_id']} «{payload['name']}»",
            success=ok,
        )
        self._refresh()

    def _delete_project(self):
        project = self._selected_project()
        if not project:
            QMessageBox.warning(self, "Удаление", "Выберите проект.")
            return
        if not self._confirm(
            "Удалить проект?",
            audit_decline_details=f"Отмена удаления проекта «{project['name']}»",
        ):
            return
        ok = self._execute("delete from project where id=%s;", (project["project_id"],))
        log_data_change(
            self.db,
            f"Удалён проект id={project['project_id']} «{project['name']}»",
            success=ok,
        )
        self._refresh()

    def _advance_project_status(self, project):
        if project["status"] == "Планируется":
            stages_count = self._fetch_all(
                "select count(*) from project_stage where project_id=%s;",
                (project["project_id"],),
            )
            if stages_count and stages_count[0][0] < 5:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Проект можно перевести в работу только после создания всех 5 этапов.",
                )
                return
            bad_stages = self._fetch_all(
                "select id from project_stage where project_id=%s and status<>'Планируется' limit 1;",
                (project["project_id"],),
            )
            if bad_stages:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Перевести проект в работу можно только если все этапы в статусе 'Планируется'.",
                )
                return
            if not self._confirm(
                "Перевести проект в работу?",
                audit_decline_details=f"Отмена перевода проекта «{project['name']}» в работу",
            ):
                return
            ok = self._execute(
                "update project set status='В работе', start_date=%s where id=%s;",
                (date.today().isoformat(), project["project_id"]),
            )
            log_data_change(
                self.db,
                f"Проект id={project['project_id']} переведён в работу",
                success=ok,
            )
        elif project["status"] == "В работе":
            not_done = self._fetch_all(
                "select id from project_stage where project_id=%s and status<>'Завершен' limit 1;",
                (project["project_id"],),
            )
            if not_done:
                QMessageBox.warning(self, "Ошибка", "Нельзя завершить проект: не все этапы завершены.")
                return
            if not self._confirm(
                "Завершить проект?",
                audit_decline_details=f"Отмена завершения проекта «{project['name']}»",
            ):
                return
            ok = self._execute(
                "update project set status='Завершен', end_date=%s where id=%s;",
                (date.today().isoformat(), project["project_id"]),
            )
            log_data_change(
                self.db,
                f"Проект id={project['project_id']} завершён",
                success=ok,
            )
        self._refresh()

    def _open_stages(self, project):
        try:
            self._stages_dialog = ManagerStagesDialog(self, self, project)
            self._stages_dialog.exec()
            self._refresh()
        except Exception as e:
            print("CRASH:", e)

    def get_next_missing_stage(self, project_id):
        rows = self._fetch_all(
            """
            select s.id, s.name
            from stage s
            where s.id not in (select ps.stage_id from project_stage ps where ps.project_id=%s)
            order by s.id
            limit 1;
            """,
            (project_id,),
            as_dict=True,
        )
        return rows[0] if rows else None

    def load_project_stages(self, project_id):
        stages = self._fetch_all(
            """
            select
                ps.id as project_stage_id,
                ps.brigade_id,
                s.name as stage_name,
                ps.status as stage_status,
                ps.planned_start_date as planned_start,
                ps.planned_end_date as planned_end,
                ps.actual_start_date as actual_start,
                ps.actual_end_date as actual_end,
                b.name as brigade_name,
                (select concat(w.surname, ' ', w.name, ' ', ifnull(w.patronymic, ''))
                 from worker w
                 join brigade_composition bc on w.id = bc.worker_id
                 where bc.brigade_id = b.id
                   and w.specialty_id = 1
                 limit 1) as foreman_full_name
            from project_stage ps
            join stage s on ps.stage_id = s.id
            left join brigade b on ps.brigade_id = b.id
            join project p on ps.project_id = p.id
            where p.id = %s
            order by ps.planned_start_date;
            """,
            (project_id,),
            as_dict=True,
        )
        for st in stages:
            sid = st["project_stage_id"]
            st["tasks"] = self._fetch_all(
                """
                select
                    t.id as task_id,
                    t.name as task_name,
                    t.description as task_description,
                    t.status as task_status,
                    t.planned_start_datetime as planned_start,
                    t.actual_start_datetime as actual_start,
                    t.planned_end_datetime as planned_end,
                    t.actual_end_datetime as actual_end,
                    GROUP_CONCAT(
                    DISTINCT CONCAT(
                        w.surname,
                        ' ',
                        SUBSTRING(w.name, 1, 1), '.',
                        CASE
                            WHEN w.patronymic IS NOT NULL AND w.patronymic != ''
                            THEN ' ' || SUBSTRING(w.patronymic, 1, 1) || '.'
                            ELSE ''
                        END
                    )
                    ORDER BY w.surname
                    SEPARATOR '\n'
                ) AS workers_assigned
                from task t
                left join work_log wl on wl.task_id=t.id
                left join worker w on w.id=wl.worker_id
                where t.project_stage_id=%s
                group by t.id,t.name,t.description,t.status,t.planned_start_datetime,t.actual_start_datetime,t.planned_end_datetime,t.actual_end_datetime
                order by t.planned_start_datetime;
                """,
                (sid,),
                as_dict=True,
            )
            st["materials"] = self._fetch_all(
                """
                select sm.id as stage_material_id, sm.material_id, m.name as material_name, sm.planned_quantity, sm.actual_quantity
                from stage_material sm
                join material m on m.id=sm.material_id
                where sm.project_stage_id=%s
                order by m.name;
                """,
                (sid,),
                as_dict=True,
            )
        return stages

    def load_workers_for_stage(self, project_stage_id):
        return self._fetch_all(
            """
            select w.id, concat(w.surname, ' ', w.name, ' ', ifnull(w.patronymic, '')) as worker_name
            from project_stage ps
            join brigade_composition bc on bc.brigade_id=ps.brigade_id
            join worker w on w.id=bc.worker_id
            where ps.id=%s
            order by w.surname, w.name;
            """,
            (project_stage_id,),
            as_dict=True,
        )

    def create_task(self, project_stage_id, payload):
        ok = self._execute(
            """
            insert into task(name,description,project_stage_id,planned_start_datetime,planned_end_datetime,status)
            values(%s,%s,%s,%s,%s,'Планируется');
            """,
            (payload["name"], payload["description"], project_stage_id, payload["planned_start"],
             payload["planned_end"]),
        )
        if not ok:
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
            select
                t.id as task_id,
                t.name as task_name,
                t.description as task_description,
                t.status as task_status,
                t.planned_start_datetime as planned_start,
                t.planned_end_datetime as planned_end
            from task t
            where t.id=%s
            limit 1;
            """,
            (task_id,),
            as_dict=True,
        )
        return rows[0] if rows else None

    def get_task_worker_ids(self, task_id):
        rows = self._fetch_all("select distinct worker_id from work_log where task_id=%s;", (task_id,))
        return [x[0] for x in rows]

    def update_task(self, task_id, payload):
        self._execute(
            """
            update task
            set name=%s, description=%s, planned_start_datetime=%s, planned_end_datetime=%s
            where id=%s;
            """,
            (payload["name"], payload["description"], payload["planned_start"], payload["planned_end"], task_id),
        )
        if payload.get("status_action") == "В работе":
            self._execute(
                "update task set status=%s, actual_start_datetime=coalesce(actual_start_datetime, now()) where id=%s;",
                ("В работе", task_id),
            )
        elif payload.get("status_action") == "Завершена":
            self._execute(
                "update task set status=%s, actual_end_datetime=coalesce(actual_end_datetime, now()) where id=%s;",
                ("Завершена", task_id),
            )
        self._execute("delete from work_log where task_id=%s;", (task_id,))
        for worker_id in payload["worker_ids"]:
            self._execute(
                "insert into work_log(task_id,worker_id,hours_spent,work_date) values(%s,%s,0,current_date());",
                (task_id, worker_id),
            )