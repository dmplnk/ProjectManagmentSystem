from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui_assets import apply_window_icon, load_logo_pixmap
from ui_theme import content_margins, style_primary_button

from config import DBA_PASSWORD, DBA_USER
from db import MySQLConnection
from audit_service import set_user_offline, set_user_online, write_audit_event
from windows.director_panel_window import DirectorPanelWindow
from windows.manager_panel_window import ManagerPanelWindow
from windows.foreman_panel_window import ForemanPanelWindow
from windows.employee_panel_window import EmployeePanelWindow
from windows.accountant_panel_window import AccountantPanelWindow
from windows.admin_panel_window import AdminPanelWindow


class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = MySQLConnection()
        self.director_window = None
        self.manager_window = None
        self.foreman_window = None
        self.employee_window = None
        self.accountant_window = None
        self.admin_window = None
        self._login_succeeded = False
        self._loading_timer = QTimer(self)
        self._loading_timer.timeout.connect(self._animate_login_button)
        self._loading_step = 0
        self.setObjectName("authWindow")
        self.setWindowTitle("Авторизация — управление проектами")
        self._build_ui()
        apply_window_icon(self)

    def showEvent(self, event):
        super().showEvent(event)
        self.showMaximized()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        content_margins(outer, 32, 16)
        outer.addStretch(1)

        card = QFrame()
        card.setObjectName("authCard")
        card_layout = QVBoxLayout(card)
        content_margins(card_layout, 28, 18)

        logo = load_logo_pixmap(80)
        if logo is not None:
            logo_lbl = QLabel()
            logo_lbl.setPixmap(logo)
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(logo_lbl)

        title = QLabel("Вход в систему")
        title.setObjectName("authTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("Управление фармацевтическими инженерными проектами")
        subtitle.setObjectName("authSubtitle")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.login_input = QLineEdit("dba_user")
        self.login_input.setPlaceholderText("Введите логин")
        form_layout.addRow("Логин", self.login_input)

        self.password_input = QLineEdit("password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.returnPressed.connect(self._handle_login)
        form_layout.addRow("Пароль", self.password_input)

        self.login_btn = QPushButton("Войти")
        style_primary_button(self.login_btn)
        self.login_btn.clicked.connect(self._handle_login)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
        card_layout.addLayout(form_layout)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.login_btn)

        outer.addWidget(
            card,
            alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        )
        outer.addStretch(1)

    def _validate_inputs(self, login, password):
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин.")
            return False
        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль.")
            return False

        return True

    def _handle_login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not self._validate_inputs(login, password):
            return
        self._set_loading(True)
        try:
            role = self.db.get_user_role(login, password)
        except RuntimeError as exc:
            self._set_loading(False)
            QMessageBox.critical(self, "Ошибка БД", str(exc))
            return
        if role is None:
            self._set_loading(False)
            write_audit_event(
                self.db,
                "login_failed",
                actor_username=login,
                details="Неверный логин или пароль",
                success=False,
            )
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")
            return

        write_audit_event(
            self.db,
            "login_success",
            actor_username=login,
            details=f"Роль: {role}",
            success=True,
        )
        set_user_online(self.db, login, role)

        worker_id = self._get_worker_id_from_users(login)

        self._set_loading(False)
        # QMessageBox.information(self, "Успех", "Авторизация выполнена успешно.")
        self._login_succeeded = True

        if str(role).strip().casefold() == "dba":
            dba_password = password if login == DBA_USER else DBA_PASSWORD
            if not dba_password:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Для панели администратора нужен пароль пользователя {DBA_USER} "
                    f"(вход под этим логином или DB_DBA_PASSWORD в .env).",
                )
                return
            self.db.ensure_connection_user(DBA_USER, dba_password)
            self.admin_window = AdminPanelWindow(self.db, DBA_USER, dba_password)
            self.admin_window.show()
            self.close()
            return

        self.db.set_connection_user(login, password)

        if str(role).strip().casefold() == "director":
            self.director_window = DirectorPanelWindow(self.db)
            # self.director_window.show()
            self.close()
            return

        if str(role).strip().casefold() == "project_manager":
            self.manager_window = ManagerPanelWindow(self.db)
            # self.manager_window.show()
            self.close()
            return

        if str(role).strip().casefold() == "foreman":
            if not worker_id:
                QMessageBox.warning(self, "Ошибка", "Для бригадира не найден worker_id в users.")
                return
            self.foreman_window = ForemanPanelWindow(self.db, worker_id)
            # self.foreman_window.show()
            self.close()
            return

        if str(role).strip().casefold() == "employee":
            if not worker_id:
                QMessageBox.warning(self, "Ошибка", "Для сотрудника не найден worker_id в users.")
                return
            self.employee_window = EmployeePanelWindow(self.db, worker_id)
            # self.employee_window.show()
            self.close()
            return

        if str(role).strip().casefold() == "accountant":
            self.accountant_window = AccountantPanelWindow(self.db)
            # self.accountant_window.show()
            self.close()
            return

    def closeEvent(self, event):
        if not self._login_succeeded:
            login = self.login_input.text().strip()
            if login:
                write_audit_event(
                    self.db,
                    "logout",
                    actor_username=login,
                    details="Закрытие окна входа без входа",
                )
        self.db.close()
        super().closeEvent(event)

    def _set_loading(self, value: bool):
        if value:
            self.login_btn.setEnabled(False)
            self.login_input.setEnabled(False)
            self.password_input.setEnabled(False)
            self._loading_step = 0
            self.login_btn.setText("Вход")
            # self._loading_timer.start(250)
            return
        self._loading_timer.stop()
        self.login_btn.setEnabled(True)
        self.login_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.login_btn.setText("Войти")

    def _animate_login_button(self):
        self._loading_step = (self._loading_step + 1) % 4
        dots = "." * self._loading_step
        self.login_btn.setText(f"Вход{dots}")

    def _get_worker_id_from_users(self, login: str):
        con = self.db.connect()
        if not con:
            return None
        cursor = None
        try:
            cursor = con.cursor()
            cursor.execute(
                "select worker_id from users where username = %s limit 1;",
                (login,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return row[0]
        except Exception:
            return None
        finally:
            if cursor:
                cursor.close()
