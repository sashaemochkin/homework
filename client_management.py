from config.database import get_db_connection
from utils.validators import validate_email, validate_phone, validate_date
from datetime import datetime

class ClientManager:
    """Класс для управления данными клиентов"""
    
    def __init__(self):
        self.connection = get_db_connection()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
    
    def add_client(self, full_name, phone, email, registration_date, notes=None):
        """Добавление нового клиента"""
        # Валидация данных
        if not full_name or len(full_name.strip()) < 3:
            raise ValueError("ФИО должно содержать минимум 3 символа")
        
        if not validate_phone(phone):
            raise ValueError("Неверный формат телефонного номера")
        
        if not validate_email(email):
            raise ValueError("Неверный формат email адреса")
        
        if isinstance(registration_date, str):
            registration_date = validate_date(registration_date)
        
        try:
            cur = self.connection.cursor()
            
            query = """
            INSERT INTO clients (full_name, phone, email, registration_date, notes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, full_name, phone, email, registration_date, notes, created_at
            """
            
            cur.execute(query, (full_name.strip(), phone.strip(), 
                               email.strip(), registration_date, notes))
            client_data = cur.fetchone()
            self.connection.commit()
            
            return {
                'id': client_data[0],
                'full_name': client_data[1],
                'phone': client_data[2],
                'email': client_data[3],
                'registration_date': client_data[4].strftime('%Y-%m-%d'),
                'notes': client_data[5],
                'created_at': client_data[6].strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Ошибка при добавлении клиента: {e}")
        finally:
            cur.close()
    
    def search_clients(self, search_term=None, phone=None, email=None, 
                      date_from=None, date_to=None, limit=100):
        """Поиск клиентов по различным параметрам"""
        try:
            cur = self.connection.cursor()
            
            query_parts = ["SELECT id, full_name, phone, email, registration_date, notes FROM clients WHERE 1=1"]
            params = []
            
            # Поиск по ФИО
            if search_term:
                query_parts.append("AND (full_name ILIKE %s OR phone ILIKE %s OR email ILIKE %s)")
                like_term = f"%{search_term.strip()}%"
                params.extend([like_term, like_term, like_term])
            
            # Поиск по телефону
            if phone:
                query_parts.append("AND phone ILIKE %s")
                params.append(f"%{phone.strip()}%")
            
            # Поиск по email
            if email:
                query_parts.append("AND email ILIKE %s")
                params.append(f"%{email.strip()}%")
            
            # Поиск по дате регистрации
            if date_from:
                if isinstance(date_from, str):
                    date_from = validate_date(date_from)
                query_parts.append("AND registration_date >= %s")
                params.append(date_from)
            
            if date_to:
                if isinstance(date_to, str):
                    date_to = validate_date(date_to)
                query_parts.append("AND registration_date <= %s")
                params.append(date_to)
            
            # Сортировка и ограничение
            query_parts.append("ORDER BY registration_date DESC, full_name ASC")
            query_parts.append("LIMIT %s")
            params.append(limit)
            
            query = " ".join(query_parts)
            cur.execute(query, tuple(params))
            results = cur.fetchall()
            
            clients = []
            for row in results:
                clients.append({
                    'id': row[0],
                    'full_name': row[1],
                    'phone': row[2],
                    'email': row[3],
                    'registration_date': row[4].strftime('%Y-%m-%d'),
                    'notes': row[5]
                })
            
            return clients
            
        except Exception as e:
            raise Exception(f"Ошибка при поиске клиентов: {e}")
        finally:
            cur.close()
    
    def update_client(self, client_id, full_name=None, phone=None, email=None, 
                     registration_date=None, notes=None):
        """Обновление данных клиента"""
        try:
            cur = self.connection.cursor()
            
            # Проверка существования клиента
            cur.execute("SELECT id FROM clients WHERE id = %s", (client_id,))
            if not cur.fetchone():
                raise ValueError(f"Клиент с ID {client_id} не найден")
            
            update_fields = []
            params = []
            
            if full_name is not None:
                if len(full_name.strip()) < 3:
                    raise ValueError("ФИО должно содержать минимум 3 символа")
                update_fields.append("full_name = %s")
                params.append(full_name.strip())
            
            if phone is not None:
                if not validate_phone(phone):
                    raise ValueError("Неверный формат телефонного номера")
                update_fields.append("phone = %s")
                params.append(phone.strip())
            
            if email is not None:
                if not validate_email(email):
                    raise ValueError("Неверный формат email адреса")
                update_fields.append("email = %s")
                params.append(email.strip())
            
            if registration_date is not None:
                if isinstance(registration_date, str):
                    registration_date = validate_date(registration_date)
                update_fields.append("registration_date = %s")
                params.append(registration_date)
            
            if notes is not None:
                update_fields.append("notes = %s")
                params.append(notes)
            
            if not update_fields:
                raise ValueError("Нет данных для обновления")
            
            params.append(client_id)
            query = f"""
            UPDATE clients 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, full_name, phone, email, registration_date, notes, updated_at
            """
            
            cur.execute(query, tuple(params))
            updated_data = cur.fetchone()
            self.connection.commit()
            
            if not updated_data:
                raise ValueError(f"Клиент с ID {client_id} не найден")
            
            return {
                'id': updated_data[0],
                'full_name': updated_data[1],
                'phone': updated_data[2],
                'email': updated_data[3],
                'registration_date': updated_data[4].strftime('%Y-%m-%d'),
                'notes': updated_data[5],
                'updated_at': updated_data[6].strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Ошибка при обновлении клиента: {e}")
        finally:
            cur.close()
    
    def delete_client(self, client_id):
        """Удаление клиента"""
        try:
            cur = self.connection.cursor()
            
            # Сначала проверяем существование клиента
            cur.execute("SELECT full_name FROM clients WHERE id = %s", (client_id,))
            client = cur.fetchone()
            if not client:
                raise ValueError(f"Клиент с ID {client_id} не найден")
            
            # Удаляем клиента
            cur.execute("DELETE FROM clients WHERE id = %s", (client_id,))
            self.connection.commit()
            
            return {
                'success': True,
                'message': f"Клиент '{client[0]}' успешно удален",
                'deleted_client_id': client_id
            }
            
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Ошибка при удалении клиента: {e}")
        finally:
            cur.close()
    
    def get_all_clients(self, limit=1000):
        """Получение всех клиентов"""
        try:
            cur = self.connection.cursor()
            
            cur.execute("""
            SELECT id, full_name, phone, email, registration_date, notes 
            FROM clients 
            ORDER BY registration_date DESC, full_name ASC 
            LIMIT %s
            """, (limit,))
            
            results = cur.fetchall()
            
            clients = []
            for row in results:
                clients.append({
                    'id': row[0],
                    'full_name': row[1],
                    'phone': row[2],
                    'email': row[3],
                    'registration_date': row[4].strftime('%Y-%m-%d'),
                    'notes': row[5]
                })
            
            return clients
            
        except Exception as e:
            raise Exception(f"Ошибка при получении списка клиентов: {e}")
        finally:
            cur.close()
