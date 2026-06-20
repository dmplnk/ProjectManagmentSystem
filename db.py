import os
import re
from cryptography.fernet import Fernet
import pymysql
from pymysql import Error

from config import DB_CONFIG

_ALLOWED_APP_ROLES = (
    "dba",
    "director",
    "project_manager",
    "foreman",
    "accountant",
    "employee",
)

APP_ROLE_LABELS = {
    "dba": "Администратор",
    "director": "Директор",
    "project_manager": "Менеджер проектов",
    "foreman": "Бригадир",
    "accountant": "Бухгалтер",
    "employee": "Рабочий",
}

_SPECIALTY_TO_APP_ROLE = {
    "администратор": "dba",
    "директор": "director",
    "менеджер проектов": "project_manager",
    "проектный менеджер": "project_manager",
    "бухгалтер": "accountant",
    "бригадир": "foreman",
    "рабочий": "employee",
    "сотрудник": "employee",
}


def app_role_from_specialty_name(specialty_name) -> str | None:
    if not specialty_name:
        return None
    key = str(specialty_name).strip().casefold()
    if key in _SPECIALTY_TO_APP_ROLE:
        return _SPECIALTY_TO_APP_ROLE[key]
    for pattern, role in _SPECIALTY_TO_APP_ROLE.items():
        if pattern in key:
            return role
    return "employee"


def role_label_from_specialty_name(specialty_name) -> str:
    app_role = app_role_from_specialty_name(specialty_name)
    if app_role:
        return APP_ROLE_LABELS.get(app_role, app_role)
    if specialty_name:
        return str(specialty_name).strip()
    return "не определена"

MANAGEABLE_APP_ROLES = (
    "director",
    "project_manager",
    "foreman",
    "accountant",
    "employee",
)


