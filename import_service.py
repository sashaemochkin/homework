import pandas as pd
import logging
from typing import Dict, List
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.client import Client
from src.models.order import Order
from src.services.client_service import ClientService
from src.services.order_service import OrderService
from src.validators.client_validators import ClientValidator
from src.validators.order_validators import OrderValidator

class ImportService:
    """Сервис для импорта данных из Excel"""
    
    def __init__(self, client_service: ClientService, order_service: OrderService):
        self.client_service = client_service
        self.order_service = order_service
        self.client_validator = ClientValidator()
        self.order_validator = OrderValidator()
        self.logger = logging.getLogger(__name__)
    
    def import_clients_from_excel(self, file_path: str) -> Dict:
        """
        Импорт клиентов из Excel файла
        """
        try:
            if not Path(file_path).exists():
                return {'success': False, 'errors': [f'Файл {file_path} не найден']}
            
            # Чтение Excel файла
            df = pd.read_excel(file_path)
            self.logger.info(f"Загружен файл с {len(df)} строками")
            
            results = {
                'total_rows': len(df),
                'imported': 0,
                'updated': 0,
                'errors': [],
                'skipped': 0
            }
            
            for index, row in df.iterrows():
                try:
                    client_data = self._parse_client_row(row, index + 2)
                    if not client_data:
                        results['skipped'] += 1
                        continue
                    
                    # Проверяем существование клиента по email
                    if client_data.get('email'):
                        existing_clients = self.client_service.search_clients({
                            'email': client_data['email']
                        })
                        
                        if existing_clients:
                            # Обновляем существующего клиента
                            client_id = existing_clients[0]['id']
                            update_result = self.client_service.update_client(client_id, client_data)
                            if update_result['success']:
                                results['updated'] += 1
                            else:
                                results['errors'].append({
                                    'row': index + 2,
                                    'error': f"Не удалось обновить клиента {client_data['email']}",
                                    'details': update_result['errors']
                                })
                        else:
                            # Добавляем нового клиента
                            add_result = self.client_service.add_client(client_data)
                            if add_result['success']:
                                results['imported'] += 1
                            else:
                                results['errors'].append({
                                    'row': index + 2,
                                    'error': f"Не удалось добавить клиента {client_data['email']}",
                                    'details': add_result['errors']
                                })
                    else:
                        # Клиенты без email просто добавляются
                        add_result = self.client_service.add_client(client_data)
                        if add_result['success']:
                            results['imported'] += 1
                        else:
                            results['errors'].append({
                                'row': index + 2,
                                'error': "Не удалось добавить клиента",
                                'details': add_result['errors']
                            })
                            
                except Exception as e:
                    results['errors'].append({
                        'row': index + 2,
                        'error': str(e),
                        'data': dict(row)
                    })
                    self.logger.error(f"Ошибка в строке {index + 2}: {e}")
            
            return {'success': True, 'results': results}
            
        except Exception as e:
            self.logger.error(f"Ошибка импорта клиентов: {e}")
            return {'success': False, 'errors': [f'Ошибка импорта: {str(e)}']}
    
    def _parse_client_row(self, row: pd.Series, row_number: int) -> Dict:
        """Парсинг строки с данными клиента"""
        client_data = {}
        
        # Обработка ФИО
        if 'first_name' in row and pd.notna(row['first_name']):
            client_data['first_name'] = str(row['first_name']).strip()
        else:
            raise ValueError("Не указано имя клиента")
        
        if 'last_name' in row and pd.notna(row['last_name']):
            client_data['last_name'] = str(row['last_name']).strip()
        else:
            raise ValueError("Не указана фамилия клиента")
        
        if 'patronymic' in row and pd.notna(row['patronymic']):
            client_data['patronymic'] = str(row['patronymic']).strip()
        
        # Контактные данные
        if 'email' in row and pd.notna(row['email']):
            client_data['email'] = str(row['email']).strip().lower()
        
        if 'phone' in row and pd.notna(row['phone']):
            client_data['phone'] = str(row['phone']).strip()
        
        if 'city' in row and pd.notna(row['city']):
            client_data['city'] = str(row['city']).strip()
        
        if 'notes' in row and pd.notna(row['notes']):
            client_data['notes'] = str(row['notes']).strip()
        
        # Валидация данных
        is_valid, errors = self.client_validator.validate_client_data(client_data)
        if not is_valid:
            raise ValueError(f"Ошибки валидации: {', '.join(errors)}")
        
        return client_data
    
    def import_orders_from_excel(self, file_path: str) -> Dict:
        """
        Импорт заказов из Excel файла
        """
        try:
            if not Path(file_path).exists():
                return {'success': False, 'errors': [f'Файл {file_path} не найден']}
            
            df = pd.read_excel(file_path)
            self.logger.info(f"Загружен файл заказов с {len(df)} строками")
            
            results = {
                'total_rows': len(df),
                'imported': 0,
                'errors': [],
                'skipped': 0
            }
            
            for index, row in df.iterrows():
                try:
                    order_data = self._parse_order_row(row, index + 2)
                    if not order_data:
                        results['skipped'] += 1
                        continue
                    
                    # Создаем заказ
                    create_result = self.order_service.create_order(order_data)
                    if create_result['success']:
                        results['imported'] += 1
                    else:
                        results['errors'].append({
                            'row': index + 2,
                            'error': "Не удалось создать заказ",
                            'details': create_result['errors']
                        })
                        
                except Exception as e:
                    results['errors'].append({
                        'row': index + 2,
                        'error': str(e),
                        'data': dict(row)
                    })
            
            return {'success': True, 'results': results}
            
        except Exception as e:
            self.logger.error(f"Ошибка импорта заказов: {e}")
            return {'success': False, 'errors': [f'Ошибка импорта: {str(e)}']}
    
    def _parse_order_row(self, row: pd.Series, row_number: int) -> Dict:
        """Парсинг строки с данными заказа"""
        order_data = {}
        
        # ID клиента
        if 'client_id' in row and pd.notna(row['client_id']):
            try:
                order_data['client_id'] = int(row['client_id'])
            except (ValueError, TypeError):
                raise ValueError("Неверный формат ID клиента")
        else:
            raise ValueError("Не указан ID клиента")
        
        # Сумма заказа
        if 'total_amount' in row and pd.notna(row['total_amount']):
            try:
                order_data['total_amount'] = float(row['total_amount'])
            except (ValueError, TypeError):
                raise ValueError("Неверный формат суммы заказа")
        else:
            raise ValueError("Не указана сумма заказа")
        
        # Статус заказа
        if 'status' in row and pd.notna(row['status']):
            status = str(row['status']).strip().lower()
            if status in ['pending', 'completed', 'cancelled']:
                order_data['status'] = status
        
        # Дата заказа
        if 'order_date' in row and pd.notna(row['order_date']):
            try:
                if isinstance(row['order_date'], datetime):
                    order_data['order_date'] = row['order_date'].date()
                else:
                    order_data['order_date'] = datetime.strptime(
                        str(row['order_date']), '%Y-%m-%d'
                    ).date()
            except ValueError:
                order_data['order_date'] = datetime.now().date()
        
        # Описание
        if 'description' in row and pd.notna(row['description']):
            order_data['description'] = str(row['description']).strip()
        
        # Валидация данных
        is_valid, errors = self.order_validator.validate_order_data(order_data)
        if not is_valid:
            raise ValueError(f"Ошибки валидации: {', '.join(errors)}")
        
        return order_data
    
    def create_import_template(self, data_type: str) -> str:
        """
        Создание шаблона Excel для импорта
        """
        if data_type == 'clients':
            template_data = {
                'first_name': ['Иван', 'Мария'],
                'last_name': ['Иванов', 'Петрова'],
                'patronymic': ['Иванович', 'Сергеевна'],
                'email': ['ivanov@mail.ru', 'petrova@yandex.ru'],
                'phone': ['+79161234567', '+79031234568'],
                'city': ['Москва', 'Санкт-Петербург'],
                'notes': ['Постоянный клиент', 'Новый клиент']
            }
            filename = 'template_clients.xlsx'
        elif data_type == 'orders':
            template_data = {
                'client_id': [1, 2],
                'total_amount': [5000.0, 7500.0],
                'status': ['pending', 'completed'],
                'order_date': [datetime.now().date(), datetime.now().date()],
                'description': ['Заказ №1', 'Заказ №2']
            }
            filename = 'template_orders.xlsx'
        else:
            raise ValueError("Неверный тип данных. Используйте 'clients' или 'orders'")
        
        df = pd.DataFrame(template_data)
        df.to_excel(filename, index=False)
        
        return filename
