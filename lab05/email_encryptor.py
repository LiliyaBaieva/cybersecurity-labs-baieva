import os
import re
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

# Налаштування шифрування
AES_KEY_SIZE = 32
SALT_SIZE = 16     # Розмір солі для PBKDF2
ITERATIONS = 100000
ENCODING = 'utf-8'
BASE_ENCRYPT_FILENAME = "message.enc"

# ГЕНЕРАЦІЯ КЛЮЧА (використовуємо PBKDF2)

def generate_key_from_data(shared_secret: str, salt: bytes) -> bytes:
    """
    Генерує криптографічний ключ, використовуючи PBKDF2HMAC.
    
    :param shared_secret: Комбінований рядок (Email_Відправника:Пароль)
    :param salt: Унікальна сіль (16 байт)
    :return: Згенерований ключ (32 байти)
    """
    secret_data = shared_secret.encode(ENCODING)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    
    key = kdf.derive(secret_data)
    return key

#  ШИФРУВАННЯ ПОВІДОМЛЕННЯ

def encrypt_message(sender_email: str, password: str, plaintext: str) -> tuple[str, str]:
    """
    Шифрує повідомлення за допомогою AES-256-GCM.
    
    :param sender_email: Email Відправника (використовується для генерації ключа)
    :param password: Пароль користувача
    :param plaintext: Відкритий текст для шифрування
    :return: Кортеж: (Зашифроване повідомлення у Base64, Base64-кодований Спільний Секретний Ключ)
    """
    
    # 1. Створюємо Спільний Секретний Ключ у відкритому вигляді
    raw_shared_secret = f"{sender_email}:{password}"
    
    # 2. Кодуємо його у Base64 для "маскування"
    encoded_shared_secret = base64.b64encode(raw_shared_secret.encode(ENCODING)).decode(ENCODING)
    
    # 3. Генерація ключа для шифрування
    salt = os.urandom(SALT_SIZE)
    
    # Використовуємо НЕКОДОВАНИЙ секрет для генерації ключа
    key = generate_key_from_data(raw_shared_secret, salt)
    
    # 4. Власне шифрування
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    ciphertext = encryptor.update(plaintext.encode(ENCODING)) + encryptor.finalize()
    tag = encryptor.tag
    
    # Об'єднуємо всі необхідні частини для передачі: сіль + IV + шифротекст + тег
    encoded_message = salt + iv + ciphertext + tag
    
    # Кодуємо результат у Base64 для безпечної передачі як рядка
    return base64.b64encode(encoded_message).decode(ENCODING), encoded_shared_secret

# РОЗШИФРУВАННЯ ПОВІДОМЛЕННЯ

def decrypt_message(encoded_shared_secret: str, encoded_message: str) -> str | None:
    
    # Розшифровує повідомлення за допомогою AES-256-GCM, використовуючи Base64-кодований Спільний Секретний Ключ
    
    try:
        # 1. Декодуємо Base64-ключ, щоб отримати назад "Email:Пароль"
        raw_shared_secret = base64.b64decode(encoded_shared_secret).decode(ENCODING)
    except Exception:
        print("\n[ПОМИЛКА] Некоректний формат Base64-ключа.")
        return None
        
    try:
        # 2. Декодування зашифрованих даних з Base64
        decoded_data = base64.b64decode(encoded_message)
        
        # 3. Розділення даних на частини
        MIN_SIZE = SALT_SIZE + 12 + 16
        if len(decoded_data) < MIN_SIZE:
             print("[ПОМИЛКА] Некоректний формат даних: занадто короткий.")
             return None
             
        salt = decoded_data[:SALT_SIZE] 
        iv = decoded_data[SALT_SIZE : SALT_SIZE + 12] 
        tag_start = -16
        ciphertext = decoded_data[SALT_SIZE + 12 : tag_start]
        tag = decoded_data[tag_start:]
        
        # 4. Генерація ключа AES (з декодованого секрету)
        key = generate_key_from_data(raw_shared_secret, salt)
        
        # 5. Створення об'єкта розшифрування
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag), 
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # 6. Розшифрування
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext.decode(ENCODING)
        
    except ValueError:
        print("\n[ПОМИЛКА КРИПТОГРАФІЇ] Неможливо розшифрувати. Перевірте Спільний Секретний Ключ.")
        return None
    except Exception as e:
        print(f"\n[ЗАГАЛЬНА ПОМИЛКА] Помилка обробки повідомлення: {e}")
        return None

# ФУНКЦІЇ ВЗАЄМОДІЇ З ФАЙЛАМИ та ХЕЛПЕРИ

