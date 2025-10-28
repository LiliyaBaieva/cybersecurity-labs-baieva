import re

LATIN_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

TRANSLITERATION_MAP = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E', 'Є': 'IE', 'Ж': 'ZH', 'З': 'Z',
    'И': 'Y', 'І': 'I', 'Ї': 'YI', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P',
    'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'KH', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SHCH',
    'Ь': '', 'Ю': 'IU', 'Я': 'IA'
}


class CipherAnalyzer:
    """Клас для реалізації та порівняння шифрів Цезаря та Віженера."""
    
    def __init__(self, surname, birthday, text):
        self.surname = surname.upper() 
        self.birthday = birthday
        self.text = self._prepare_text(text)
        
        self.caesar_key = self._generate_caesar_key()
        self.vigenere_key = self.surname
        
    def _transliterate(self, text):
        """Переводить кириличний текст у латиницю (простий варіант)."""
        result = ''
        for char in text.upper():
            if char in TRANSLITERATION_MAP:
                result += TRANSLITERATION_MAP[char]
            elif char in LATIN_ALPHABET or char.isspace():
                result += char
        return result

    def _prepare_text(self, text):
        """Готує текст, транслітерує його та залишає лише латинські літери."""
        transliterated = self._transliterate(text)
        prepared = re.sub(r'[^A-Z\s]', '', transliterated.upper())
        return prepared

    def _generate_caesar_key(self):
        """Генерує ключ Цезаря: Сума цифр дня та місяця (ДД.ММ)."""
        try:
            parts = self.birthday.split('.')
            day_month_str = parts[0] + parts[1]
            key = sum(int(d) for d in day_month_str)
            return (key % 26) or 1 
        except:
            return 3

    def caesar_encrypt(self, text):
        result = ""
        for char in text:
            if char in LATIN_ALPHABET:
                index = LATIN_ALPHABET.find(char)
                new_index = (index + self.caesar_key) % 26
                result += LATIN_ALPHABET[new_index]
            else:
                result += char
        return result

    def caesar_decrypt(self, text):
        result = ""
        for char in text:
            if char in LATIN_ALPHABET:
                index = LATIN_ALPHABET.find(char)
                new_index = (index - self.caesar_key) % 26
                result += LATIN_ALPHABET[new_index]
            else:
                result += char
        return result

    def vigenere_encrypt(self, text):
        result = ""
        key_length = len(self.vigenere_key)
        key_index = 0
        
        for char in text:
            if char in LATIN_ALPHABET:
                key_char = self.vigenere_key[key_index % key_length]
                shift = LATIN_ALPHABET.find(key_char)
                
                text_index = LATIN_ALPHABET.find(char)
                new_index = (text_index + shift) % 26
                result += LATIN_ALPHABET[new_index]
                
                key_index += 1
            else:
                result += char
        return result

    def vigenere_decrypt(self, text):
        result = ""
        key_length = len(self.vigenere_key)
        key_index = 0
        
        for char in text:
            if char in LATIN_ALPHABET:
                key_char = self.vigenere_key[key_index % key_length]
                shift = LATIN_ALPHABET.find(key_char)
                
                text_index = LATIN_ALPHABET.find(char)
                new_index = (text_index - shift) % 26
                result += LATIN_ALPHABET[new_index]
                
                key_index += 1
            else:
                result += char
        return result

    def _calculate_uniqueness(self, cipher_text):
        """Оцінює "унікальність" шифротексту."""
        text_no_space = re.sub(r'[^A-Z]', '', cipher_text)
        if not text_no_space: return 0
        unique_chars = len(set(text_no_space))
        total_chars = len(text_no_space)
        return (unique_chars / total_chars)

def run_program():
    print("=== АНАЛІЗ БЕЗПЕКИ КЛАСИЧНИХ ШИФРІВ (Кирилиця -> Латиниця) ===")
    
    surname = input("1. Введіть Прізвище ЛАТИНИЦЕЮ: ")
    birthday = input("2. Введіть дату народження (ДД.ММ.РРРР): ")
    text_input = input("3. Введіть тестовий текст для шифрування: ")

    if not surname or not birthday or not text_input:
        print("\nПомилка: Необхідно ввести всі дані для аналізу.")
        return

    analyzer = CipherAnalyzer(surname, birthday, text_input)
    
    print("\n" + "=" * 40)
    print("      РЕЗУЛЬТАТИ АНАЛІЗУ ШИФРІВ")
    print("=" * 40)
    
    print("\n--- 1. ГЕНЕРАЦІЯ КЛЮЧІВ ТА ПІДГОТОВКА ТЕКСТУ ---")
    print(f"   * Вхідний текст (Оригінал): '{text_input}'")
    print(f"   * Підготовлений текст (Транслітерація): '{analyzer.text}'")
    print(f"   * Ключ Цезаря (ДД+ММ): K = {analyzer.caesar_key}")
    print(f"   * Ключ Віженера (Прізвище): K = {analyzer.vigenere_key}")
    
    cipher_caesar = analyzer.caesar_encrypt(analyzer.text)
    cipher_vigenere = analyzer.vigenere_encrypt(analyzer.text)
    
    uniqueness_caesar = analyzer._calculate_uniqueness(cipher_caesar)
    uniqueness_vigenere = analyzer._calculate_uniqueness(cipher_vigenere)
    
    decrypted_caesar = analyzer.caesar_decrypt(cipher_caesar)
    decrypted_vigenere = analyzer.vigenere_decrypt(cipher_vigenere)

    print("\n--- 2. РЕЗУЛЬТАТИ ШИФРУВАННЯ ТА ДЕШИФРУВАННЯ ---")
    print(f"   * [Цезар] Шифротекст: {cipher_caesar}")
    print(f"   * [Віженер] Шифротекст: {cipher_vigenere}")
    
    print("\n--- 3. ПОРІВНЯЛЬНИЙ АНАЛІЗ СТІЙКОСТІ ---")
    print("| {:<10} | {:<12} | {:<15} | {:<25} |".format("Шифр", "Ключ", "Метод", "Унікальність літер (%)"))
    print("|" + "-"*12 + "|" + "-"*14 + "|" + "-"*17 + "|" + "-"*27 + "|")

    print("| {:<10} | {:<12} | {:<15} | {:<25.2f} |".format(
        "Цезаря", f"K={analyzer.caesar_key}", "Моноалфавітний", uniqueness_caesar * 100))
        
    print("| {:<10} | {:<12} | {:<15} | {:<25.2f} |".format(
        "Віженера", analyzer.vigenere_key[:10], "Поліалфавітний", uniqueness_vigenere * 100))
        
    print("\n--- 4. ВИСНОВКИ ПРО СТІЙКІСТЬ МЕТОДІВ ---")
    if uniqueness_vigenere > uniqueness_caesar:
        print("Шифр Віженера є стійкішим, оскільки поліалфавітна заміна краще приховує частоти літер.")
    else:
        print("Шифр Цезаря завжди криптографічно слабший, незважаючи на показник унікальності.")
        

if __name__ == '__main__':
    run_program()