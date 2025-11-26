from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

class Repository(ABC):
    """Абстрактный базовый класс репозитория (Pattern: Repository)"""
    
   
    def get(self, id: int) -> Optional[Any]:
        pass
    
    
    def add(self, entity: Any) -> Any:
        pass
    
    
    def update(self, id: int, updates: Dict) -> Optional[Any]:
        pass
    
   
    def delete(self, id: int) -> bool:
        pass
    
    
    def list(self, filters: Dict = None) -> List[Any]:
        pass

class ClientRepository(Repository):
    """Реализация репозитория для клиентов (Pattern: Repository)"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get(self, client_id: int) -> Optional[Dict]:
        query = "SELECT * FROM clients WHERE id = ?"
        result = self.db.execute(query, (client_id,)).fetchone()
        return dict(result) if result else None
    
    def add(self, client_data: Dict) -> Dict:
        query = """
            INSERT INTO clients (first_name, last_name, phone, email, registration_date, notes, city)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            client_data['first_name'],
            client_data['last_name'],
            client_data['phone'],
            client_data['email'],
            client_data.get('registration_date', datetime.now()),
            client_data.get('notes'),
            client_data.get('city')
        )
        
        cursor = self.db.execute(query, params)
        client_id = cursor.lastrowid
        
        return {**client_data, 'id': client_id}
    
    def update(self, client_id: int, updates: Dict) -> Optional[Dict]:
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE clients SET {set_clause} WHERE id = ?"
        params = list(updates.values()) + [client_id]
        
        cursor = self.db.execute(query, params)
        if cursor.rowcount == 0:
            return None
        
        return self.get(client_id)
    
    def delete(self, client_id: int) -> bool:
        query = "DELETE FROM clients WHERE id = ?"
        cursor = self.db.execute(query, (client_id,))
        return cursor.rowcount > 0
    
    def list(self, filters: Dict = None) -> List[Dict]:
        query = "SELECT * FROM clients WHERE 1=1"
        params = []
        
        if filters:
            for key, value in filters.items():
                if value:
                    query += f" AND {key} LIKE ?"
                    params.append(f"%{value}%")
        
        results = self.db.execute(query, params).fetchall()
        return [dict(row) for row in results]

# src/patterns/service.py
class ClientService:
    """Сервис для работы с клиентами (Pattern: Service)"""
    
    def __init__(self, repository: ClientRepository, validator: 'ClientValidator'):
        self.repository = repository
        self.validator = validator
    
    def create_client(self, client_data: Dict) -> Dict:
        """Создание клиента с валидацией"""
        if not self.validator.validate(client_data):
            raise ValueError("Invalid client data")
        
        return self.repository.add(client_data)
    
    def find_clients(self, filters: Dict = None) -> List[Dict]:
        """Поиск клиентов с фильтрацией"""
        return self.repository.list(filters)
    
    def update_client(self, client_id: int, updates: Dict) -> Optional[Dict]:
        """Обновление клиента с валидацией"""
        # Валидируем только изменяемые поля
        validation_data = {k: v for k, v in updates.items() if k in ['first_name', 'last_name', 'email', 'phone']}
        if validation_data and not self.validator.validate(validation_data, partial=True):
            raise ValueError("Invalid update data")
        
        return self.repository.update(client_id, updates)

# src/patterns/factory.py
class ValidatorFactory:
    """Фабрика валидаторов (Pattern: Factory)"""
    
    @staticmethod
    def create_validator(validator_type: str):
        if validator_type == 'client':
            return ClientValidator()
        elif validator_type == 'order':
            return OrderValidator()
        elif validator_type == 'email':
            return EmailValidator()
        else:
            raise ValueError(f"Unknown validator type: {validator_type}")

class ClientValidator:
    """Валидатор клиентов (Pattern: Strategy)"""
    
    def validate(self, data: Dict, partial: bool = False) -> bool:
        required_fields = ['first_name', 'last_name', 'phone', 'email']
        
        if not partial:
            for field in required_fields:
                if field not in data or not data[field]:
                    return False
        
        # Валидация отдельных полей
        validators = {
            'first_name': validate_fio,
            'last_name': validate_fio,
            'email': validate_email,
            'phone': validate_phone
        }
        
        for field, validator in validators.items():
            if field in data and data[field]:
                if not validator(data[field]):
                    return False
        
        return True

# src/patterns/observer.py
class Event:
    """Базовый класс события (Pattern: Observer)"""
    
    def __init__(self, name: str, data: Dict = None):
        self.name = name
        self.data = data or {}
        self.timestamp = datetime.now()

class EventObserver:
    """Наблюдатель событий"""
    
    def __init__(self):
        self._subscribers = {}
    
    def subscribe(self, event_type: str, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def notify(self, event: Event):
        event_type = event.name
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")

# Применение Observer в сервисе клиентов
class ObservableClientService(ClientService):
    """Сервис клиентов с поддержкой событий"""
    
    def __init__(self, repository: ClientRepository, validator: ClientValidator):
        super().__init__(repository, validator)
        self.observer = EventObserver()
    
    def create_client(self, client_data: Dict) -> Dict:
        client = super().create_client(client_data)
        
        # Уведомляем о создании клиента
        event = Event('client_created', {'client_id': client['id'], 'client_data': client_data})
        self.observer.notify(event)
        
        return client
    
    def delete_client(self, client_id: int) -> bool:
        result = super().delete_client(client_id)
        
        if result:
            # Уведомляем об удалении клиента
            event = Event
