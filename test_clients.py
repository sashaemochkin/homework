import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.client_service import ClientService
from src.utils.validators import validate_russian_name, validate_email, validate_phone

class TestClientSystem(unittest.TestCase):
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.client_service = ClientService("sqlite:///:memory:")
    
    def test_validate_russian_name(self):
        """Тест валидации русских имен"""
        # Valid names
        self.assertTrue(validate_russian_name("Иван")[0])
        self.assertTrue(validate_russian_name("Анна-Мария")[0])
        self.assertTrue(validate_russian_name("Ёлкин")[0])
        
        # Invalid names
        self.assertFalse(validate_russian_name("John")[0])  # Latin
        self.assertFalse(validate_russian_name("Иван123")[0])  # Digits
        self.assertFalse(validate_russian_name("")[0])  # Empty
        self.assertFalse(validate_russian_name("А")[0])  # Too short
    
    def test_validate_email(self):
        """Тест валидации email"""
        self.assertTrue(validate_email("test@example.com")[0])
        self.assertTrue(validate_email("")[0])  # Empty is allowed
        self.assertFalse(validate_email("invalid-email")[0])
        self.assertFalse(validate_email("test@")[0])
    
    def test_add_client(self):
        """Тест добавления клиента"""
        client_data = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'email': 'ivan@test.com',
            'phone': '+79161234567'
        }
        
        result = self.client_service.add_client(client_data)
        self.assertTrue(result['success'])
        self.assertIn('client', result)
        self.assertEqual(result['client']['first_name'], 'Иван')
    
    def test_search_clients(self):
        """Тест поиска клиентов"""
        # Добавляем тестовых клиентов
        self.client_service.add_client({
            'first_name': 'Алексей', 
            'last_name': 'Сидоров',
            'city': 'Москва'
        })
        
        clients = self.client_service.search_clients({'city': 'Москва'})
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0]['last_name'], 'Сидоров')

if __name__ == '__main__':
    unittest.main()
