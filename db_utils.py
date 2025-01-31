# db_utils.py

def execute_query(connection, query, params=None):
    """
    Выполняет запрос (SELECT, UPDATE, DELETE, INSERT).
    Возвращает результат для SELECT-запросов и None в остальных случаях.
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        upper_query = query.strip().upper()
        if upper_query.startswith("SELECT") or upper_query.startswith("SHOW"):
            return cursor.fetchall()
        connection.commit()
    return []

def get_table_columns(connection, table_name):
    """
    Возвращает список столбцов для указанной таблицы (результат запроса SHOW COLUMNS).
    """
    query = f"SHOW COLUMNS FROM {table_name}"
    columns = execute_query(connection, query)
    return columns
