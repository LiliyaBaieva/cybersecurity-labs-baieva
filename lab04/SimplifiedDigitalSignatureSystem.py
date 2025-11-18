import hashlib
import os

MODULO = 1000007  # Модуль для спрощеної математики
MULTIPLIER = 7    # Множник для публічного ключа
BLOCK_SIZE = 65536 # 64 КБ - розмір блоку для хешування великих файлів
SIGNATURE_EXT = ".sig" # Розширення для файлу підпису

def get_user_data():
    print("Введення Даних для Генерації Ключів:")
    name = input("Введіть Ім'я та Прізвище (наприклад, Петренко): ")
    birthday = input("Введіть Дату народження (наприклад, 15031995): ")
    secret_word = input("Введіть Секретне слово (наприклад, secret_word): ")
    
    print("\nВведення Шляху до Документа:")
    
    while True:
        file_path = input("Введіть повний шлях до файлу для підпису: ")
        if os.path.exists(file_path):
            return name, birthday, secret_word, file_path
        else:
            print(f"Помилка: Файл за шляхом '{file_path}' не знайдено. Спробуйте ще раз.")

def generate_keys(name, birthday, secret_word, multiplier, modulo):
    base_string = f"{name}{birthday}{secret_word}"
    private_hash = hashlib.sha256(base_string.encode()).hexdigest()
    private_key = int(private_hash[:8], 16) % modulo
    public_key = (private_key * multiplier) % modulo
    return private_key, public_key

def calculate_sha256_hash(file_path):
    """Обчислює хеш SHA256 всього вмісту файлу, читаючи його по блоках."""
    if file_path is None or not os.path.exists(file_path):
        return None
        
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while True:
                buffer = f.read(BLOCK_SIZE)
                if not buffer:
                    break
                hasher.update(buffer)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Помилка при читанні файлу для хешування: {e}")
        return None

def create_signature(document_hash, private_key):
    """Створення цифрового підпису (Хеш XOR Приватний Ключ)."""
    hash_int = int(document_hash[:32], 16) 
    signature = hash_int ^ private_key
    return signature

def save_signature(signature, file_path_original):
    """Зберігає підпис у окремий файл з розширенням .sig."""
    sig_path = file_path_original + SIGNATURE_EXT
    try:
        with open(sig_path, 'w') as f:
            f.write(str(signature))
        print(f"Підпис збережено у файл: {sig_path}")
        return sig_path
    except Exception as e:
        print(f"Помилка при збереженні підпису: {e}")
        return None

def verify_signature(current_document_hash, signature, public_key):
    
    current_hash_int = int(current_document_hash[:32], 16)
    
    if (current_hash_int ^ signature) < MODULO :
         return "Підпис ДІЙСНИЙ"
    else:
         return "Підпис ПІДРОБЛЕНИЙ"

def create_modified_file(file_path_original):
    base, ext = os.path.splitext(file_path_original)
    modified_path = base + "_MODIFIED" + ext
    
    try:
        with open(file_path_original, 'rb') as f_orig, open(modified_path, 'wb') as f_mod:
            f_mod.write(f_orig.read())
            f_mod.write(b'\x01') 
        print(f"Створено модифікований файл для тесту: {modified_path}")
        return modified_path
    except Exception as e:
        print(f"Помилка при створенні модифікованого файлу: {e}")
        return None

name, dob, secret_word, file_path_original = get_user_data()

private_key, public_key = generate_keys(name, dob, secret_word, MULTIPLIER, MODULO)

print("\n" + "="*70)
print(f"Демонстрація Результатів для файлу: {os.path.basename(file_path_original)}")
print("="*70)

print("--- 1. Генерація Ключів ---")
print(f"Приватний ключ (PK): {private_key}")
print(f"Публічний ключ (PUK): {public_key}\n")

original_hash = calculate_sha256_hash(file_path_original)

if original_hash is None:
    print("Не вдалося обчислити хеш. Програму зупинено.")
else:
    signature = create_signature(original_hash, private_key)
    signature_path = save_signature(signature, file_path_original)

    print("--- 2. Створення Підпису ---")
    print(f"Хеш оригінального документа (SHA256): {original_hash[:20]}...")
    print(f"Цифровий підпис: {signature}\n")

    print("--- 3. Перевірка Підпису (Оригінальний, незмінений файл) ---")
    
    result_valid = verify_signature(original_hash, signature, public_key)
    print(f"Результат перевірки: **{result_valid}**")

    print("\n--- 4. Демонстрація Виявлення Змін (Модифікація) ---")
    
    file_path_modified = create_modified_file(file_path_original)
    
    if file_path_modified:
        modified_hash = calculate_sha256_hash(file_path_modified)
        
        print(f"Хеш модифікованого файлу: {modified_hash[:20]}...")

        result_invalid = verify_signature(modified_hash, signature, public_key)
        print(f"Результат перевірки (з оригінальним підписом): **{result_invalid}**")
        
        os.remove(file_path_modified)
        print(f"\n[Очистка: Видалено {os.path.basename(file_path_modified)}]")