# views/login_view.py

import threading
import time
import flet
from flet import TextField, ElevatedButton, Column, Text, Container, alignment

from db_utils import execute_query

def build_login_view(page, connection, show_message, on_login_success):
    """
    Возвращает контейнер с формой логина (Login + Password).
    :param page: Flet Page
    :param connection: соединение с БД
    :param show_message: функция для отображения сообщений
    :param on_login_success: колбэк, вызываемый при успешном логине
    """

    login_field = TextField(label="Логин", width=200)
    password_field = TextField(label="Пароль", password=True, can_reveal_password=True, width=200)

    def login_action(e):
        user_login = login_field.value.strip()
        user_password = password_field.value.strip()

        if not user_login or not user_password:
            show_message("Введите логин и пароль", error=True)
            return

        query = "SELECT * FROM Employees WHERE login=%s AND password=%s"
        res = execute_query(connection, query, (user_login, user_password))

        if res and len(res) > 0:
            show_message("Успешный вход!")
            on_login_success()  # Переключаемся на следующий экран
        else:
            show_message("Неверный логин или пароль", error=True)

    login_button = ElevatedButton("Войти", on_click=login_action)

    login_view = Container(
        content=Column(
            [
                Text("Авторизация", size=30, weight="bold"),
                login_field,
                password_field,
                login_button
            ],
            alignment="center",
            horizontal_alignment="center",
            spacing=20
        ),
        expand=True,
        alignment=alignment.center
    )

    return login_view
