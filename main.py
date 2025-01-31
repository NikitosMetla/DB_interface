# main.py

import flet
from flet import Page, Column, Container, alignment, border, Text
import threading
import time

from db_connection import create_connection
from views.login_view import build_login_view
from views.table_view import build_table_view

def main(page: Page):
    # Настройка страницы
    page.scroll = "auto"
    page.window.full_screen = True
    page.window.maximized = True
    page.theme_mode = "dark"

    # Создаём соединение с БД
    connection = create_connection()

    # Контейнер для сообщений
    messages_container = Column(scroll="auto")
    messages_box = Container(
        content=messages_container,
        padding=10,
        border=border.all(1, "gray"),
        border_radius=10,
        bgcolor="#1E1E1E",
        width=300,
        height=400,
        alignment=alignment.top_center
    )

    def show_message(message, error=False):
        """
        Выводит сообщение в messages_container на несколько секунд.
        """
        color = "red" if error else "green"
        message_container = Container(
            content=Text(message, color=color),
            padding=10,
            border_radius=5,
            bgcolor="#292929"
        )
        messages_container.controls.append(message_container)
        page.update()

        def hide_message():
            time.sleep(5)
            if message_container in messages_container.controls:
                messages_container.controls.remove(message_container)
                page.update()

        threading.Thread(target=hide_message, daemon=True).start()

    # Колбэк, который вызывается при успешном логине
    def on_login_success():
        page.controls.clear()
        table_view = build_table_view(page, connection, show_message)
        # Можно добавить messages_box справа
        main_content = Container(
            content=Column(
                [
                    table_view,
                ],
                expand=True
            ),
            expand=True
        )

        page.add(
            main_content,
            messages_box
        )
        page.update()

    # Создаём login_view
    login_view = build_login_view(page, connection, show_message, on_login_success)

    # Изначально отображаем форму авторизации
    page.add(login_view)

flet.app(target=main, host="192.168.250.245", port=8080)
