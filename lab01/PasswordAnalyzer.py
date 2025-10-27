import re

class PasswordAnalyzer:
    
    def __init__(self, name, surname, birthday):
        self.personal_data = self.get_personal_keywords(name, surname, birthday)
        self.max_score = 10
        self.min_score = 1

    def get_personal_keywords(self, name, surname, birthday):
        data = []
        
        for item in [name, surname]:
            data.append(item.lower())
            data.append(item[:3].lower())
            
        parts = birthday.split('.')
        data.extend([
            parts[0], parts[1], parts[2],          
            "".join(parts),                        
            parts[0] + parts[1],                   
            parts[1] + parts[2],                   
        ])
        
        return list(set([str(item) for item in data if item])) 

    def analyze(self, password):
        score = 1
        recommendations = []
                
        if len(password) > 7:
            score += 2
        else:
            recommendations.append("Збільште довжину пароля (потрібно > 7 символів) для отримання базових балів.")

        if re.search(r'[A-Z]', password) and re.search(r'[a-z]', password):
            score += 2
        else:
            recommendations.append("Додайте літери у верхньому та нижньому регістрі.")

        if re.search(r'[0-9]', password):
            score += 2
        else:
            recommendations.append("Додайте цифри.")

        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 2
        else:
            recommendations.append("Додайте спеціальні символи (наприклад, !, @, #).")
            
        personal_data_found = []
        password_lower = password.lower()
        
        for data_item in self.personal_data:
            if data_item in password_lower and len(data_item) > 2:
                score -= 3
                personal_data_found.append(data_item)
                
        if personal_data_found:
            recommendations.append(f"КРИТИЧНО: Пароль містить особисті дані: {', '.join(personal_data_found)}. Це знижує надійність!")

        if re.search(r'(\d)\1{2,}|(.)\2{2,}', password):
            score -= 2
            recommendations.append("Уникайте повторюваних символів (наприклад, '111' або 'aaa').")

        final_score = max(self.min_score, min(score, self.max_score))
        
        return final_score, personal_data_found, recommendations

def get_user_input():
    print("--- Введіть ваші дані для аналізу ---")
    password = input("Введіть пароль для перевірки: ")
    full_name_lat = input("Введіть ПОВНЕ ім'я та прізвище ЛАТИНИЦЕЮ (Surname Name): ") 
    birthday = input("Введіть дату народження (у форматі ДД.ММ.РРРР): ")
    print("-" * 35)

    try:
        name_parts = full_name_lat.split()
        if len(name_parts) >= 2:
            surname = name_parts[0]
            name = name_parts[1]
        else:
            raise ValueError("Будь ласка, введіть принаймні Прізвище та Ім'я.")
        
        if not re.match(r'\d{2}\.\d{2}\.\d{4}', birthday):
            raise ValueError("Невірний формат дати народження.")

        return password, name, surname, birthday
        
    except ValueError as e:
        print(f"Помилка вводу: {e}")
        return None, None, None, None

def run_analysis():
    password, name, surname, birthday = get_user_input()

    if password:
        analyzer = PasswordAnalyzer(name, surname, birthday)
        final_score, personal_data_found, recommendations = analyzer.analyze(password)

        if final_score >= 9:
            rating = "Ідеальний"
        elif final_score >= 7:
            rating = "Дуже надійний"
        elif final_score >= 5:
            rating = "Надійний"
        elif final_score >= 3:
            rating = "Середній"
        else:
            rating = "Слабкий"
            
        print("\n--- РЕЗУЛЬТАТ АНАЛІЗУ ПАРОЛЯ ---")
        print(f"1. Оцінка надійності: {final_score}/{analyzer.max_score} ({rating})")
        
        if personal_data_found:
            print(f"2. КРИТИЧНИЙ ЗВ'ЯЗОК З ОСОБИСТИМИ ДАНИМИ: Виявлено використання: {', '.join(personal_data_found)}")
        else:
            print("2. ЗВ'ЯЗОК З ОСОБИСТИМИ ДАНИМИ: Не виявлено.")
            
        if recommendations:
            print("\n3. РЕКОМЕНДАЦІЇ для підвищення безпеки:")
            for rec in recommendations:
                print(f"   - {rec}")
        else:
            print("\n3. РЕКОМЕНДАЦІЇ: Пароль має максимальну надійність і не потребує змін.")

if __name__ == '__main__':
    run_analysis()