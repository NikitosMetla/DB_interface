# 🖥️ DB Interface – Интерфейс для работы с базой данных

## 📌 Описание проекта

**DB Interface** – это простое графическое приложение для управления базой данных MySQL. Оно предоставляет удобный интерфейс для просмотра, редактирования, добавления и удаления данных в таблицах.

Приложение разработано с использованием **Flet** – мощного инструмента для создания кроссплатформенных GUI-приложений на Python.

---

## 🚀 Функциональные возможности

✅ **Авторизация** – вход в систему через логин и пароль, связанные с таблицей `Employees`.
✅ **Выбор таблицы** – удобный выпадающий список с русскими названиями.
✅ **Просмотр данных** – информация из таблиц представлена в виде таблицы с колонками и строками.
✅ **Добавление записей** – заполните необходимые поля и нажмите "Добавить".
✅ **Редактирование записей** – изменение данных с возможностью сохранения.
✅ **Удаление записей** – быстрое удаление ненужных строк.
✅ **Система уведомлений** – всплывающие сообщения о действиях и ошибках.

---

## 🎯 Целевая аудитория

Проект ориентирован на **администраторов баз данных, разработчиков и аналитиков**, которым требуется удобный инструмент для управления таблицами MySQL.

---

## 🏗️ Структура проекта

```bash
DB_interface/
├── main.py               # Точка входа в приложение (Flet UI)
├── config.py             # Словари русских названий таблиц и колонок
├── db_connection.py      # Подключение к базе данных MySQL
├── db_utils.py           # Функции для выполнения SQL-запросов (CRUD)
├── views/
│   ├── login_view.py     # Экран авторизации
│   ├── table_view.py     # Интерфейс для работы с таблицами
└── README.md             # Документация проекта
```

---

## 🔧 Установка и запуск

1️⃣ **Клонирование репозитория**
```bash
git clone https://github.com/NikitosMetla/DB_interface.git
cd DB_interface
```

2️⃣ **Установка зависимостей**
```bash
pip install -r requirements.txt
```

3️⃣ **Настройка подключения к БД**  
   Открываем `db_connection.py` и указываем правильные параметры:
```python
host="127.0.0.1"
user="root"
password=""
database="fischer"
```

4️⃣ **Запуск приложения**
```bash
python main.py
```

После запуска откроется окно или вкладка браузера с приложением по адресу `http://192.168.250.245:8080`.

---

## 🎨 Интерфейс

🔑 **Авторизация** – вход по логину и паролю.  
📊 **Главный экран** – таблицы с данными, кнопки редактирования, добавления и удаления записей.  
📩 **Окно сообщений** – всплывающие уведомления о действиях.  

---

## 📜 Лицензия

Проект распространяется по лицензии **MIT**. Вы можете свободно использовать и модифицировать код.

🤝 **Авторы:** [NikitosMetla](https://github.com/NikitosMetla)

💡 Если у вас есть предложения или замечания – создавайте Issue или Pull Request в репозитории. **Спасибо за поддержку!** 🚀

