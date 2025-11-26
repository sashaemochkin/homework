from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Order(Base):
    """Модель заказа клиента"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    order_number = Column(String(20), unique=True, nullable=False)
    order_date = Column(Date, default=datetime.now)
    status = Column(String(20), default='pending')  # pending, completed, cancelled
    total_amount = Column(Float, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Связь с клиентом
    client = relationship("Client", backref="orders")
    
    def to_dict(self):
        """Преобразование объекта в словарь"""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'status': self.status,
            'total_amount': self.total_amount,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'client_name': f"{self.client.last_name} {self.client.first_name}" if self.client else None
        }
    
    def __repr__(self):
        return f"<Order(id={self.id}, number='{self.order_number}', amount={self.total_amount})>"
