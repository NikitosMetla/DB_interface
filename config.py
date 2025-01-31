# config.py

# Сопоставление таблиц с их русскими названиями
TABLE_NAMES_RUS = {
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
TABLE_COLUMN_NAMES = {
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
    """
    Возвращает русское название столбца по имени таблицы и столбца.
    """
    return TABLE_COLUMN_NAMES.get(table_name, {}).get(col_name, col_name)
