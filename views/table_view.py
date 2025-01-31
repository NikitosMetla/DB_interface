# views/table_view.py

import threading
import time
from flet import (
    Column, Text, Row, TextField, ElevatedButton, DataTable, DataColumn,
    DataRow, DataCell, Icons, Container, alignment, border, TextOverflow, Dropdown, dropdown
)

from db_utils import execute_query, get_table_columns
from config import TABLE_NAMES_RUS, get_column_rus_name

def build_table_view(page, connection, show_message):
    """
    Возвращает колонку с интерфейсом для отображения и управления таблицами.
    :param page: Flet Page
    :param connection: соединение с БД
    :param show_message: функция для отображения сообщений в отдельном контейнере
    """

    # Список таблиц
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

    selected_table = "Employees"
    columns_info = []
    fields_dict = {}
    primary_key = None
    editing_row_id = None

    # Элементы интерфейса
    selected_table_label = Text("", size=20, weight="bold")
    table_dropdown = Dropdown(
        label="Выберите таблицу",
        options=[dropdown.Option(key=t, text=TABLE_NAMES_RUS.get(t, t)) for t in tables_list],
        value=selected_table
    )
    add_button = ElevatedButton("Добавить")
    save_button = ElevatedButton("Сохранить изменения", disabled=True)
    cancel_button = ElevatedButton("Отменить изменения", disabled=True)
    clear_button = ElevatedButton("Очистить поля")

    input_row = Row(spacing=20)
    table = DataTable(columns=[], rows=[])
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

    # Основной блок контента (колонка)
    content_view = Column(
        [
            Text("Управление таблицами", size=30, weight="bold"),
            table_dropdown,
            selected_table_label,
            input_row,
            Row([add_button, save_button, cancel_button, clear_button], spacing=20),
            table_container
        ],
        expand=True,
        spacing=20
    )

    # ФУНКЦИИ:

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
        selected_table_label.value = f"Таблица: {TABLE_NAMES_RUS.get(selected_table, selected_table)}"
        refresh_table()
        page.update()

    def rebuild_input_fields():
        fields_dict.clear()
        input_row.controls.clear()
        if not columns_info:
            return

        for col in columns_info:
            # Пропускаем автоинкремент
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
                row_cells.append(
                    DataCell(Text(str(val), width=150, max_lines=1, overflow=TextOverflow.ELLIPSIS))
                )

            # Кнопки
            row_cells.append(
                DataCell(ElevatedButton("Изменить", icon=Icons.EDIT, on_click=lambda e, rd=row_data: edit_row(rd)))
            )
            row_cells.append(
                DataCell(ElevatedButton("Удалить", icon=Icons.DELETE, on_click=lambda e, rd=row_data: delete_row(rd)))
            )

            table.rows.append(DataRow(cells=row_cells, selected=is_editing))

        page.update()

    def add_row(e=None):
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

        # Проверяем, что нет пустых полей:
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

    def save_row(e=None):
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

    def cancel_edit(e=None):
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

    def clear_input_fields(e=None):
        for col_name in fields_dict:
            fields_dict[col_name].value = ""
        page.update()

    # Привязываем колбэки к кнопкам и дропдауну
    table_dropdown.on_change = lambda e: select_table(e.control.value)
    add_button.on_click = add_row
    save_button.on_click = save_row
    cancel_button.on_click = cancel_edit
    clear_button.on_click = clear_input_fields

    # Изначальная инициализация
    select_table(selected_table)

    return content_view
