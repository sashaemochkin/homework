import unittest
from unittest.mock import Mock, patch
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.client_service import ClientService
from utils.validators import validate_fio, validate_email, validate_phone

class TestClientServiceUnit(unittest.TestCase):
    """Модульные тесты для ClientService"""
    
    def setUp(self):
        self.mock_conn = Mock(spec=sqlite3.Connection)
        self.mock_cursor = Mock(spec=sqlite3.Cursor)
        self.mock_conn.cursor.return_value = self.mock_cursor
        
        # Патчим соединение с базой данных
        self.patcher = patch('sqlite3.connect')
        self.mock_connect = self.patcher.start()
        self.mock_connect.return_value = self.mock_conn
        
        self.client_service = ClientService('test.db')
    
    def tearDown(self):
        self.patcher.stop()
    
    def test_add_client_success(self):
        """Тест успешного добавления клиента"""
        # Настройка моков
        self.mock_cursor.lastrowid = 1
        
        client_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'phone': '+79161234567',
            'email': 'ivan@mail.ru'
        }
        
        client = self.client_service.add_client(client_data)
        
        # Проверяем вызовы базы данных
        self.mock_cursor.execute.assert_called()
        self.mock_conn.commit.assert_called_once()
        
        # Проверяем результат
        self.assertEqual(client.id, 1)
        self.assertEqual(client.first_name, 'Иван')
    
    def test_add_client_validation_failure(self):
        """Тест валидации при добавлении клиента"""
        invalid_client_data = {
            'first_name': 'John',  # латиница
            'last_name': 'Иванов',
            'phone': '+79161234567',
            'email': 'ivan@mail.ru'
        }
        
        with self.assertRaises(ValueError):
            self.client_service.add_client(invalid_client_data)
        
        # Проверяем, что запрос к БД не выполнялся
        self.mock_cursor.execute.assert_not_called()

class TestValidatorsUnit(unittest.TestCase):
    """Модульные тесты для валидаторов"""
    
    def test_validate_fio(self):
        self.assertTrue(validate_fio('Иван'))
        self.assertTrue(validate_fio('Анна-Мария'))
        self.assertFalse(validate_fio('John'))
        self.assertFalse(validate_fio('Иван123'))
    
    def test_validate_email(self):
        self.assertTrue(validate_email('test@example.com'))
        self.assertTrue(validate_email('user.name+tag@domain.co.uk'))
        self.assertFalse(validate_email('invalid-email'))
        self.assertFalse(validate_email('@no-username.com'))
    
    def test_validate_phone(self):
        self.assertTrue(validate_phone('+79161234567'))
        self.assertTrue(validate_phone('89161234567'))
        self.assertTrue(validate_phone('+7 (916) 123-45-67'))
        self.assertFalse(validate_phone('123456'))
        self.assertFalse(validate_phone('+791612345678'))  # слишком длинный

class TestDatabaseIntegration(unittest.TestCase):
    """Интеграционные тесты с реальной базой данных"""
    
    def setUp(self):
        self.test_db = ':memory:'  # Используем базу в памяти
        self.client_service = ClientService(self.test_db)
    
    def test_database_schema(self):
        """Тест структуры базы данных"""
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            
            # Проверяем существование таблицы clients
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='clients'
            """)
            table_exists = cursor.fetchone()
            self.assertIsNotNone(table_exists, "❌ Таблица clients не создана")
            
            # Проверяем структуру таблицы
            cursor.execute("PRAGMA table_info(clients)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            expected_columns = ['id', 'first_name', 'last_name', 'phone', 'email', 
                              'registration_date', 'notes', 'city']
            
            for expected_col in expected_columns:
                self.assertIn(expected_col, column_names, 
                            f"❌ Отсутствует колонка: {expected_col}")

if __name__ == '__main__':
    unittest.main()
