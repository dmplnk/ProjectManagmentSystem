import os
from dotenv import load_dotenv

load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

DBA_USER = (os.getenv("DB_DBA_USER") or "dba_user").strip()
DBA_PASSWORD = os.getenv("DB_DBA_PASSWORD") or ""

ZABBIX_URL = (os.getenv("ZABBIX_URL") or "").strip()