# db_connection.py

import pymysql

def create_connection():
    """
    Создаёт и возвращает новое соединение с базой данных.
    """
    connection = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="fischer",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
