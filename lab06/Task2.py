# === Небезпечне використання даних користувача ===

from sqlite3 import Cursor


user_input = "Gifts' OR 1=1 --" # Дані безпосередньо від користувача
sql_query = f"SELECT * FROM products WHERE category = '{user_input}' AND released = 1"
# Результат: 
# SELECT * FROM products WHERE category = 'Gifts' OR 1=1 --' AND released = 1
# Тут лапки навколо змінної дозволяють ін'єкцію!


# === Безпечний SQL-запит ===

category_input = "Gifts' OR 1=1 --" # Імітація введення зловмисника

# БЕЗПЕКА: Використання плейсхолдера '?' (Prepared Statement)
sql_template = "SELECT * FROM products WHERE category = ? AND released = 1"

# Виконання запиту
# Курсор передає запит і дані ОКРЕМО.
Cursor.execute(sql_template, (category_input,))