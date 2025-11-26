from typing import Dict, Any, List, Optional
from decimal import Decimal, InvalidOperation
from datetime import datetime

class OrderValidator:
    """Валидатор для данных заказа"""
    
    def validate_order_data(order_data: Dict[str, Any]) -> List[str]:
        """Валидация данных заказа"""
        errors = []
        
        # Проверка обязательных полей
        if 'client_id' not in order_data or not order_data['client_id']:
            errors.append("Не указан ID клиента")
        
        if 'items' not in order_data or not order_data['items']:
            errors.append("Заказ должен содержать хотя бы один товар")
        else:
            # Валидация товаров
            for i, item in enumerate(order_data['items']):
                item_errors = OrderValidator.validate_order_item(item, i)
                errors.extend(item_errors)
        
        # Валидация статуса
        if 'status' in order_data:
            valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
            if order_data['status'] not in valid_statuses:
                errors.append(f"Неверный статус заказа. Допустимые значения: {', '.join(valid_statuses)}")
        
        # Валидация дат
        if 'order_date' in order_data and order_data['order_date']:
            if not isinstance(order_data['order_date'], datetime):
                errors.append("Неверный формат даты заказа")
        
        if 'delivery_date' in order_data and order_data['delivery_date']:
            if not isinstance(order_data['delivery_date'], datetime):
                errors.append("Неверный формат даты доставки")
        
        return errors
    
    def validate_order_item(item_data: Dict[str, Any], index: int = 0) -> List[str]:
        """Валидация данных товара в заказе"""
        errors = []
        
        if 'product_name' not in item_data or not item_data['product_name']:
            errors.append(f"Товар #{index + 1}: не указано наименование товара")
        elif len(item_data['product_name']) > 200:
            errors.append(f"Товар #{index + 1}: наименование товара слишком длинное")
        
        if 'quantity' not in item_data:
            errors.append(f"Товар #{index + 1}: не указано количество")
        else:
            try:
                quantity = int(item_data['quantity'])
                if quantity <= 0:
                    errors.append(f"Товар #{index + 1}: количество должно быть положительным числом")
            except (ValueError, TypeError):
                errors.append(f"Товар #{index + 1}: неверный формат количества")
        
        if 'price' not in item_data:
            errors.append(f"Товар #{index + 1}: не указана цена")
        else:
            try:
                price = Decimal(str(item_data['price']))
                if price < 0:
                    errors.append(f"Товар #{index + 1}: цена не может быть отрицательной")
            except (ValueError, InvalidOperation):
                errors.append(f"Товар #{index + 1}: неверный формат цены")
        
        return errors
    
    def validate_order_filters(filters: Dict[str, Any]) -> List[str]:
        """Валидация фильтров для поиска заказов"""
        errors = []
        
        # Валидация дат
        date_fields = ['start_date', 'end_date']
        for field in date_fields:
            if field in filters and filters[field]:
                if not isinstance(filters[field], datetime):
                    errors.append(f"Неверный формат даты для фильтра '{field}'")
        
        # Валидация числовых полей
        numeric_fields = ['min_amount', 'max_amount']
        for field in numeric_fields:
            if field in filters and filters[field] is not None:
                try:
                    value = Decimal(str(filters[field]))
                    if value < 0:
                        errors.append(f"Фильтр '{field}' не может быть отрицательным")
                except (ValueError, InvalidOperation):
                    errors.append(f"Неверный формат для фильтра '{field}'")
        
        # Валидация статуса
        if 'status' in filters and filters['status']:
            valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
            if filters['status'] not in valid_statuses:
                errors.append(f"Неверный статус для фильтра. Допустимые значения: {', '.join(valid_statuses)}")
        
        return errors
