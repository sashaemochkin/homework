import re
from typing import List, Tuple

def validate_russian_name(name: str) -> Tuple[bool, str]:
    """Валидация русского имени/фамилии"""
    if not name or not name.strip():
        return False, "Имя не может быть пустым"
    
    if not re.match(r'^[А-ЯЁа-яё\-]+$', name.strip()):
        return False, "Должны быть только кириллические буквы и дефис"
    
    if len(name.strip()) < 2:
        return False, "Слишком короткое имя"
    
    if len(name.strip()) > 50:
        return False, "Слишком длинное имя"
    
    return True, ""

def validate_email(email: str) -> Tuple[bool, str]:
    """Валидация email"""
    if not email:
        return True, ""  # Email не обязателен
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Неверный формат email"
    
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    """Валидация номера телефона"""
    if not phone:
        return True, ""  # Телефон не обязателен
    
    if not re.match(r'^\+7\d{10}$', phone):
        return False, "Телефон должен быть в формате +7XXXXXXXXXX"
    
    return True, ""

def validate_password(password: str) -> Tuple[bool, List[str]]:
    """Валидация пароля"""
    errors = []
    
    if len(password) < 8:
        errors.append("Пароль должен быть не менее 8 символов")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Добавьте хотя бы одну заглавную букву")
    
    if not re.search(r'\d', password):
        errors.append("Добавьте хотя бы одну цифру")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password):
        errors.append("Добавьте хотя бы один специальный символ")
    
    return len(errors) == 0, errors
