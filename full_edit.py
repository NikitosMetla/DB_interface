import flet
from flet import (
    Page, Text, Row, Column, TextField, ElevatedButton, DataTable, DataColumn,
    DataRow, DataCell, Icons, Container, alignment, border, TextOverflow, Dropdown, dropdown
)
import pymysql
import threading
import time

# Сопоставление таблиц с их русскими названиями
table_names_rus = {
    "Clients": "Клиенты",
    "Document_Types": "Типы документов",
    "Employees": "Сотрудники",
    "GOSTs": "ГОСТы",
    "Orders": "Заказы",
    "Positions": "Должности",
    "Production_Documents": "Производственные документы",
    "Products": "Продукция",

    "Products_in_Stock": "Продукция на складе",
    "Stock": "Склады"
}

# Словарь русских названий столбцов для каждой таблицы
table_column_names = {
    "Clients": {
        "client_id": "ID клиента",
        "last_name": "Фамилия",
        "first_name": "Имя",
        "middle_name": "Отчество",
        "contacts": "Контакты"
    },
    "Document_Types": {
        "document_type_id": "ID типа документа",
        "name": "Наименование"
    },
    "Employees": {
        "employee_id": "ID сотрудника",
        "last_name": "Фамилия",
        "first_name": "Имя",
        "middle_name": "Отчество",
        "position_id": "ID должности",
        "login": "Логин",
        "password": "Пароль"
    },
    "GOSTs": {
        "gost_id": "ID ГОСТ",
        "name": "Наименование ГОСТ"
    },
    "Orders": {
        "order_id": "ID заказа",
        "status": "Статус",
        "client_id": "ID клиента",
        "employee_id": "ID сотрудника"
    },
    "Positions": {
        "position_id": "ID должности",
        "title": "Название должности"
    },
    "Production_Documents": {
        "document_id": "ID документа",
        "order_id": "ID заказа",
        "date": "Дата",
        "document_type_id": "ID типа документа",
        "employee_id": "ID сотрудника",
        "info": "Информация"
    },
    "Products": {
        "product_id": "ID продукта",
        "manufacture_date": "Дата производства",
        "name": "Наименование",
        "gost_id": "ID ГОСТ",
        "order_id": "ID заказа"
    },
    "Products_in_Stock": {
        "product_id": "ID продукта",
        "stock_id": "ID склада",
        "quantity": "Количество"
    },
    "Stock": {
        "stock_id": "ID склада",
        "address": "Адрес"
    }
}

def get_column_rus_name(table_name, col_name):
    return table_column_names.get(table_name, {}).get(col_name, col_name)

