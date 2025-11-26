from sqlalchemy import create_engine, and_, or_, func
from sqlalchemy.orm import sessionmaker
from src.models.order import Order, Base
from src.models.client import Client
from src.validators.order_validators import OrderValidator
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random
import string

class OrderService:
    """Сервис для управления заказами с расширенной функциональностью"""
    
    def __init__(self, database_url: str = "sqlite:///clients.db"):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.validator = OrderValidator()
    
    def generate_order_number(self) -> str:
        """Генерация уникального номера заказа"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"ORD-{timestamp}-{random_part}"
    
    def create_order(self, order_data: Dict) -> Dict:
        """Создание нового заказа с обновлением статистики клиента"""
        # Валидация данных
        is_valid, errors = self.validator.validate_order_data(order_data)
        if not is_valid:
            return {'success': False, 'errors': errors}
        
        session = self.Session()
        try:
            # Проверка существования клиента
            client = session.query(Client).get(order_data['client_id'])
            if not client:
                return {'success': False, 'errors': ['Клиент не найден']}
            
            # Создание заказа
            order = Order(
                client_id=order_data['client_id'],
                order_number=self.generate_order_number(),
                total_amount=order_data['total_amount'],
                description=order_data.get('description', ''),
                status=order_data.get('status', 'pending'),
                order_date=order_data.get('order_date', datetime.now().date())
            )
            
            # Обновление статистики клиента
            client.total_orders += 1
            client.total_revenue += order.total_amount
            
            session.add(order)
            session.commit()
            
            return {'success': True, 'order': order.to_dict()}
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'errors': [f'Ошибка базы данных: {str(e)}']}
        finally:
            session.close()
    
    def get_client_orders(self, client_id: int) -> List[Dict]:
        """Получение заказов клиента"""
        session = self.Session()
        try:
            orders = session.query(Order).filter_by(client_id=client_id).order_by(
                Order.order_date.desc()
            ).all()
            return [order.to_dict() for order in orders]
        finally:
            session.close()
    
    def search_orders(self, search_params: Dict) -> Dict:
        """Расширенный поиск заказов с пагинацией"""
        # Валидация параметров поиска
        is_valid, errors = self.validator.validate_order_search_params(search_params)
        if not is_valid:
            return {'success': False, 'errors': errors, 'orders': [], 'total_count': 0}
        
        session = self.Session()
        try:
            query = session.query(Order).join(Client)
            
            # Базовые фильтры
            if 'client_id' in search_params:
                query = query.filter(Order.client_id == search_params['client_id'])
            
            if 'status' in search_params:
                query = query.filter(Order.status == search_params['status'])
            
            if 'min_amount' in search_params:
                query = query.filter(Order.total_amount >= search_params['min_amount'])
            
            if 'max_amount' in search_params:
                query = query.filter(Order.total_amount <= search_params['max_amount'])
            
            if 'start_date' in search_params:
                query = query.filter(Order.order_date >= search_params['start_date'])
            
            if 'end_date' in search_params:
                query = query.filter(Order.order_date <= search_params['end_date'])
            
            # Поиск по имени клиента
            if 'client_name' in search_params:
                search_term = f"%{search_params['client_name']}%"
                query = query.filter(
                    or_(
                        Client.first_name.ilike(search_term),
                        Client.last_name.ilike(search_term)
                    )
                )
            
            # Поиск по номеру заказа
            if 'order_number' in search_params:
                query = query.filter(Order.order_number.ilike(f"%{search_params['order_number']}%"))
            
            # Получаем общее количество для пагинации
            total_count = query.count()
            
            # Применяем сортировку
            sort_by = search_params.get('sort_by', 'order_date')
            sort_order = search_params.get('sort_order', 'desc')
            
            if sort_by == 'order_date':
                order_column = Order.order_date
            elif sort_by == 'total_amount':
                order_column = Order.total_amount
            elif sort_by == 'client_name':
                order_column = Client.last_name
            else:
                order_column = Order.order_date
            
            if sort_order == 'asc':
                query = query.order_by(order_column.asc())
            else:
                query = query.order_by(order_column.desc())
            
            # Применяем пагинацию
            page = search_params.get('page', 1)
            per_page = search_params.get('per_page', 50)
            offset = (page - 1) * per_page
            
            query = query.offset(offset).limit(per_page)
            
            orders = query.all()
            
            return {
                'success': True, 
                'orders': [order.to_dict() for order in orders],
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            }
            
        except Exception as e:
            return {'success': False, 'errors': [f'Ошибка поиска: {str(e)}'], 'orders': [], 'total_count': 0}
        finally:
            session.close()
    
    def update_order_status(self, order_id: int, status: str) -> Dict:
        """Обновление статуса заказа"""
        # Валидация данных
        is_valid, errors = self.validator.validate_order_status_update(order_id, status)
        if not is_valid:
            return {'success': False, 'errors': errors}
        
        session = self.Session()
        try:
            order = session.query(Order).get(order_id)
            if not order:
                return {'success': False, 'errors': ['Заказ не найден']}
            
            order.status = status
            session.commit()
            
            return {'success': True, 'order': order.to_dict()}
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'errors': [f'Ошибка базы данных: {str(e)}']}
        finally:
            session.close()
    
    def get_order(self, order_id: int) -> Dict:
        """Получение заказа по ID"""
        session = self.Session()
        try:
            order = session.query(Order).get(order_id)
            if not order:
                return {'success': False, 'errors': ['Заказ не найден']}
            
            return {'success': True, 'order': order.to_dict()}
        finally:
            session.close()
    
    def delete_order(self, order_id: int) -> Dict:
        """Удаление заказа с обновлением статистики клиента"""
        session = self.Session()
        try:
            order = session.query(Order).get(order_id)
            if not order:
                return {'success': False, 'errors': ['Заказ не найден']}
            
            # Получаем клиента для обновления статистики
            client = session.query(Client).get(order.client_id)
            if client:
                client.total_orders -= 1
                client.total_revenue -= order.total_amount
            
            session.delete(order)
            session.commit()
            
            return {'success': True, 'message': 'Заказ успешно удален'}
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'errors': [f'Ошибка удаления: {str(e)}']}
        finally:
            session.close()
    
    def get_order_statistics(self, period_days: int = 30, client_id: Optional[int] = None) -> Dict:
        """Получение расширенной статистики по заказам"""
        session = self.Session()
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=period_days)
            
            query = session.query(Order).filter(
                Order.order_date >= start_date,
                Order.order_date <= end_date
            )
            
            if client_id:
                query = query.filter(Order.client_id == client_id)
            
            # Основная статистика
            total_orders = query.count()
            total_revenue = session.query(func.sum(Order.total_amount)).filter(
                Order.order_date >= start_date,
                Order.order_date <= end_date
            ).scalar() or 0
            
            # Статистика по статусам
            status_stats = session.query(
                Order.status,
                func.count(Order.id),
                func.sum(Order.total_amount)
            ).filter(
                Order.order_date >= start_date,
                Order.order_date <= end_date
            ).group_by(Order.status).all()
            
            # Ежедневная статистика
            daily_stats = session.query(
                Order.order_date,
                func.count(Order.id),
                func.sum(Order.total_amount)
            ).filter(
                Order.order_date >= start_date,
                Order.order_date <= end_date
            ).group_by(Order.order_date).order_by(Order.order_date).all()
            
            # Топ клиентов по выручке
            top_clients = session.query(
                Client.id,
                Client.first_name,
                Client.last_name,
                func.count(Order.id),
                func.sum(Order.total_amount)
            ).join(Order).filter(
                Order.order_date >= start_date,
                Order.order_date <= end_date
            ).group_by(Client.id, Client.first_name, Client.last_name).order_by(
                func.sum(Order.total_amount).desc()
            ).limit(10).all()
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': period_days
                },
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'average_order_value': total_revenue / total_orders if total_orders > 0 else 0,
                'status_stats': [
                    {
                        'status': status,
                        'count': count,
                        'revenue': revenue or 0
                    }
                    for status, count, revenue in status_stats
                ],
                'daily_stats': [
                    {
                        'date': date.isoformat(),
                        'orders': count,
                        'revenue': revenue or 0
                    }
                    for date, count, revenue in daily_stats
                ],
                'top_clients': [
                    {
                        'client_id': client_id,
                        'name': f"{first_name} {last_name}",
                        'orders': count,
                        'revenue': revenue or 0
                    }
                    for client_id, first_name, last_name, count, revenue in top_clients
                ]
            }
        finally:
            session.close()
