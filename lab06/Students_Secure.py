import sqlite3
import os

DB_NAME = "secure_students.db"

def setup_database():
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                group_id TEXT NOT NULL,
                secret_pin TEXT NOT NULL 
            );
        """)

        test_data = [
            ("Олександр Іваненко", "КІ-21", "7788"),
            ("Марія Шевчук", "КІ-21", "9901"),
            ("Ігор Петренко", "КН-22", "1234"),
            ("Адмін Секретар", "Адмін", "0000") 
        ]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("INSERT INTO users (name, group_id, secret_pin) VALUES (?, ?, ?)", test_data)
            conn.commit()
            print(f" База даних '{DB_NAME}' створена та заповнена тестовими даними.")
            
    except sqlite3.Error as e:
        print(f" Помилка SQLite при налаштуванні: {e}")
    finally:
        if conn:
            conn.close()

def secure_query(user_input):

    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # БЕЗПЕЧНЕ МІСЦЕ: Використання плейсхолдерів (?)
        sql_query = "SELECT id, name, group_id, secret_pin FROM users WHERE name LIKE ? OR group_id LIKE ?"
        
        # Готуємо рядок для часткового пошуку: обгортаємо в %
        search_term = f"%{user_input}%"
        
        print("-" * 50)
        print(f"SQL-запит, що виконується (ЗАХИЩЕНИЙ):\n{sql_query}")
        print(f"З параметрами: ('{search_term}', '{search_term}')")
        print("-" * 50)
        
        # Передача параметрів ОКРЕМО від запиту
        cursor.execute(sql_query, (search_term, search_term))
        
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f" Помилка SQLite при виконанні запиту: {e}")
        return []
    finally:
        if conn:
            conn.close()

def print_results(results):
    if not results:
        print("🤷 Результатів не знайдено.")
        return
    
    print("\n📋 ЗНАЙДЕНІ ЗАПИСИ:")
    print("---------------------------------------------------------------------")
    # Використання str.format() для уникнення проблем з лапками
    print("{:<4} | {:<25} | {:<10} | {:<15}".format("ID", "Ім'я", "Група", "PIN-код"))
    print("---------------------------------------------------------------------")
    for row in results:
        pin_status = "КОНФІДЕНЦІЙНО" if str(row[3]) == "0000" else str(row[3])
        print(f"{row[0]:<4} | {row[1]:<25} | {row[2]:<10} | {pin_status:<15}")
    print("---------------------------------------------------------------------")


def main():
    setup_database()
    print("\n=== ЗАХИЩЕНИЙ КОНСОЛЬНИЙ ДОДАТОК ДЛЯ ПОШУКУ СТУДЕНТІВ ===")
    
    while True:
        try:
            user_input = input("\nВведіть ім'я, групу:\n> ").strip()
            
            if user_input.lower() in ['exit', 'вихід']:
                print("Завершення роботи.")
                break
            if not user_input:
                continue

            results = secure_query(user_input)
            
            if "%' OR 1=1" in user_input.upper():
                if not results:
                    print("\n ЗАХИСТ УСПІШНИЙ! Ін'єкційний рядок розцінений як простий термін пошуку, що не дав результатів.")

            print_results(results)

        except KeyboardInterrupt:
            print("\nЗавершення роботи.")
            break
        except Exception as e:
            print(f"Виникла несподівана помилка: {e}")

if __name__ == '__main__':
    try:
        main()
    finally:
        # Очищення бази даних після завершення
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
            print(f"\n Файл бази даних '{DB_NAME}' видалено.")