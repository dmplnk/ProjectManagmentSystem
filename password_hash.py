from cryptography.fernet import Fernet
import pymysql
import os
from db import MySQLConnection

if __name__ == "__main__":
    fernet = Fernet(os.getenv("FERNET_KEY").encode())

    connection = MySQLConnection().connect()
    cursor = connection.cursor()

    username = input("Введите логин: ")
    password = input("Введите пароль: ")
    worker_id = input("Введите worker_id (или Enter): ") or None

    encrypted_password = fernet.encrypt(password.encode()).decode()

    cursor.execute(
        "INSERT INTO users (username, password, worker_id) VALUES (%s, %s, %s)",
        (username, encrypted_password, worker_id)
    )
    connection.commit()
    print("Пользователь создан.")