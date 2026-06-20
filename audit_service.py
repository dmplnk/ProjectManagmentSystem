"""Запись событий в audit_log и обновление user_presence."""

from typing import Optional

EVENT_LABELS = {
    "login_success": "Успешный вход",
    "login_failed": "Неудачный вход",
    "logout": "Выход",
    "user_create": "Создание пользователя",
    "user_update": "Изменение пользователя",
    "user_delete": "Удаление пользователя",
    "data_change": "Изменение данных",
    "data_change_declined": "Отмена изменения",
    "data_change_failed": "Ошибка изменения данных",
}


def actor_from_db(db) -> Optional[str]:
    cfg = getattr(db, "_active_config", None) or {}
    user = cfg.get("user")
    return str(user) if user else None


def log_data_change(
    db,
    details: str,
    *,
    actor_username: Optional[str] = None,
    success: bool = True,
) -> bool:
    if actor_username is None:
        actor_username = actor_from_db(db)
    event_type = "data_change" if success else "data_change_failed"
    return write_audit_event(
        db,
        event_type,
        actor_username=actor_username,
        details=details,
        success=success,
    )


def log_data_declined(
    db,
    details: str,
    *,
    actor_username: Optional[str] = None,
) -> bool:
    if actor_username is None:
        actor_username = actor_from_db(db)
    return write_audit_event(
        db,
        "data_change_declined",
        actor_username=actor_username,
        details=details,
        success=False,
    )


def _execute(db, query: str, params=()) -> bool:
    con = db.connect()
    if not con:
        return False
    cursor = None
    try:
        cursor = con.cursor()
        cursor.execute(query, params)
        con.commit()
        return True
    except Exception as exc:
        print(f"audit_service: {exc}")
        try:
            con.rollback()
        except Exception:
            pass
        return False
    finally:
        if cursor:
            cursor.close()


def write_audit_event(
    db,
    event_type: str,
    actor_username: Optional[str] = None,
    target_username: Optional[str] = None,
    details: Optional[str] = None,
    success: bool = True,
) -> bool:
    return _execute(
        db,
        """
        INSERT INTO audit_log (event_type, actor_username, target_username, details, success)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (event_type, actor_username, target_username, details, 1 if success else 0),
    )


def _fetch_user_id(db, username: str) -> Optional[int]:
    con = db.connect()
    if not con:
        return None
    cursor = None
    try:
        cursor = con.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s LIMIT 1", (username,))
        row = cursor.fetchone()
        return int(row[0]) if row else None
    except Exception as exc:
        print(f"audit_service: {exc}")
        return None
    finally:
        if cursor:
            cursor.close()


def set_user_online(db, username: str, role: Optional[str] = None) -> bool:
    user_id = _fetch_user_id(db, username)
    if user_id is None:
        return False
    return _execute(
        db,
        """
        INSERT INTO user_presence (user_id, is_online, last_seen_at, last_role)
        VALUES (%s, 1, NOW(), %s)
        ON DUPLICATE KEY UPDATE
            is_online = 1,
            last_seen_at = NOW(),
            last_role = VALUES(last_role);
        """,
        (user_id, role),
    )


def record_logout(db, username: str, details: str = "Выход из системы") -> None:
    write_audit_event(db, "logout", actor_username=username, details=details)
    set_user_offline(db, username)


def set_user_offline(db, username: str) -> bool:
    user_id = _fetch_user_id(db, username)
    if user_id is None:
        return False
    return _execute(
        db,
        """
        INSERT INTO user_presence (user_id, is_online, last_logout_at)
        VALUES (%s, 0, NOW())
        ON DUPLICATE KEY UPDATE
            is_online = 0,
            last_logout_at = NOW();
        """,
        (user_id,),
    )