def execute_query(connection, query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        upper_query = query.strip().upper()
        if upper_query.startswith("SELECT") or upper_query.startswith("SHOW"):
            return cursor.fetchall()
        connection.commit()
    return []

def get_table_columns(connection, table_name):
    query = f"SHOW COLUMNS FROM {table_name}"
    columns = execute_query(connection, query)
    return columns

def main(page: Page):
    page.scroll = "auto"
    page.window.full_screen = True
    page.window.maximized = True
    page.theme_mode = "dark"

    connection = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="fischer",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

    authenticated = False
    selected_table = "employees"
    columns_info = []
    fields_dict = {}
    primary_key = None
    editing_row_id = None

    # Контейнер для сообщений
    messages_container = Column(scroll="auto")

    messages_box = Container(
        content=messages_container,
        padding=10,
        border=border.all(1, "gray"),
        border_radius=10,
        bgcolor="#1E1E1E",  # Темный цвет фона для сообщений
        width=300,
        height=400,  # Фиксированная высота
        alignment=alignment.top_center
    )

    def show_message(message, error=False):
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

    # Поля для логина
    login_field = TextField(label="Логин", width=200)
    password_field = TextField(label="Пароль", password=True, can_reveal_password=True, width=200)
    login_button = ElevatedButton("Войти", on_click=lambda e: login_action())

    # Центрируем форму логина
    login_view = Container(
        content=Column([
            Text("Авторизация", size=30, weight="bold"),
            login_field,
            password_field,
            login_button
        ], alignment="center", horizontal_alignment="center", spacing=20),
        expand=True,
        alignment=alignment.center
    )

    # Таблицы
    tables_list = [
        "Clients",
        "Document_Types",
        "Employees",
        "GOSTs",
        "Orders",
        "Positions",
        "Production_Documents",
        "Products",
        "Products_in_Stock",
        "Stock"
    ]

    table_dropdown = Dropdown(
        label="Выберите таблицу",
        options=[dropdown.Option(key=t, text=table_names_rus.get(t, t)) for t in tables_list],
        value=selected_table,
        on_change=lambda e: select_table(e.control.value)
    )

    add_button = ElevatedButton("Добавить", on_click=lambda e: add_row())
    save_button = ElevatedButton("Сохранить изменения", on_click=lambda e: save_row(), disabled=True)
    cancel_button = ElevatedButton("Отменить изменения", on_click=lambda e: cancel_edit(), disabled=True)
    clear_button = ElevatedButton("Очистить поля", on_click=lambda e: clear_input_fields())

    input_row = Row(spacing=20)

    table = DataTable(columns=[], rows=[])

    # Оборачиваем таблицу в Row с горизонтальной прокруткой
    table_row = Row(
        controls=[table],
        scroll="auto",
        width=1500,
        height=600,
        vertical_alignment="start"
    )

    table_container = Container(
        content=table_row,
        border=border.all(1, "white"),
        alignment=alignment.top_left
    )

    selected_table_label = Text("", size=20, weight="bold")

    content_view = Column([
        Text("Управление таблицами", size=30, weight="bold"),
        table_dropdown,
        selected_table_label,
        input_row,
        Row([add_button, save_button, cancel_button, clear_button], spacing=20),
        Row([table_container, messages_box], spacing=20, alignment="spaceBetween", expand=True)
    ], expand=True, spacing=20)

    def login_action():
        user_login = login_field.value.strip()
        user_password = password_field.value.strip()

        if not user_login or not user_password:
            show_message("Введите логин и пароль", error=True)
            return

        query = "SELECT * FROM Employees WHERE login=%s AND password=%s"
        res = execute_query(connection, query, (user_login, user_password))

        if res and len(res) > 0:
            nonlocal authenticated
            authenticated = True
            init_app_view()
        else:
            show_message("Неверный логин или пароль", error=True)

    def init_app_view():
        page.controls.clear()
        select_table(selected_table)
        page.add(content_view)
        page.update()
        show_message("Успешный вход!")

    def select_table(table_name):
        nonlocal selected_table, columns_info, primary_key, editing_row_id
        selected_table = table_name
        editing_row_id = None

        columns_info = get_table_columns(connection, selected_table)
        primary_key = None
        for col in columns_info:
            if col['Key'] == 'PRI':
                primary_key = col['Field']
                break

        rebuild_input_fields()
        selected_table_label.value = f"Таблица: {table_names_rus.get(selected_table, selected_table)}"
        refresh_table()
        page.update()

    def rebuild_input_fields():
        fields_dict.clear()
        input_row.controls.clear()
        if not columns_info:
            return

        for col in columns_info:
            if "auto_increment" in col['Extra']:
                continue
            col_name = col['Field']
            field_label = get_column_rus_name(selected_table, col_name)
            tf = TextField(label=field_label, expand=1)
            fields_dict[col_name] = tf
            input_row.controls.append(tf)
        page.update()

    def refresh_table():
        table.columns.clear()
        table.rows.clear()

        if not columns_info:
            show_message("Не удалось получить столбцы для выбранной таблицы или таблица не существует.", error=True)
            page.update()
            return

        # Настройки для некоторых таблиц
        if selected_table in ["Employees", "Production_Documents"]:
            table.column_spacing = 10
        else:
            table.column_spacing = 20

        query = f"SELECT * FROM {selected_table}"
        try:
            rows = execute_query(connection, query)
        except Exception as e:
            show_message(f"Ошибка при выборке данных: {e}", error=True)
            return

        for col in columns_info:
            table.columns.append(DataColumn(Text(get_column_rus_name(selected_table, col['Field']))))
        # Добавляем столбцы для кнопок
        table.columns.append(DataColumn(Text("")))
        table.columns.append(DataColumn(Text("")))

        for row_data in rows:
            is_editing = (editing_row_id is not None and primary_key and row_data[primary_key] == editing_row_id)
            row_cells = []
            for col in columns_info:
                val = row_data[col['Field']]
                if val is None:
                    val = ""
                row_cells.append(DataCell(Text(str(val), width=150, max_lines=1, overflow=TextOverflow.ELLIPSIS)))

            row_cells.append(DataCell(ElevatedButton("Изменить", icon=Icons.EDIT, on_click=lambda e, rd=row_data: edit_row(rd))))
            row_cells.append(DataCell(ElevatedButton("Удалить", icon=Icons.DELETE, on_click=lambda e, rd=row_data: delete_row(rd))))

            table.rows.append(DataRow(cells=row_cells, selected=is_editing))

        page.update()

    def add_row():
        if not columns_info:
            show_message("Столбцы не инициализированы. Невозможно добавить данные.", error=True)
            return

        fields_to_insert = []
        values = []
        placeholders = []
        for col in columns_info:
            if primary_key == col['Field'] and "auto_increment" in col['Extra']:
                continue
            val = fields_dict[col['Field']].value.strip() if col['Field'] in fields_dict else None
            fields_to_insert.append(col['Field'])
            placeholders.append("%s")
            values.append(val if val else None)

        if any(v is None or v == "" for v in values):
            show_message("Все поля должны быть заполнены!", error=True)
            return

        query = f"INSERT INTO {selected_table} ({', '.join(fields_to_insert)}) VALUES ({', '.join(placeholders)})"
        try:
            execute_query(connection, query, tuple(values))
            clear_input_fields()
            refresh_table()
            show_message("Запись успешно добавлена!")
        except Exception as ex:
            show_message(f"Ошибка при добавлении данных: {ex}", error=True)

    def delete_row(row_data):
        if not primary_key:
            show_message("Первичный ключ не определен. Удаление невозможно.", error=True)
            return

        pk_value = row_data[primary_key]
        query = f"DELETE FROM {selected_table} WHERE {primary_key} = %s"
        try:
            execute_query(connection, query, (pk_value,))
            refresh_table()
            show_message("Запись успешно удалена!")
        except Exception as ex:
            show_message(f"Ошибка при удалении данных: {ex}", error=True)

    def edit_row(row_data):
        nonlocal editing_row_id
        if not primary_key:
            show_message("Первичный ключ не определен. Редактирование невозможно.", error=True)
            return

        editing_row_id = row_data[primary_key]
        for col in columns_info:
            if primary_key == col['Field'] and "auto_increment" in col['Extra']:
                continue
            val = row_data[col['Field']]
            fields_dict[col['Field']].value = str(val) if val is not None else ""

        save_button.disabled = False
        cancel_button.disabled = False
        add_button.disabled = True
        page.update()

    def save_row():
        if editing_row_id is None or not primary_key:
            return

        set_clauses = []
        values = []
        for col in columns_info:
            if primary_key == col['Field'] and "auto_increment" in col['Extra']:
                continue
            val = fields_dict[col['Field']].value.strip() if col['Field'] in fields_dict else None
            if not val:
                show_message("Все поля должны быть заполнены для сохранения!", error=True)
                return
            set_clauses.append(f"{col['Field']} = %s")
            values.append(val)

        values.append(editing_row_id)
        query = f"UPDATE {selected_table} SET {', '.join(set_clauses)} WHERE {primary_key} = %s"
        try:
            execute_query(connection, query, tuple(values))
            stop_editing()
            show_message("Изменения успешно сохранены!")
        except Exception as ex:
            show_message(f"Ошибка при сохранении данных: {ex}", error=True)

    def cancel_edit():
        stop_editing()

    def stop_editing():
        nonlocal editing_row_id
        editing_row_id = None
        clear_input_fields()
        save_button.disabled = True
        cancel_button.disabled = True
        add_button.disabled = False
        refresh_table()
        page.update()

    def clear_input_fields():
        for col_name in fields_dict:
            fields_dict[col_name].value = ""
        page.update()

    # Изначально отображаем форму авторизации
    page.add(login_view)

flet.app(target=main, host="192.168.250.245", port=8080)
