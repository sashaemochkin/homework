from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import re

Base = declarative_base()

class Client(Base):
    #Модель клиента
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    patronymic = Column(String(50))
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    registration_date = Column(Date, default=datetime.now)
    city = Column(String(50))
    notes = Column(Text)
    status = Column(String(20), default='active')
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        #Преобразование объекта в словарь
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'patronymic': self.patronymic,
            'email': self.email,
            'phone': self.phone,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'city': self.city,
            'notes': self.notes,
            'status': self.status,
            'total_orders': self.total_orders,
            'total_revenue': self.total_revenue,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def validate_data(self):
        #Валидация данных клиента
        errors = []
        
        # Проверка ФИО на кириллицу
        if not re.match(r'^[А-ЯЁа-яё\-]+$', self.first_name):
            errors.append("Имя должно содержать только кириллические буквы и дефисы")
        
        if not re.match(r'^[А-ЯЁа-яё\-]+$', self.last_name):
            errors.append("Фамилия должна содержать только кириллические буквы и дефисы")
        
        if self.patronymic and not re.match(r'^[А-ЯЁа-яё\-]+$', self.patronymic):
            errors.append("Отчество должно содержать только кириллические буквы и дефисы")
        
        # Проверка email
        if self.email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
            errors.append("Неверный формат email")
        
        # Проверка телефона
        if self.phone and not re.match(r'^\+7\d{10}$', self.phone):
            errors.append("Телефон должен быть в формате +7XXXXXXXXXX")
        
        return errors
    
    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.last_name} {self.first_name}')>"
