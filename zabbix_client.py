import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Optional

MYSQL_TEMPLATE_NAMES = (
    "MySQL by Zabbix agent 2",
    "Template DB MySQL by Zabbix agent 2",
)

MYSQL_METRIC_KEYS = (
    ("mysql.threads.connected", "Подключения (текущие)"),
    ("mysql.questions.rate", "Запросов в секунду (Questions)"),
    ("mysql.queries.rate", "Запросов в секунду (Queries)"),
    ("mysql.connections.rate", "Новых подключений в секунду"),
    ("mysql.threads.running", "Потоков в работе"),
    ("mysql.slow_queries.rate", "Медленных запросов в секунду"),
)


class ZabbixClient:
    def __init__(self, url: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        base = (url or os.getenv("ZABBIX_URL") or "").strip().rstrip("/")
        if base and not base.endswith("/api_jsonrpc.php"):
            self.api_url = f"{base}/api_jsonrpc.php"
        else:
            self.api_url = base or ""
        self.user = (user or os.getenv("ZABBIX_USER") or "").strip()
        self.password = password if password is not None else os.getenv("ZABBIX_PASSWORD", "")
        self._auth_token: Optional[str] = None
        self._request_id = 0
        self._use_bearer = True

    def is_configured(self) -> bool:
        return bool(self.api_url and self.user and self.password)

    def _call(self, method: str, params: Optional[dict] = None, use_auth: bool = True) -> Any:
        if not self.api_url:
            raise RuntimeError("Не задан ZABBIX_URL в .env")
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._request_id,
        }
        headers = {"Content-Type": "application/json"}
        if use_auth and method != "user.login" and self._auth_token:
            if self._use_bearer:
                headers["Authorization"] = f"Bearer {self._auth_token}"
            else:
                payload["auth"] = self._auth_token

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.api_url,
            data=data,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Не удалось подключиться к Zabbix: {exc}") from exc

        if "error" in body:
            err = body["error"]
            code = err.get("code", "")
            message = err.get("message", str(err))
            data_err = err.get("data", "")
            detail = message
            if data_err:
                detail += f" ({data_err})"
            if code:
                detail = f"[{code}] {detail}"
            raise RuntimeError(f"Zabbix API: {detail}")
        return body.get("result")

    def login(self):
        self._auth_token = self._call(
            "user.login",
            {"username": self.user, "password": self.password},
            use_auth=False,
        )
        if not self._auth_token:
            raise RuntimeError("Zabbix API: пустой ответ на user.login")
        last_error = None
        for use_bearer in (True, False):
            self._use_bearer = use_bearer
            try:
                self._call("host.get", {"output": ["hostid"], "limit": 1})
                return
            except RuntimeError as exc:
                last_error = exc
        raise last_error or RuntimeError("Вход в Zabbix выполнен, но API-запросы отклоняются")

    def _count_items(self, method: str, params: dict) -> int:
        result = self._call(method, params)
        if result is None:
            return 0
        if isinstance(result, (int, str)):
            try:
                return int(result)
            except (TypeError, ValueError):
                pass
        if isinstance(result, list):
            return len(result)
        return 0

    def _find_mysql_template_id(self) -> str:
        for name in MYSQL_TEMPLATE_NAMES:
            rows = self._call(
                "template.get",
                {"filter": {"name": name}, "output": ["templateid", "name"]},
            )
            if rows:
                return rows[0]["templateid"]
        rows = self._call(
            "template.get",
            {
                "search": {"name": "MySQL by Zabbix agent"},
                "searchWildcardsEnabled": True,
                "output": ["templateid", "name"],
            },
        ) or []
        if rows:
            return rows[0]["templateid"]
        raise RuntimeError(
            "Шаблон «MySQL by Zabbix agent 2» не найден в Zabbix. "
            "Проверьте, что шаблон подключён к хосту."
        )

    def _history_type_for_item(self, value_type) -> int:
        try:
            vt = int(value_type)
        except (TypeError, ValueError):
            return 0
        return {0: 0, 3: 3}.get(vt, 0)

    def fetch_mysql_metrics_last_day(self) -> list[dict]:
        """Метрики MySQL за последние 24 часа для графиков."""
        if not self.is_configured():
            raise RuntimeError(
                "Укажите ZABBIX_URL, ZABBIX_USER и ZABBIX_PASSWORD в файле .env"
            )
        self.login()
        template_id = self._find_mysql_template_id()
        hosts = self._call(
            "host.get",
            {
                "templateids": [template_id],
                "output": ["hostid", "name"],
                "sortfield": "name",
            },
        ) or []
        if not hosts:
            raise RuntimeError("Нет хостов с шаблоном MySQL by Zabbix agent 2")
        host_id = hosts[0]["hostid"]
        host_name = hosts[0].get("name", "")

        items = self._call(
            "item.get",
            {
                "hostids": [host_id],
                "output": ["itemid", "name", "key_", "units", "value_type", "lastvalue"],
                "sortfield": "name",
            },
        ) or []

        key_to_item = {}
        for item in items:
            key = item.get("key_", "")
            for pattern, title in MYSQL_METRIC_KEYS:
                if key == pattern:
                    key_to_item[pattern] = (item, title)
                    break

        if not key_to_item:
            raise RuntimeError(
                f"На хосте «{host_name}» не найдены элементы данных MySQL "
                f"(ожидались ключи: {', '.join(k for k, _ in MYSQL_METRIC_KEYS)})."
            )

        now = int(time.time())
        time_from = now - 86400
        metrics = []
        for pattern, title in MYSQL_METRIC_KEYS:
            if pattern not in key_to_item:
                continue
            item, title = key_to_item[pattern]
            item_id = item["itemid"]
            history_type = self._history_type_for_item(item.get("value_type"))
            hist = self._call(
                "history.get",
                {
                    "output": ["clock", "value"],
                    "history": history_type,
                    "itemids": [item_id],
                    "time_from": time_from,
                    "time_till": now,
                    "sortfield": "clock",
                    "sortorder": "ASC",
                    "limit": 5000,
                },
            ) or []
            points = []
            for row in hist:
                try:
                    points.append((int(row["clock"]), float(row["value"])))
                except (TypeError, ValueError, KeyError):
                    continue
            if not points and item.get("lastvalue") not in (None, ""):
                try:
                    points.append((now, float(item["lastvalue"])))
                except (TypeError, ValueError):
                    pass
            metrics.append(
                {
                    "title": title,
                    "key": pattern,
                    "unit": item.get("units") or "",
                    "host": host_name,
                    "points": points,
                }
            )
        return metrics

    def fetch_summary(self) -> dict:
        if not self.is_configured():
            raise RuntimeError(
                "Укажите ZABBIX_URL, ZABBIX_USER и ZABBIX_PASSWORD в файле .env"
            )
        self.login()
        hosts = self._count_items("host.get", {"output": ["hostid"], "limit": 10000})
        problems = self._count_items(
            "problem.get",
            {"output": ["eventid"], "recent": True, "limit": 10000},
        )
        try:
            triggers = self._count_items(
                "trigger.get",
                {
                    "output": ["triggerid"],
                    "filter": {"value": 1},
                    "skipDependent": True,
                    "limit": 10000,
                },
            )
        except RuntimeError:
            triggers = self._count_items(
                "trigger.get",
                {
                    "output": ["triggerid"],
                    "only_true": 1,
                    "skipDependent": 1,
                    "limit": 10000,
                },
            )
        return {"hosts": hosts, "problems": problems, "triggers": triggers}