def save_to_file(filename: str, content: str):
    """Зберігає текстовий контент у файл."""
    try:
        with open(filename, 'w', encoding=ENCODING) as f:
            f.write(content)
        print(f"📄 Успішно збережено у файл: {filename}")
        return True
    except IOError as e:
        print(f"[ПОМИЛКА ФАЙЛОВОГО ВВЕДЕННЯ/ВИВЕДЕННЯ] Не вдалося зберегти файл: {e}")
        return False

def load_from_file(filename: str) -> str | None:
    try:
        with open(filename, 'r', encoding=ENCODING) as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"[ПОМИЛКА] Файл не знайдено: {filename}")
        return None
    except IOError as e:
        print(f"[ПОМИЛКА ФАЙЛОВОГО ВВЕДЕННЯ/ВИВЕДЕННЯ] Не вдалося прочитати файл: {e}")
        return None

def get_next_filename(base_name: str) -> str:
    
    # Генерує наступне доступне ім'я файлу, додаючи індекси (наприклад, message.enc, message1.enc, message2.enc).

    if not os.path.exists(base_name):
        return base_name
    
    name, ext = os.path.splitext(base_name)
    match = re.search(r'(\d+)$', name)
    counter = int(match.group(1)) + 1 if match else 1
    
    clean_name = re.sub(r'\d+$', '', name) if match else name

    while True:
        new_filename = f"{clean_name}{counter}{ext}"
        if not os.path.exists(new_filename):
            return new_filename
        counter += 1

# ІНТЕРАКТИВНЕ МЕНЮ

def main_menu():
    # Головне інтерактивне меню для користувача.

    while True:
        print("\n" + "="*70)
        print(" СИМЕТРИЧНИЙ ШИФРАТОР ПОВІДОМЛЕНЬ ")
        print("="*70)

        print("Виберіть дію:")
        print("1. Зашифрувати нове повідомлення (Відправник)")
        print("2. Розшифрувати повідомлення (Отримувач)")
        print("3. Вийти")
        print("-" * 70)
        
        # Змінюємо очікувані варіанти вибору
        choice = input("Ваш вибір (1, 2 або 3): ").strip()
        
        if choice == '1':
            print("\n--- Режим Шифрування (Відправник) ---")
            sender_email = input("1. Ваш Email (Відправник): ").strip()
            password = input("2. Секретний Пароль (спільний для обох сторін): ").strip()
            message = input("3. Введіть повідомлення для шифрування: ").strip()
            
            # Автоматичне визначення імені файлу
            output_file = get_next_filename(BASE_ENCRYPT_FILENAME)
            print(f"4. Файл для збереження: {output_file} (згенеровано автоматично)")
            
            if not all([sender_email, password, message]):
                print("[УВАГА] Усі поля мають бути заповнені.")
                continue

            try:
                encoded, encoded_shared_secret = encrypt_message(sender_email, password, message)
                
                print("\n" + "="*70)
                print(" ШИФРУВАННЯ УСПІШНЕ! Збереження...")
                
                # Зберігаємо зашифрований текст у файл
                if save_to_file(output_file, encoded):
                    print(f"СЕКРЕТНИЙ КЛЮЧ ДЛЯ ОТРИМУВАЧА (Повідомте йому!):")
                    print(f"  {encoded_shared_secret}")
                    print("\nПРИМІТКА: Отримувач повинен ввести ЦЕЙ Base64-рядок ТОЧНО для розшифрування.")
                print("="*70)
                
            except Exception as e:
                print(f"[КРИТИЧНА ПОМИЛКА ШИФРУВАННЯ] Сталася помилка: {e}")
                
        elif choice == '2':
            print("\n--- Режим Розшифрування (Отримувач) ---")
            
            encoded_shared_secret_key = input("Введіть Спільний Секретний Ключ (Base64-рядок): ").strip()
            
            input_file = input("Введіть назву файлу для розшифрування (наприклад, message.enc): ").strip()

            if not all([encoded_shared_secret_key, input_file]):
                print("[УВАГА] Усі поля мають бути заповнені.")
                continue

            # Завантажуємо зашифрований Base64 текст з файлу
            encoded_message = load_from_file(input_file)
            if encoded_message is None:
                 continue

            decrypted = decrypt_message(encoded_shared_secret_key, encoded_message)
            
            if decrypted is not None:
                print("\n" + "="*50)
                print("РОЗШИФРУВАННЯ УСПІШНЕ!")
                print("\nОригінальне повідомлення:")
                print("--------------------------------------------------")
                print(decrypted)
                print("--------------------------------------------------")
                print("="*50)
                        
        elif choice == '3':
            print("\nДякую за використання шифратора. До побачення!")
            break
            
        else:
            print("[УВАГА] Неправильний вибір. Будь ласка, введіть 1, 2 або 3.")

if __name__ == "__main__":
    main_menu()