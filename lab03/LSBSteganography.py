from PIL import Image
import os
import sys

# Маркер кінця повідомлення (запобігає витягуванню зайвих даних).
DELIMITER = "###END###" 
# Для конвертації використовуємо байтове представлення, щоб коректно працювати з UTF-8
BINARY_DELIMITER = ''.join(format(byte, '08b') for byte in DELIMITER.encode('utf-8'))

class LSBSteganography:
    
    def __init__(self, container_path):
        self.container_path = container_path
        try:
            self.img = Image.open(container_path).convert('RGB')
        except FileNotFoundError:
            print(f"Помилка: Файл контейнера '{container_path}' не знайдено.")
            sys.exit(1)
        
        self.width, self.height = self.img.size
        self.max_capacity_bits = self.width * self.height * 3

    def _text_to_binary(self, text):
        """Конвертує текст у потік бітів, використовуючи UTF-8."""
        
        byte_data = text.encode('utf-8')
        
        binary_message = ''.join(format(byte, '08b') for byte in byte_data)
        
        return binary_message + BINARY_DELIMITER

    def _binary_to_text(self, binary_data):
        """Перетворює двійковий рядок назад у текст, декодуючи UTF-8."""
        byte_list = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
        
        # Збираємо список цілих чисел (значень байтів)
        byte_values = []
        
        for byte in byte_list:
            if len(byte) != 8:
                break
            
            byte_value = int(byte, 2)
            byte_values.append(byte_value)
            
            # Спробуємо декодувати всю зібрану послідовність байтів
            try:
                temp_text = bytes(byte_values).decode('utf-8', errors='replace')
                
                # Перевіряємо, чи знайдено маркер кінця
                if DELIMITER in temp_text:
                    return temp_text.split(DELIMITER)[0]
                
            except UnicodeDecodeError:
                # Якщо декодування невдале, продовжуємо збирати байти
                continue
                
        try:
             return bytes(byte_values).decode('utf-8', errors='replace').split(DELIMITER)[0]
        except:
             return "Помилка декодування, маркер не знайдено."


    def hide_message(self, message, output_path):
        """Реалізація приховування LSB."""
        binary_message = self._text_to_binary(message)
        message_length = len(binary_message)
        
        if message_length > self.max_capacity_bits:
            print(f"Помилка: Повідомлення занадто велике. Потрібно {message_length} бітів, доступно {self.max_capacity_bits} бітів.")
            return False

        bit_index = 0
        changed_pixels_count = 0
        modified_pixels = list(self.img.getdata()) 

        for i in range(len(modified_pixels)):
            r, g, b = modified_pixels[i]
            current_pixel = list((r, g, b))
            
            for channel_index in range(3): # R, G, B
                if bit_index < message_length:
                    message_bit = int(binary_message[bit_index])
                    color_value = current_pixel[channel_index]
                    
                    new_color_value = (color_value & 0xFE) | message_bit
                    
                    if new_color_value != color_value:
                         changed_pixels_count += 1
                         
                    current_pixel[channel_index] = new_color_value
                    bit_index += 1
                else:
                    break 

            modified_pixels[i] = tuple(current_pixel)
            
            if bit_index >= message_length:
                break 

        new_img = Image.new(self.img.mode, self.img.size)
        new_img.putdata(modified_pixels)
        
        # Створення та збереження нового зображення
        new_img.save(output_path)
        
        print("\n--- [АНАЛІЗ ЗМІН] (Етап 4) ---")
        print(f"   * Приховано бітів (включно з маркером): {message_length}")
        print(f"   * Змінено кольорових байтів (LSB): {changed_pixels_count}")
        print(f"   * Стегоконтейнер збережено як: {output_path}")
        print(f"   * Зображення візуально не змінилося (LSB ефект)")
        return True

    def extract_message(self, stego_path):
        """Витягування LSB."""
        try:
            img = Image.open(stego_path).convert('RGB')
        except FileNotFoundError:
            print(f"Помилка: Файл стегоконтейнера '{stego_path}' не знайдено.")
            return None

        binary_data = ""
        
        for pixel in img.getdata():
            for color_value in pixel:
                binary_data += str(color_value & 1)
                
                # Перевіряємо, чи містить бінарний потік обмежувач
                if binary_data.endswith(BINARY_DELIMITER):
                    extracted_message = self._binary_to_text(binary_data)
                    return extracted_message
                        
        return None

def run_steganography_task():
    print("=== РЕАЛІЗАЦІЯ LSB-СТЕГАНОГРАФІЇ ===")
    
    full_name_input = input("Введіть П.І.Б. (для приховування): ")
    birthday_input = input("Введіть Д.Н. (ДД.ММ.РРРР): ")
    
    message = f"П.І.Б: {full_name_input}, Д.Н.: {birthday_input}"
    
    container_file = input("Введіть шлях до файлу-контейнера: ")
    
    directory = os.path.dirname(container_file) 
    filename = os.path.basename(container_file)
    new_filename = "stego_" + filename
    output_file = os.path.join(directory, new_filename)
    
    print("\n--- ДЕМОНСТРАЦІЯ РОЗУМІННЯ (Етап 1) ---")
    print("1. Повідомлення перетворюється на потік бітів (UTF-8).")
    print(f"   * Частина тексту: '{message[:5]}...'")
    print(f"   * У двійковому коді: {LSBSteganography._text_to_binary(LSBSteganography, message[:5])}...")
    print("2. Біти повідомлення замінюють LSB пікселів, що зберігає візуальну непомітність.")
    
    steg_system = LSBSteganography(container_file)
    print(f"\n[ПРИХОВУВАННЯ] Максимальна ємність (біт): {steg_system.max_capacity_bits}")
    
    if steg_system.hide_message(message, output_file):
        extracted_message = steg_system.extract_message(output_file)
        
        print("\n--- [ВИЯВЛЕННЯ] ---")
        if extracted_message and extracted_message == message:
             print(f"   * Успішно виявлене повідомлення: '{extracted_message}'")
        elif extracted_message:
             print("   * Виявлене повідомлення (можлива помилка кодування, але текст знайдено):")
             print(f"   * '{extracted_message}'")
        else:
            print("   * Помилка: Повідомлення не знайдено.")

if __name__ == '__main__':
    run_steganography_task()