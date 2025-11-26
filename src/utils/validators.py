import re
from datetime import datetime

def validate_email(email):
    """Валидация email-адреса"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

def validate_phone(phone):
    """Валидация телефонного номера"""
    # Убираем все символы кроме цифр
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 10 and len(digits) <= 15

def validate_date(date_str):
    """Валидация и преобразование даты"""
    formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError("Неверный формат даты. Используйте ГГГГ-ММ-ДД, ДД.ММ.ГГГГ или ДД/ММ/ГГГГ")