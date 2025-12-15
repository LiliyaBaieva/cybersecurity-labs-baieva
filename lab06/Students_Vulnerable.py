import sqlite3
import os

DB_NAME = "vulnerable_students.db"

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

def vulnerable_query(user_input):

    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # ВРАЗЛИВЕ МІСЦЕ: Пряма конкатенація рядка користувача 

        sql_query = f"SELECT id, name, group_id, secret_pin FROM users WHERE name LIKE '%{user_input}%' OR group_id LIKE '%{user_input}%'"
        
        print("-" * 50)
        print(f"SQL-запит, що виконується (УРАЗЛИВИЙ):\n{sql_query}")
        print("-" * 50)

        cursor.execute(sql_query)
        
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f" Помилка виконання SQL-запиту: {e}")
        print("Це може свідчити про УСПІШНУ зміну логіки запиту (ін'єкцію).")
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
    print("{:<4} | {:<25} | {:<10} | {:<15}".format("ID", "Ім'я", "Група", "PIN-код"))
    print("---------------------------------------------------------------------")
    is_injection_successful = False
    for row in results:
        pin_status = "КОНФІДЕНЦІЙНО" if str(row[3]) == "0000" else str(row[3])
        print(f"{row[0]:<4} | {row[1]:<25} | {row[2]:<10} | {pin_status:<15}")
        if str(row[3]) == "0000":
             is_injection_successful = True
             
    print("---------------------------------------------------------------------")



def main():
    setup_database()
    print("\n=== ВРАЗЛИВИЙ КОНСОЛЬНИЙ ДОДАТОК ДЛЯ ПОШУКУ СТУДЕНТІВ ===")
    
    while True:
        try:
            # Змінений пейлоад для LIKE: тепер потрібен % на початку.
            user_input = input("\nВведіть ім'я, групу:\n> ").strip()
            
            if user_input.lower() in ['exit', 'вихід']:
                print("Завершення роботи.")
                break
            if not user_input:
                continue

            results = vulnerable_query(user_input)
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