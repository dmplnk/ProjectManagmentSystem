"""Диалоги формирования Word-отчётов."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
)

from word_report import build_accountant_report, build_manager_report


class ManagerReportDialog(QDialog):
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self._manager = manager
        self.setWindowTitle("Формирование отчёта")
        self.resize(520, 480)

        self._projects = manager._fetch_all(
            "select id as project_id, name, address, start_date, end_date, status "
            "from project order by name;",
            as_dict=True,
        )

        self._list = QListWidget()
        for p in self._projects:
            item = QListWidgetItem(p["name"])
            item.setData(Qt.ItemDataRole.UserRole, p["project_id"])
            item.setCheckState(Qt.CheckState.Unchecked)
            self._list.addItem(item)

        params = QGroupBox("Включить в отчёт")
        params_lay = QVBoxLayout(params)
        self._chk_stages = QCheckBox("Этапы")
        self._chk_stages.setChecked(True)
        self._chk_tasks = QCheckBox("Задачи")
        self._chk_tasks.setChecked(True)
        self._chk_materials = QCheckBox("Материалы")
        self._chk_materials.setChecked(True)
        params_lay.addWidget(self._chk_stages)
        params_lay.addWidget(self._chk_tasks)
        params_lay.addWidget(self._chk_materials)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Сформировать")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self._generate)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.addWidget(QLabel("Выберите проекты:"))
        root.addWidget(self._list, 1)
        root.addWidget(params)
        root.addWidget(buttons)

    def _selected_ids(self) -> list[int]:
        ids = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                ids.append(int(item.data(Qt.ItemDataRole.UserRole)))
        return ids

    def _load_project_bundle(self, project_id: int) -> dict:
        m = self._manager
        proj_rows = m._fetch_all(
            "select id as project_id, name, address, start_date, end_date, status "
            "from project where id=%s;",
            (project_id,),
            as_dict=True,
        )
        project = proj_rows[0] if proj_rows else {"project_id": project_id}
        project["stages"] = m._fetch_all(
            """
            select s.name as stage_name, ps.status as stage_status,
                ps.planned_start_date as planned_start, ps.planned_end_date as planned_end,
                b.name as brigade_name
            from project_stage ps
            join stage s on s.id = ps.stage_id
            left join brigade b on b.id = ps.brigade_id
            where ps.project_id=%s order by ps.planned_start_date;
            """,
            (project_id,),
            as_dict=True,
        )
        project["tasks"] = m._fetch_all(
            """
            select t.name as task_name, s.name as stage_name, t.status as task_status,
                t.planned_start_datetime as planned_start, t.planned_end_datetime as planned_end
            from task t
            join project_stage ps on ps.id = t.project_stage_id
            join stage s on s.id = ps.stage_id
            where ps.project_id=%s order by t.planned_start_datetime;
            """,
            (project_id,),
            as_dict=True,
        )
        project["materials"] = m._fetch_all(
            """
            select m.name as material_name, s.name as stage_name,
                sm.planned_quantity, sm.actual_quantity
            from stage_material sm
            join material m on m.id = sm.material_id
            join project_stage ps on ps.id = sm.project_stage_id
            join stage s on s.id = ps.stage_id
            where ps.project_id=%s order by s.name, m.name;
            """,
            (project_id,),
            as_dict=True,
        )
        return project

    def _generate(self) -> None:
        ids = self._selected_ids()
        if not ids:
            QMessageBox.warning(self, "Отчёт", "Выберите хотя бы один проект.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчёт",
            "otchet_proekty.docx",
            "Word (*.docx)",
        )
        if not path:
            return
        try:
            bundles = [self._load_project_bundle(pid) for pid in ids]
            build_manager_report(
                Path(path),
                bundles,
                include_stages=self._chk_stages.isChecked(),
                include_tasks=self._chk_tasks.isChecked(),
                include_materials=self._chk_materials.isChecked(),
            )
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать отчёт:\n{exc}")
            return
        QMessageBox.information(self, "Готово", f"Отчёт сохранён:\n{path}")
        self.accept()


class AccountantReportDialog(QDialog):
    def __init__(self, panel, parent=None):
        super().__init__(parent)
        self._panel = panel
        self.setWindowTitle("Формирование отчёта")
        self.resize(480, 420)

        self._list = QListWidget()
        all_employees = panel._employee_combo.currentData() is None
        selected_worker = panel._employee_combo.currentData()
        for i in range(panel._employee_combo.count()):
            text = panel._employee_combo.itemText(i)
            data = panel._employee_combo.itemData(i)
            if data is None:
                continue
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, data)
            checked = all_employees or data == selected_worker
            item.setCheckState(
                Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
            )
            self._list.addItem(item)

        self._date_from = QDateEdit()
        self._date_from.setDate(panel._date_from.date())
        self._date_from.setCalendarPopup(True)
        self._date_from.setDisplayFormat("dd.MM.yyyy")
        self._date_to = QDateEdit()
        self._date_to.setDate(panel._date_to.date())
        self._date_to.setCalendarPopup(True)
        self._date_to.setDisplayFormat("dd.MM.yyyy")

        form = QFormLayout()
        form.addRow("Дата от", self._date_from)
        form.addRow("Дата до", self._date_to)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Сформировать")
        buttons.accepted.connect(self._generate)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.addWidget(QLabel("Сотрудники:"))
        root.addWidget(self._list, 1)
        root.addLayout(form)
        root.addWidget(buttons)

    def _generate(self) -> None:
        worker_ids = []
        names = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                wid = item.data(Qt.ItemDataRole.UserRole)
                if wid is not None:
                    worker_ids.append(int(wid))
                names.append(item.text())
        if not worker_ids:
            QMessageBox.warning(self, "Отчёт", "Выберите хотя бы одного сотрудника.")
            return

        d_from = self._date_from.date().toPyDate()
        d_to = self._date_to.date().toPyDate()
        panel = self._panel
        employee_label = "Все" if len(worker_ids) == self._list.count() else ", ".join(names)
        placeholders = ",".join(["%s"] * len(worker_ids))
        rows = panel._fetch_all(
            f"""
            select concat(w.surname,' ',w.name,' ',ifnull(w.patronymic,'')) as employee,
                p.name as project, s.name as stage, t.name as task,
                wl.hours_spent as hours, wl.work_date
            from work_log wl
            join worker w on w.id = wl.worker_id
            join task t on t.id = wl.task_id
            join project_stage ps on ps.id = t.project_stage_id
            join stage s on s.id = ps.stage_id
            join project p on p.id = ps.project_id
            where wl.worker_id in ({placeholders})
              and wl.work_date between %s and %s
            order by wl.work_date, w.surname, p.name;
            """,
            tuple(worker_ids) + (d_from, d_to),
            as_dict=True,
        )

        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчёт", "otchet_chasy.docx", "Word (*.docx)"
        )
        if not path:
            return
        try:
            build_accountant_report(
                Path(path),
                rows,
                date_from=d_from,
                date_to=d_to,
                employee_label=employee_label,
            )
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
            return
        QMessageBox.information(self, "Готово", f"Отчёт сохранён:\n{path}")
        self.accept()