class MySQLConnection:
    def __init__(self):
        self.con = None
        self._default_config = DB_CONFIG.copy()
        self._active_config = DB_CONFIG.copy()

    def connect(self):
        try:
            if self.con:
                try:
                    self.con.ping(reconnect=True)
                    return self.con
                except Exception:
                    self.con = None
            self.con = pymysql.connect(
                host=self._active_config.get("host"),
                user=self._active_config.get("user"),
                password=self._active_config.get("password"),
                database=self._active_config.get("database"),
                cursorclass=pymysql.cursors.Cursor
            )
            return self.con
        except Exception as e:
            print("Ошибка подключения к БД :", e)
            return None

    def close(self):
        if self.con:
            self.con.close()
            self.con = None

    def set_connection_user(self, username, password):
        self.close()
        self._active_config["user"] = username
        self._active_config["password"] = password

    def reset_connection_user(self):
        self.close()
        self._active_config["user"] = self._default_config.get("user")
        self._active_config["password"] = self._default_config.get("password")

    @staticmethod
    def _parse_role_names_from_grant_lines(grant_rows):
        names = []
        for row in grant_rows:
            if not row:
                continue
            grant = row[0]
            if not grant or not isinstance(grant, str):
                continue
            upper = grant.upper()
            if upper.startswith("GRANT USAGE ON"):
                continue
            for m in re.finditer(r"GRANT\s+`([^`]+)`@`[^`]+`\s+TO\s+", grant, re.I):
                names.append(m.group(1))
            for m in re.finditer(r"GRANT\s+'([^']+)'@'[^']+'\s+TO\s+", grant, re.I):
                names.append(m.group(1))
            for m in re.finditer(r"`([^`]+)`@`%`", grant):
                names.append(m.group(1))
            for m in re.finditer(r"'([^']+)'@'%'", grant):
                names.append(m.group(1))
            for m in re.finditer(r"DEFAULT\s+ROLE\s+`([^`]+)`", grant, re.I):
                names.append(m.group(1))
            for m in re.finditer(r"DEFAULT\s+ROLE\s+'([^']+)'", grant, re.I):
                names.append(m.group(1))
        return list(dict.fromkeys(names))

    @classmethod
    def _pick_app_role(cls, mysql_role_names):
        for raw in mysql_role_names:
            key = str(raw).strip().casefold()
            for allowed in _ALLOWED_APP_ROLES:
                if allowed.casefold() == key:
                    return allowed
        return None

    @staticmethod
    def _quote_mysql_account_part(value: str) -> str:
        return value.replace("\\", "\\\\").replace("'", "''")

    @classmethod
    def _mysql_user_at_host(cls, login: str, host: str) -> str:
        return (
            f"'{cls._quote_mysql_account_part(login)}'"
            f"@'{cls._quote_mysql_account_part(host)}'"
        )

    def _account_host_candidates(self):
        explicit = (os.getenv("DB_ACCOUNT_HOST") or "").strip()
        if explicit:
            return [explicit]
        return ["localhost", "%", "127.0.0.1"]

    def get_user_role(self, login, password):
        self.reset_connection_user()
        cursor = None
        try:
            if not self.connect():
                raise RuntimeError(
                    "Не удалось подключиться к БД под пользователем по умолчанию (.env)."
                )
            cursor = self.con.cursor()

            cursor.execute(
                "SELECT password FROM users WHERE username = %s LIMIT 1",
                (login,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            stored = row[0]
            fernet = Fernet(os.getenv("FERNET_KEY").encode())

            if stored is None:
                return None
            stored_str = stored if isinstance(stored, str) else str(stored)
            if stored_str.startswith("gAAAAA"):
                # новые Fernet-зашифрованные пароли
                try:
                    decrypted = fernet.decrypt(stored_str.encode()).decode()
                except Exception:
                    return None
                if decrypted != password:
                    return None
            else:
                # plaintext (совсем старые записи)
                if stored_str != password:
                    return None

            # if cursor.fetchone() is None:
            #     return None

            rows = None
            last_error = None
            for host in self._account_host_candidates():
                try:
                    account = self._mysql_user_at_host(login, host)
                    cursor.execute(f"SHOW GRANTS FOR {account}")
                    rows = cursor.fetchall()
                    break
                except pymysql.Error as exc:
                    last_error = exc
                    rows = None
                    continue

            if rows is None:
                raise RuntimeError(
                    "Не удалось выполнить SHOW GRANTS FOR для этого логина. "
                    "Укажите верный хост MySQL-учётной записи в переменной окружения "
                    "DB_ACCOUNT_HOST (например localhost или %). "
                    f"Последняя ошибка: {last_error}"
                )

            mysql_roles = self._parse_role_names_from_grant_lines(rows)
            app_role = self._pick_app_role(mysql_roles)
            if app_role is None:
                allowed = ", ".join(_ALLOWED_APP_ROLES)
                raise RuntimeError(
                    "Для пользователя в MySQL не найдена роль приложения: "
                    f"в GRANT должна быть одна из ролей: {allowed} "
                    "(имя как в списке, без русских синонимов). "
                    "Проверьте: CREATE ROLE / GRANT `имя_роли`@`%` TO пользователю."
                )
            return app_role
        except Error as exc:
            raise RuntimeError(f"MySQL error: {exc}") from exc
        finally:
            if cursor:
                cursor.close()

    def _mysql_hosts_for_login(self, login: str):
        cursor = None
        hosts = []
        try:
            if not self.connect():
                return []
            cursor = self.con.cursor()
            cursor.execute("SELECT Host FROM mysql.user WHERE User = %s", (login,))
            hosts = [row[0] for row in cursor.fetchall()]
        except pymysql.Error:
            hosts = []
        finally:
            if cursor:
                cursor.close()
        if hosts:
            return hosts
        return self._account_host_candidates()

    def _read_mysql_role_grants(self, login: str):
        cursor = None
        try:
            if not self.connect():
                return None
            cursor = self.con.cursor()
            all_role_names = []
            for host in self._mysql_hosts_for_login(login):
                try:
                    account = self._mysql_user_at_host(login, host)
                    cursor.execute(f"SHOW GRANTS FOR {account}")
                    rows = cursor.fetchall()
                except pymysql.Error:
                    continue
                all_role_names.extend(self._parse_role_names_from_grant_lines(rows))
            if not all_role_names:
                return None
            return self._pick_app_role(all_role_names)
        finally:
            if cursor:
                cursor.close()

    def get_mysql_role_for_login(self, login: str):
        return self._read_mysql_role_grants(login)

    def ensure_connection_user(self, username: str, password: str):
        if (
            self._active_config.get("user") != username
            or self._active_config.get("password") != password
        ):
            self.set_connection_user(username, password)
        else:
            self.connect()

    def _execute_admin_ddl(self, query: str, params=()):
        cursor = None
        try:
            if not self.connect():
                raise RuntimeError("Нет подключения к БД.")
            cursor = self.con.cursor()
            cursor.execute(query, params)
            self.con.commit()
            return True
        except Exception as exc:
            if self.con:
                self.con.rollback()
            raise RuntimeError(str(exc)) from exc
        finally:
            if cursor:
                cursor.close()

    def create_mysql_account(self, login: str, password: str, app_role: str):
        login_q = self._quote_mysql_account_part(login)
        pwd_q = self._quote_mysql_account_part(password)
        role_q = self._quote_mysql_account_part(app_role)
        for host in self._account_host_candidates():
            try:
                self._execute_admin_ddl(
                    f"CREATE USER IF NOT EXISTS '{login_q}'@'{host}' "
                    f"IDENTIFIED BY '{pwd_q}'"
                )
                self._execute_admin_ddl(
                    f"GRANT `{role_q}`@`%` TO '{login_q}'@'{host}'"
                )
                self._execute_admin_ddl(
                    f"SET DEFAULT ROLE `{role_q}`@`%` TO '{login_q}'@'{host}'"
                )
            except RuntimeError:
                continue

    def update_mysql_password(self, login: str, password: str):
        login_q = self._quote_mysql_account_part(login)
        pwd_q = self._quote_mysql_account_part(password)
        for host in self._account_host_candidates():
            try:
                self._execute_admin_ddl(
                    f"ALTER USER '{login_q}'@'{host}' IDENTIFIED BY '{pwd_q}'"
                )
            except RuntimeError:
                continue

    def rename_mysql_account(self, old_login: str, new_login: str):
        old_q = self._quote_mysql_account_part(old_login)
        new_q = self._quote_mysql_account_part(new_login)
        for host in self._account_host_candidates():
            try:
                self._execute_admin_ddl(
                    f"RENAME USER '{old_q}'@'{host}' TO '{new_q}'@'{host}'"
                )
            except RuntimeError:
                continue

    def drop_mysql_account(self, login: str):
        login_q = self._quote_mysql_account_part(login)
        for host in self._account_host_candidates():
            try:
                self._execute_admin_ddl(f"DROP USER IF EXISTS '{login_q}'@'{host}'")
            except RuntimeError:
                continue

    def change_mysql_role(self, login: str, new_role: str):
        login_q = self._quote_mysql_account_part(login)
        role_q = self._quote_mysql_account_part(new_role)
        for host in self._account_host_candidates():
            try:
                for old_role in MANAGEABLE_APP_ROLES + ("dba",):
                    old_q = self._quote_mysql_account_part(old_role)
                    try:
                        self._execute_admin_ddl(
                            f"REVOKE `{old_q}`@`%` FROM '{login_q}'@'{host}'"
                        )
                    except RuntimeError:
                        pass
                self._execute_admin_ddl(
                    f"GRANT `{role_q}`@`%` TO '{login_q}'@'{host}'"
                )
                self._execute_admin_ddl(
                    f"SET DEFAULT ROLE `{role_q}`@`%` TO '{login_q}'@'{host}'"
                )
            except RuntimeError:
                continue
