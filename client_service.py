from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from src.models.client import Client, Base
from src.validators.client_validators import ClientValidator
from typing import List, Dict, Optional

class ClientService:
    """Сервис для управления клиентами"""
    
    def __init__(self, database_url: str = "sqlite:///clients.db"):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.validator = ClientValidator()
    
    def add_client(self, client_data: Dict) -> Dict:
        """Добавление нового клиента"""
        # Валидация данных
        is_valid, errors = self.validator.validate_client_data(client_data)
        if not is_valid:
            return {'success': False, 'errors': errors}
        
        session = self.Session()
        try:
            # Проверка уникальности email
            if client_data.get('email'):
                existing_client = session.query(Client).filter_by(
                    email=client_data['email']
                ).first()
                if existing_client:
                    return {'success': False, 'errors': ['Клиент с таким email уже существует']}
            
            # Создание клиента
            client = Client(
                first_name=client_data['first_name'],
                last_name=client_data['last_name'],
                patronymic=client_data.get('patronymic'),
                email=client_data.get('email'),
                phone=client_data.get('phone'),
                city=client_data.get('city'),
                notes=client_data.get('notes')
            )
            
            session.add(client)
            session.commit()
            
            return {'success': True, 'client': client.to_dict()}
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'errors': [f'Ошибка базы данных: {str(e)}']}
        finally:
            session.close()
    
    def get_client(self, client_id: int) -> Optional[Dict]:
        """Получение клиента по ID"""
        session = self.Session()
        try:
            client = session.query(Client).get(client_id)
            return client.to_dict() if client else None
        finally:
            session.close()
    
    def search_clients(self, search_params: Dict) -> List[Dict]:
        """Поиск клиентов по параметрам"""
        session = self.Session()
        try:
            query = session.query(Client)
            
            # Поиск по имени/фамилии/отчеству
            if 'first_name' in search_params:
                query = query.filter(Client.first_name.ilike(f"%{search_params['first_name']}%"))
            if 'last_name' in search_params:
                query = query.filter(Client.last_name.ilike(f"%{search_params['last_name']}%"))
            if 'patronymic' in search_params:
                query = query.filter(Client.patronymic.ilike(f"%{search_params['patronymic']}%"))
            
            # Поиск по контактным данным
            if 'email' in search_params:
                query = query.filter(Client.email.ilike(f"%{search_params['email']}%"))
            if 'phone' in search_params:
                query = query.filter(Client.phone.ilike(f"%{search_params['phone']}%"))
            if 'city' in search_params:
                query = query.filter(Client.city.ilike(f"%{search_params['city']}%"))
            
            # Фильтрация по статусу
            if 'status' in search_params:
                query = query.filter(Client.status == search_params['status'])
            
            # Фильтрация по количеству заказов
            if 'min_orders' in search_params:
                query = query.filter(Client.total_orders >= search_params['min_orders'])
            if 'max_orders' in search_params:
                query = query.filter(Client.total_orders <= search_params['max_orders'])
            
            clients = query.order_by(Client.last_name, Client.first_name).all()
            return [client.to_dict() for client in clients]
            
        finally:
            session.close()
    
    def update_client(self, client_id: int, updates: Dict) -> Dict:
        """Обновление данных клиента"""
        # Валидация обновляемых данных
        validation_data = {k: v for k, v in updates.items() if k in [
            'first_name', 'last_name', 'patronymic', 'email', 'phone', 'city', 'notes'
        ]}
        
        if validation_data:
            is_valid, errors = self.validator.validate_client_data(validation_data, partial=True)
            if not is_valid:
                return {'success': False, 'errors': errors}
        
        session = self.Session()
        try:
            client = session.query(Client).get(client_id)
            if not client:
                return {'success': False, 'errors': ['Клиент не найден']}
            
            # Проверка уникальности email
            if 'email' in updates and updates['email']:
                existing_client = session.query(Client).filter(
                    and_(
                        Client.email == updates['email'],
                        Client.id != client_id
                    )
                ).first()
                if existing_client:
                    return {'success': False, 'errors': ['Клиент с таким email уже существует']}
            
            # Обновление полей
            for key, value in updates.items():
                if hasattr(client, key):
                    setattr(client, key, value)
            
            session.commit()
            return {'success': True, 'client': client.to_dict()}
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'errors': [f'Ошибка базы данных: {str(e)}']}
        finally:
            session.close()
    
    def delete_client(self, client_id: int) -> Dict:
        """Удаление клиента"""
        session = self.Session()
        try:
            client = session.query(Client).get(client_id)
            if not client:
                return {'success': False, 'errors': ['Клиент не найден']}
            
            session.delete(client)
            session.commit()
            return {'success': True, 'message': 'Клиент успешно удален'}
            
        except Exception as e:
            session.rollback()
            return {'success': False, 'errors': [f'Ошибка удаления: {str(e)}']}
        finally:
            session.close()
    
    def get_client_statistics(self) -> Dict:
        """Получение статистики по клиентам"""
        session = self.Session()
        try:
            total_clients = session.query(Client).count()
            active_clients = session.query(Client).filter_by(status='active').count()
            total_revenue = session.query(Client).with_entities(
                func.sum(Client.total_revenue)
            ).scalar() or 0
            total_orders = session.query(Client).with_entities(
                func.sum(Client.total_orders)
            ).scalar() or 0
            
            # Статистика по городам
            city_stats = session.query(
                Client.city,
                func.count(Client.id),
                func.sum(Client.total_revenue)
            ).filter(Client.city.isnot(None)).group_by(Client.city).all()
            
            return {
                'total_clients': total_clients,
                'active_clients': active_clients,
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'city_stats': [
                    {'city': city, 'count': count, 'revenue': revenue or 0}
                    for city, count, revenue in city_stats
                ]
            }
        finally:
            session.close()
