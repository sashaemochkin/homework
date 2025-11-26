from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Client(Base):
    """Модель клиента"""
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    patronymic = Column(String(50))
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    city = Column(String(50))
    notes = Column(Text)
    status = Column(String(20), default='active')
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    registration_date = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        """Преобразование объекта в словарь"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'patronymic': self.patronymic,
            'email': self.email,
            'phone': self.phone,
            'city': self.city,
            'notes': self.notes,
            'status': self.status,
            'total_orders': self.total_orders,
            'total_revenue': self.total_revenue,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.first_name} {self.last_name}')>"
