from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from ui_assets import apply_window_icon
from ui_theme import (
    configure_table,
    content_margins,
    create_panel_header,
    compact_table_rows,
    empty_state_label,
    metric_card,
    section_label,
    table_fit_content,
    wrap_content_card,
)


class ProjectStagesDialog(QDialog):
    def __init__(self, project_name: str, stages_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Этапы проекта {project_name}")
        self.resize(1500, 920)
        self._build_ui()
        self.set_stages(stages_data or [])
        self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)

    def _build_ui(self):
        self.stage_tabs = QTabWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.stage_tabs)
        self.setLayout(layout)

    @staticmethod
    def _format_value(value):
        if value is None or value == "":
            return "-"
        if isinstance(value, datetime):
            return value.strftime("%d.%m.%Y %H:%M")
        return str(value)

    @staticmethod
    def _to_date(value):
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d.%m.%Y", "%d.%m.%Y %H:%M"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None

    @staticmethod
    def _set_table_cell(table, row_index, col_index, text, color=None):
        item = QTableWidgetItem(text)
        if color:
            item.setForeground(color)
        table.setItem(row_index, col_index, item)

    @staticmethod
    def _highlight_table_row(table, row_index: int, ok: bool | None) -> None:
        if ok is None:
            return
        bg = QColor("#dcfce7") if ok else QColor("#fee2e2")
        for col in range(table.columnCount()):
            item = table.item(row_index, col)
            if item:
                item.setBackground(bg)

    def _add_timing_note(self, parent_layout, planned_end, actual_end):
        planned = self._to_date(planned_end)
        actual = self._to_date(actual_end)
        if not planned or not actual:
            return

        days_diff = (actual - planned).days
        if days_diff > 0:
            text = f"*Позже срока на {days_diff} дн."
        elif days_diff < 0:
            text = f"*Раньше срока на {abs(days_diff)} дн."
        else:
            text = "*В срок"

        note_label = QLabel(text)
        if days_diff > 0:
            note_label.setObjectName("statusLate")
        else:
            note_label.setObjectName("statusOnTime")
        parent_layout.addWidget(note_label)

    def _build_tasks_table(self, tasks):
        table = QTableWidget()
        configure_table(table)
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels(
            [
                "Задача",
                "Описание",
                "Статус",
                "План дата начала",
                "Факт дата начала",
                "Сотрудники",
                "План дата окончания",
                "Факт дата окончания",
            ]
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.setWordWrap(True)
        table.setRowCount(len(tasks))

        for row_index, task in enumerate(tasks):
            planned_end = task.get("planned_end")
            actual_end = task.get("actual_end")
            planned_end_date = self._to_date(planned_end)
            actual_end_date = self._to_date(actual_end)
            end_color = None
            row_ok = None
            actual_end_text = self._format_value(actual_end)
            if planned_end_date and actual_end_date:
                diff = (actual_end_date - planned_end_date).days
                row_ok = diff <= 0
                if diff > 0:
                    end_color = QColor("#b91c1c")
                    actual_end_text += f" (опоздание {diff} дн.)"
                elif diff < 0:
                    end_color = QColor("#15803d")
                    actual_end_text += f" (раньше на {abs(diff)} дн.)"
                else:
                    end_color = QColor("#15803d")
                    actual_end_text += " (в срок)"

            desc = task.get("task_description")
            desc_text = "-" if not desc or str(desc).strip() == "" else self._format_value(desc)

            self._set_table_cell(table, row_index, 0, self._format_value(task.get("task_name")))
            self._set_table_cell(table, row_index, 1, desc_text)
            self._set_table_cell(table, row_index, 2, self._format_value(task.get("task_status")))
            self._set_table_cell(table, row_index, 3, self._format_value(task.get("planned_start")))
            self._set_table_cell(table, row_index, 4, self._format_value(task.get("actual_start")))
            self._set_table_cell(table, row_index, 5, self._format_value(task.get("workers_assigned")))
            self._set_table_cell(table, row_index, 6, self._format_value(planned_end))
            self._set_table_cell(table, row_index, 7, actual_end_text, end_color)

            workers_item = table.item(row_index, 5)
            if workers_item and "\n" in workers_item.text():
                workers_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
                )
            self._highlight_table_row(table, row_index, row_ok)

        compact_table_rows(table)
        total_h = table.horizontalHeader().height() + 8
        for i in range(table.rowCount()):
            total_h += table.rowHeight(i)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        target_h = min(max(total_h, 52), 320)
        table.setMinimumHeight(target_h)
        table.setMaximumHeight(target_h)
        return table

    def _build_materials_table(self, materials):
        table = QTableWidget()
        configure_table(table)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(
            [
                "Используемый материал",
                "Плановое количество",
                "Фактическое количество",
            ]
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.setWordWrap(True)
        table.setRowCount(len(materials))

        for row_index, material in enumerate(materials):
            planned_quantity = material.get("planned_quantity")
            actual_quantity = material.get("actual_quantity")
            unit = self._format_value(material.get("unit"))
            planned_text = "-"
            if planned_quantity is not None:
                planned_text = f"{planned_quantity} {unit}"

            actual_text = "-"
            actual_color = None
            row_ok = None
            if actual_quantity is not None:
                actual_text = f"{actual_quantity} {unit}"
                if planned_quantity is not None:
                    diff = actual_quantity - planned_quantity
                    row_ok = diff <= 0
                    if diff > 0:
                        actual_text += f" (превышение плана на {diff})"
                        actual_color = QColor("#b91c1c")
                    elif diff < 0:
                        actual_text += f" (остаток {abs(diff)})"
                        actual_color = QColor("#15803d")
                    else:
                        actual_color = QColor("#15803d")

            self._set_table_cell(
                table, row_index, 0, self._format_value(material.get("material_name"))
            )
            self._set_table_cell(table, row_index, 1, planned_text)
            self._set_table_cell(table, row_index, 2, actual_text, actual_color)
            self._highlight_table_row(table, row_index, row_ok)

        compact_table_rows(table)
        total_h = table.horizontalHeader().height() + 8
        for i in range(table.rowCount()):
            total_h += table.rowHeight(i)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        target_h = min(max(total_h, 52), 280)
        table.setMinimumHeight(target_h)
        table.setMaximumHeight(target_h)
        return table

    def set_stages(self, stages_data):
        self.stage_tabs.clear()

        if not stages_data:
            empty_widget = QWidget()
            empty_layout = QVBoxLayout()
            empty_layout.addWidget(QLabel("Нет данных по этапам проекта."))
            empty_widget.setLayout(empty_layout)
            self.stage_tabs.addTab(empty_widget, "Этапы")
            return

        for index, stage in enumerate(stages_data, start=1):
            stage_name = self._format_value(stage.get("stage_name"))
            stage_status = self._format_value(stage.get("stage_status"))

            section = QWidget()
            section_layout = QVBoxLayout()
            section_layout.setSpacing(2)
            section_layout.setContentsMargins(4, 4, 4, 4)
            section_layout.addWidget(QLabel(f"Этап: {stage_name} ({stage_status})"))
            section_layout.addSpacing(20)

            planned_start = self._format_value(stage.get("planned_start"))
            planned_end = self._format_value(stage.get("planned_end"))
            actual_start = self._format_value(stage.get("actual_start"))
            actual_end = self._format_value(stage.get("actual_end"))

            dates_row = QHBoxLayout()
            plan_col = QVBoxLayout()
            plan_col.addWidget(QLabel(f"Плановая дата начала: {planned_start}"))
            plan_col.addWidget(QLabel(f"Плановая дата окончания: {planned_end}" ))
            dates_row.addLayout(plan_col)
            dates_row.addSpacing(20)

            fact_col = QVBoxLayout()
            fact_col.addWidget(QLabel(f"Фактическая дата начала: {actual_start}"))
            fact_col.addWidget(QLabel(f"Фактическая дата окончания: {actual_end}"))
            dates_row.addLayout(fact_col)
            dates_row.addStretch()
            section_layout.addLayout(dates_row)
            section_layout.addSpacing(20)


            self._add_timing_note(section_layout, stage.get("planned_end"), stage.get("actual_end"))

            brigade_name = self._format_value(stage.get("brigade_name"))
            foreman_name = self._format_value(stage.get("foreman_full_name"))
            section_layout.addWidget(
                QLabel(f"Бригада: {brigade_name}; бригадир: {foreman_name}")
            )
            section_layout.addSpacing(20)


            tasks = stage.get("tasks", [])
            if tasks:
                section_layout.addWidget(QLabel("Задачи:"))
                tasks_table = self._build_tasks_table(tasks)
                section_layout.addWidget(tasks_table)
            else:
                no_tasks = empty_state_label("Задачи не добавлены")
                no_tasks.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
                section_layout.addWidget(no_tasks, alignment=Qt.AlignmentFlag.AlignLeft)
            section_layout.addSpacing(20)


            materials = stage.get("materials", [])
            if materials:
                section_layout.addWidget(QLabel("Материалы:"))
                materials_table = self._build_materials_table(materials)
                section_layout.addWidget(materials_table)
            else:
                no_materials = empty_state_label("Материалы не добавлены")
                no_materials.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
                section_layout.addWidget(no_materials, alignment=Qt.AlignmentFlag.AlignLeft)

            section.setLayout(section_layout)
            section_layout.addStretch()
            self.stage_tabs.addTab(section, f"{index}. {stage_name} [{stage_status}]")

class DirectorPanelWindow(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self._stages_dialog = None
        self.setWindowTitle("Панель директора")
        self._build_ui()
        apply_window_icon(self)
        self._load_all_data()
        self.showMaximized()

    def _build_ui(self):
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_margins(content_layout, 16, 12)
        content_layout.addWidget(
            create_panel_header(
                "Панель директора",
                "Обзор проектов и показателей эффективности",
                on_logout=self._logout,
            )
        )

        metrics_host = QWidget()
        metrics_layout = QVBoxLayout(metrics_host)
        metrics_layout.setSpacing(14)

        self._metric_labels = {}

        projects_title = section_label("Проекты")
        metrics_layout.addWidget(projects_title)
        projects_grid = QGridLayout()
        projects_grid.setHorizontalSpacing(12)
        projects_grid.setVerticalSpacing(12)
        for i, (caption, key) in enumerate(
            [
                ("Всего проектов", "projects_total"),
                ("Планируется", "projects_planned"),
                ("В работе", "projects_active"),
                ("Завершено", "projects_done"),
                ("В срок, %", "projects_on_time"),
            ]
        ):
            card, val_lbl = metric_card(caption)
            self._metric_labels[key] = val_lbl
            projects_grid.addWidget(card, 0, i)
        metrics_layout.addLayout(projects_grid)

        tasks_title = section_label("Задачи")
        metrics_layout.addWidget(tasks_title)
        tasks_grid = QGridLayout()
        tasks_grid.setHorizontalSpacing(12)
        tasks_grid.setVerticalSpacing(12)
        for i, (caption, key) in enumerate(
            [
                ("Всего задач", "tasks_total"),
                ("Планируется", "tasks_planned"),
                ("В работе", "tasks_active"),
                ("Завершено", "tasks_done"),
                ("В срок, %", "tasks_on_time"),
            ]
        ):
            card, val_lbl = metric_card(caption)
            self._metric_labels[key] = val_lbl
            tasks_grid.addWidget(card, 0, i)
        metrics_layout.addLayout(tasks_grid)

        workers_title = section_label("Сотрудники")
        metrics_layout.addWidget(workers_title)
        workers_grid = QGridLayout()
        workers_grid.setHorizontalSpacing(12)
        workers_grid.setVerticalSpacing(12)
        for i, (caption, key) in enumerate(
            [
                ("Сотрудников", "workers_total"),
                ("В работе", "workers_active"),
                ("Средняя нагрузка, ч", "workers_avg"),
            ]
        ):
            card, val_lbl = metric_card(caption)
            self._metric_labels[key] = val_lbl
            workers_grid.addWidget(card, 0, i)
        metrics_layout.addLayout(workers_grid)

        content_layout.addWidget(wrap_content_card(metrics_host))

        tabs = QTabWidget()
        self.projects_table = self._create_projects_table()
        self.kpi_table = self._create_kpi_table()

        tabs.addTab(self.projects_table, "Проекты")
        tabs.addTab(self.kpi_table, "KPI")

        content_layout.addWidget(tabs)
        scroll.setWidget(content)
        root_layout.addWidget(scroll, 1)
        self.setLayout(root_layout)

    def _logout(self):
        from audit_service import record_logout
        from windows.auth_window import AuthWindow

        username = self.db._active_config.get("user")
        if username:
            record_logout(self.db, username, "Выход (директор)")
        self._auth_window = AuthWindow()
        self._auth_window.showMaximized()
        self.close()

    def _create_projects_table(self):
        table = QTableWidget()
        configure_table(table, sortable=False)
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(
            [
                "Название",
                "Адрес",
                "Дата начала",
                "Дата окончания",
                "Статус",
                "Текущий этап",
            ]
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.setWordWrap(True)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        return table

    def _create_kpi_table(self):
        table = QTableWidget()
        configure_table(table)
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ["Фамилия", "Имя", "Выполнено задач", "Рабочие часы", "KPI"]
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.setWordWrap(True)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        return table

    def _load_all_data(self):
        self._update_metrics()
        self._populate_projects_table()
        self._populate_kpi_table()

    @staticmethod
    def _display_value(value):
        if value is None or value == "":
            return "-"
        return str(value)

    @staticmethod
    def _set_pct_metric(label: QLabel, pct) -> None:
        if pct is None:
            label.setText("—")
            label.setStyleSheet("")
            return
        label.setText(f"{pct}%")
        color = "#15803d" if pct > 85 else "#b91c1c"
        label.setStyleSheet(f"color: {color}; font-size: 22pt; font-weight: 700;")

    def _update_metrics(self):
        metrics = self.load_dashboard_metrics()
        if not metrics:
            return

        pct = metrics.get("projects_on_time_pct")
        tpct = metrics.get("tasks_on_time_pct")
        avg = metrics.get("avg_load")
        mapping = {
            "projects_total": metrics.get("projects", "—"),
            "projects_planned": metrics.get("planned", "—"),
            "projects_active": metrics.get("in_progress", "—"),
            "projects_done": metrics.get("completed", "—"),
            "tasks_total": metrics.get("total_tasks", "—"),
            "tasks_planned": metrics.get("tasks_planned", "—"),
            "tasks_active": metrics.get("tasks_in_progress", "—"),
            "tasks_done": metrics.get("tasks_completed", "—"),
            "workers_total": metrics.get("total_workers", "—"),
            "workers_active": metrics.get("active_workers", "—"),
            "workers_avg": "—" if avg is None else f"{avg}",
        }
        for key, lbl in self._metric_labels.items():
            if key in ("projects_on_time", "tasks_on_time"):
                continue
            lbl.setText(str(mapping.get(key, "—")))
            lbl.setStyleSheet("")

        self._set_pct_metric(self._metric_labels["projects_on_time"], pct)
        self._set_pct_metric(self._metric_labels["tasks_on_time"], tpct)

    def _populate_projects_table(self):
        projects = self.load_projects() or []
        self.projects_table.setRowCount(len(projects))
        for row_index, project in enumerate(projects):
            self.projects_table.setItem(
                row_index, 0, QTableWidgetItem(self._display_value(project.get("name")))
            )
            self.projects_table.setItem(
                row_index, 1, QTableWidgetItem(self._display_value(project.get("address")))
            )
            self.projects_table.setItem(
                row_index, 2, QTableWidgetItem(self._display_value(project.get("start_date")))
            )
            self.projects_table.setItem(
                row_index, 3, QTableWidgetItem(self._display_value(project.get("end_date")))
            )
            self.projects_table.setItem(
                row_index, 4, QTableWidgetItem(self._display_value(project.get("status")))
            )

            stage_info = QLabel(self._display_value(project.get("stage_info")))
            stage_info.setWordWrap(True)
            stage_btn = QPushButton("...")
            stage_btn.setToolTip("Открыть детали этапов")
            stage_btn.clicked.connect(
                lambda _checked=False, p=project: self._open_project_stages_dialog(p)
            )
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(4, 2, 4, 2)
            button_layout.setSpacing(8)
            button_layout.addWidget(stage_info, 1)
            button_layout.addWidget(stage_btn)
            self.projects_table.setCellWidget(row_index, 5, button_container)
        QTimer.singleShot(0, self._after_projects_table_update)

    def _after_projects_table_update(self):
        table_fit_content(self.projects_table)

    def _populate_kpi_table(self):
        kpi_data = self.load_kpi() or []
        self.kpi_table.setRowCount(len(kpi_data))
        for row_index, item in enumerate(kpi_data):
            self.kpi_table.setItem(
                row_index, 0, QTableWidgetItem(self._display_value(item.get("last_name")))
            )
            self.kpi_table.setItem(
                row_index, 1, QTableWidgetItem(self._display_value(item.get("first_name")))
            )
            self.kpi_table.setItem(
                row_index, 2, QTableWidgetItem(self._display_value(item.get("completed_tasks")))
            )
            self.kpi_table.setItem(row_index, 3, QTableWidgetItem(self._display_value(item.get("hours"))))
            kpi_val = item.get("kpi")
            self.kpi_table.setItem(row_index, 4, QTableWidgetItem(self._display_value(kpi_val)))
            try:
                kpi_num = float(kpi_val)
            except (TypeError, ValueError):
                kpi_num = None
            if kpi_num is not None and kpi_num > 1:
                bg = QColor("#dcfce7")
                for col in range(self.kpi_table.columnCount()):
                    cell = self.kpi_table.item(row_index, col)
                    if cell:
                        cell.setBackground(bg)
        QTimer.singleShot(0, self._after_kpi_table_update)

    def _after_kpi_table_update(self):
        table_fit_content(self.kpi_table)

    def _open_project_stages_dialog(self, project: dict) -> None:
        project_name = str(project.get("name", ""))
        project_id = project.get("project_id")
        if project_id is None:
            return
        stages = self.load_project_stages(project_id) or []
        self._stages_dialog = ProjectStagesDialog(project_name, stages, parent=self)
        self._stages_dialog.exec()

    def _fetch_all(self, query, params=None, as_dict = False):
        connection = self.db.connect()
        if not connection:
            return []

        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            while cursor.nextset():
                pass
            if not as_dict:
                return rows
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except Exception as exc:
            print(f"Ошибка выполнения запроса: {exc}")
            return []
        finally:
            if cursor:
                cursor.close()

    def load_dashboard_metrics(self):
        metrics_rows = self._fetch_all(
            """
            select
                count(id) as projects,
                sum(case when lower(status) = 'в работе' then 1 else 0 end) as in_progress,
                sum(case when lower(status) = 'завершен' then 1 else 0 end) as completed,
                sum(case when lower(status) = 'планируется' then 1 else 0 end) as planned
            from project;
            """,
            as_dict=True,
        )

        # Процент проектов, завершённых вовремя (факт конец <= план конец последнего этапа)
        on_time_rows = self._fetch_all(
            """
            select
                count(*) as total_done,
                sum(case when p.end_date <= last_stage.planned_end_date then 1 else 0 end) as on_time
            from project p
            join (
                select project_id, max(planned_end_date) as planned_end_date
                from project_stage
                group by project_id
            ) last_stage on last_stage.project_id = p.id
            where lower(p.status) = 'завершен'
              and p.end_date is not null;
            """,
            as_dict=True,
        )

        # Задачи: всего, в работе, завершены, планируются
        tasks_rows = self._fetch_all(
            """
            select
                count(id) as total_tasks,
                sum(case when lower(status) = 'в работе' then 1 else 0 end) as tasks_in_progress,
                sum(case when lower(status) = 'завершена' then 1 else 0 end) as tasks_completed,
                sum(case when lower(status) = 'планируется' then 1 else 0 end) as tasks_planned
            from task;
            """,
            as_dict=True,
        )

        # Процент задач, завершённых вовремя (факт конец <= план конец)
        tasks_on_time_rows = self._fetch_all(
            """
            select
                count(*) as total_done,
                sum(case when actual_end_datetime <= planned_end_datetime then 1 else 0 end) as on_time
            from task
            where lower(status) = 'завершена'
              and actual_end_datetime is not null
              and planned_end_datetime is not null;
            """,
            as_dict=True,
        )

        # Сотрудники: всего, сейчас в работе (назначены на задачу со статусом "В работе")
        workers_rows = self._fetch_all(
            """
            select
                count(distinct w.id) as total_workers,
                count(distinct active.worker_id) as active_workers
            from worker w
            left join (
                select distinct wl.worker_id
                from work_log wl
                join task t on t.id = wl.task_id
                where lower(t.status) = 'в работе'
            ) active on active.worker_id = w.id;
            """,
            as_dict=True,
        )

        # Средняя нагрузка: среднее кол-во активных задач на активного сотрудника
        avg_load_rows = self._fetch_all(
            """
            select
                avg(cnt) as avg_load
            from (
                select wl.worker_id, count(distinct wl.task_id) as cnt
                from work_log wl
                join task t on t.id = wl.task_id
                where lower(t.status) = 'в работе'
                group by wl.worker_id
            ) sub;
            """,
            as_dict=True,
        )

        metrics = metrics_rows[0] if metrics_rows else {}
        on_time = on_time_rows[0] if on_time_rows else {}
        tasks = tasks_rows[0] if tasks_rows else {}
        tasks_ot = tasks_on_time_rows[0] if tasks_on_time_rows else {}
        workers = workers_rows[0] if workers_rows else {}
        avg_load = avg_load_rows[0] if avg_load_rows else {}

        # Процент проектов вовремя
        total_done = on_time.get("total_done") or 0
        on_time_count = on_time.get("on_time") or 0
        projects_on_time_pct = round(on_time_count / total_done * 100) if total_done else None

        # Процент задач вовремя
        tasks_done = tasks_ot.get("total_done") or 0
        tasks_on_time_count = tasks_ot.get("on_time") or 0
        tasks_on_time_pct = round(tasks_on_time_count / tasks_done * 100) if tasks_done else None

        avg_load_val = avg_load.get("avg_load")
        avg_load_fmt = f"{float(avg_load_val):.1f}" if avg_load_val is not None else None

        return {
            "projects": metrics.get("projects", 0),
            "in_progress": metrics.get("in_progress", 0),
            "completed": metrics.get("completed", 0),
            "planned": metrics.get("planned", 0),
            "projects_on_time_pct": projects_on_time_pct,
            "total_tasks": tasks.get("total_tasks", 0),
            "tasks_in_progress": tasks.get("tasks_in_progress", 0),
            "tasks_completed": tasks.get("tasks_completed", 0),
            "tasks_planned": tasks.get("tasks_planned", 0),
            "tasks_on_time_pct": tasks_on_time_pct,
            "total_workers": workers.get("total_workers", 0),
            "active_workers": workers.get("active_workers", 0),
            "avg_load": avg_load_fmt,
        }

    def load_projects(self):
        return self._fetch_all(
            """
            select
                p.id as project_id,
                p.name,
                p.address,
                p.start_date,
                p.end_date,
                p.status,
                coalesce(
                case
                    when p.status = 'Планируется' then '-'
                    when exists (
                        select 1
                        from project_stage ps2
                        where ps2.project_id = p.id
                          and ps2.status = 'В работе'
                    ) then (
                        select concat(s.name, ' (', ps3.status, ')')
                        from project_stage ps3
                        join stage s on ps3.stage_id = s.id
                        where ps3.project_id = p.id
                          and ps3.status = 'В работе'
                        limit 1
                    )
                    else (
                        select concat(s.name, ' (', ps4.status, ')')
                        from project_stage ps4
                        join stage s on ps4.stage_id = s.id
                        where ps4.project_id = p.id
                          and ps4.actual_end_date is not null
                        order by ps4.actual_end_date desc
                        limit 1
                    )
                end, '-') as stage_info
            from project p
            order by p.id;
            """,
            as_dict=True,
        )

    def load_kpi(self):
        rows = self._fetch_all("call get_kpi_with_log();")
        out = []
        for row in rows:
            row_values = list(row)
            out.append(
                {
                    "id": row_values[0] if len(row_values) > 0 else "",
                    "last_name": row_values[1] if len(row_values) > 1 else "",
                    "first_name": row_values[2] if len(row_values) > 2 else "",
                    "completed_tasks": row_values[3] if len(row_values) > 3 else "",
                    "hours": row_values[4] if len(row_values) > 4 else "",
                    "kpi": row_values[5] if len(row_values) > 5 else "",
                }
            )
        return out

    def load_project_stages(self, project_id):
        stages = self._fetch_all(
            """
            select
                ps.id as project_stage_id,
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
        for stage in stages:
            stage_id = stage.get("project_stage_id")
            stage["tasks"] = self.load_stage_tasks(stage_id)
            stage["materials"] = self.load_stage_materials(stage_id)
        return stages

    def load_stage_tasks(self, project_stage_id):
        return self._fetch_all(
            """
            select
                t.name as task_name,
                t.description as task_description,
                t.planned_start_datetime as planned_start,
                t.actual_start_datetime as actual_start,
                t.planned_end_datetime as planned_end,
                t.actual_end_datetime as actual_end,
                t.status as task_status,
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
            left join work_log wl on t.id = wl.task_id
            left join worker w on wl.worker_id = w.id
            where t.project_stage_id = %s
            group by t.id, t.name, t.description, t.planned_start_datetime,
                     t.actual_start_datetime, t.planned_end_datetime,
                     t.actual_end_datetime, t.status
            order by t.planned_start_datetime;
            """,
            (project_stage_id,),
            as_dict=True,
        )

    def load_stage_materials(self, project_stage_id):
        return self._fetch_all(
            """
            select
                m.name as material_name,
                m.unit_of_measurement as unit,
                sm.planned_quantity as planned_quantity,
                sm.actual_quantity as actual_quantity
            from project_stage ps
            join stage s on ps.stage_id = s.id
            join stage_material sm on ps.id = sm.project_stage_id
            join material m on sm.material_id = m.id
            where ps.id = %s
            order by m.name;
            """,
            (project_stage_id,),
            as_dict=True,
        )