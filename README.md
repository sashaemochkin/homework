# Отчет по учебной практике  
**Тема:** Разработка программного модуля автоматизации учета клиентов малого бизнеса

**Выполнила:** Талпы Арина Николаевна ИСП-32

**Учитель:** Базяк Галина Владимировна

---

## Этап 1: Разработка алгоритма решения задачи 

### Цель алгоритма
Разработка алгоритма для учета клиентов малого бизнеса, обеспечивающего ввод, хранение, поиск, редактирование и удаление данных о клиентах в соответствии с техническим заданием.

### Краткое описание входных данных
- ФИО клиента (строка)
- Контактная информация (телефон, email, адрес - строка)
- Дата регистрации (дата)
- Примечания (строка, необязательное поле)

### Блок-схема алгоритма учета клиентов

```mermaid
flowchart TB
    strt([Начало]) --> menu[Отображение главного меню]
    menu --> displactionmenu[/Вывод меню действий/]
    displactionmenu --> userchoice[/Ввод выбора пользователя/]
    userchoice --> question1{Данные пользователя имеются в базе данных?}
    question1 --> |Нет| usernoregistr[/Пользователь не зарегистрирован/]
    question1 --> |Да| loginaccount[Вход в учетную запись]
    loginaccount --> loginsystem([Вход в систему])
    usernoregistr --> registr[Блок регистрации]
    registr --> dataentry[/Ввод пользовательских данных/]
    dataentry --> update[Обновление базы данных]
    update --> menu
```

### Пояснения к выбору алгоритма и структур данных

**Выбор алгоритма:**
Для реализации системы учета клиентов выбран модульный подход с использованием меню-ориентированного интерфейса. Такой подход обеспечивает:
- **Структурированность** - каждая операция выделена в отдельный функциональный блок
- **Масштабируемость** - легко добавлять новые функции без изменения основной логики
- **Удобство использования** - интуитивно понятный интерфейс для пользователя
- **Обработку ошибок** - на каждом этапе предусмотрена валидация данных и обработка исключений

**Выбор структур данных:**
1. **Реляционная база данных (PostgreSQL)** - основная структура хранения данных:
   - Таблица `clients` для хранения информации о клиентах
   - Таблица `orders` для хранения информации о заказах
   - Связь один-ко-многим между клиентами и их заказами

2. **Временные структуры в памяти** (для обработки данных):
   - Списки (lists) для хранения результатов поиска и отображения
   - Словари (dictionaries) для представления отдельных записей клиентов/заказов
   - Кортежи (tuples) для передачи параметров между функциями

3. **Структуры для отчетов**:
   - Списки словарей для формирования табличных данных
   - Специализированные объекты для экспорта в Excel/PDF

**Обоснование выбора:**
- **PostgreSQL** выбрана согласно техническому заданию, обеспечивает надежное хранение данных, поддержку транзакций и возможность масштабирования
- **Меню-ориентированный подход** позволяет реализовать все функциональные требования в логической последовательности
- **Модульная архитектура** облегчает тестирование, поддержку и дальнейшее развитие системы
- **Валидация на каждом этапе** ввода данных гарантирует целостность данных в базе

Алгоритм спроектирован с учетом всех функциональных требований технического задания и обеспечивает полный жизненный цикл работы с данными клиентов: от ввода до генерации отчетов.

---

## Этап 2: Инструментальные средства разработки

### Настройка инфраструктуры разработки

**1. Создание Git-репозитория:**
Готовый Git-репозиторий предоставил Физтех-колледж:
>1. Нужно было зарегистрироваться или войти в учетную запись Физтех-колледжа
>2. Ссылка на Git-репозиторий колледжа: [ссылка](https://gitlab.phystech.pro/users/sign_in)
>3. Для входа ввести данные уже зарегистрированной учетной записи колледжа
>4. После успешного входа предоставляется доступ к созданию и загрузке проектов


**2. Создание базовой структуры проекта:**
```
client_management_system/
├── .gitignore
├── requirements.txt
├── config/
│   ├── __init__.py
│   └── database.py
├── modules/
│   ├── __init__.py
│   ├── client_management.py
│   ├── order_management.py
│   ├── reporting.py
│   └── data_import.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_client_management.py
│   └── test_validators.py
├── main.py
└── README.md
```


### Выявленные и исправленные ошибки

**1. Проблема с подключением к PostgreSQL:**
- **Ошибка:** Не удалось подключиться к базе данных из-за неверных учетных данных
- **Решение:** Создан файл `.env` для хранения конфиденциальных данных и добавлена проверка подключения
```python
# config/database.py
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'client_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        raise
```

**2. Проблема с валидацией email:**
- **Ошибка:** Некорректная валидация email-адресов
- **Решение:** Реализована правильная валидация с использованием регулярных выражений
```python
# utils/validators.py
import re
from datetime import datetime

def validate_email(email):
    """Валидация email-адреса"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

def validate_phone(phone):
    """Валидация телефонного номера"""
    # Убираем все символы кроме цифр
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 10 and len(digits) <= 15
```

**3. Проблема с обработкой дат:**
- **Ошибка:** Некорректный формат даты при вводе
- **Решение:** Добавлена гибкая обработка различных форматов дат
```python
def validate_date(date_str):
    """Валидация и преобразование даты"""
    formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError("Неверный формат даты. Используйте ГГГГ-ММ-ДД, ДД.ММ.ГГГГ или ДД/ММ/ГГГГ")
```

### Интеграция с IDE (PyCharm)

**Настройка отладочных точек:**
1. Установка breakpoint в функции `add_client` для отслеживания процесса добавления клиента
2. Настройка watch-выражений для переменных `client_data` и `validation_result`
3. Конфигурация запуска с переменными окружения

**Отладка функции добавления клиента:**
```python
# modules/client_management.py
def add_client(full_name, phone, email, registration_date, notes=None):
    """
    Добавление нового клиента в базу данных
    
    Args:
        full_name (str): Полное имя клиента
        phone (str): Телефонный номер
        email (str): Email адрес
        registration_date (str or date): Дата регистрации
        notes (str, optional): Примечания
        
    Returns:
        dict: Информация о добавленном клиенте
        
    Raises:
        ValueError: При невалидных данных
    """
    # breakpoint()  # Отладочная точка для PyCharm
    
    # Валидация данных
    if not full_name or len(full_name.strip()) < 3:
        raise ValueError("ФИО должно содержать минимум 3 символа")
    
    if not validate_phone(phone):
        raise ValueError("Неверный формат телефонного номера")
    
    if not validate_email(email):
        raise ValueError("Неверный формат email адреса")
    
    if isinstance(registration_date, str):
        registration_date = validate_date(registration_date)
    
    # Подключение к базе данных
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # SQL запрос для добавления клиента
        query = """
        INSERT INTO clients (full_name, phone, email, registration_date, notes)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, full_name, phone, email, registration_date, notes, created_at
        """
        
        cur.execute(query, (full_name.strip(), phone.strip(), 
                           email.strip(), registration_date, notes))
        client_data = cur.fetchone()
        conn.commit()
        
        # Формирование результата
        result = {
            'id': client_data[0],
            'full_name': client_data[1],
            'phone': client_data[2],
            'email': client_data[3],
            'registration_date': client_data[4].strftime('%Y-%m-%d'),
            'notes': client_data[5],
            'created_at': client_data[6].strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return result
        
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
```

**Ключевые настройки PyCharm:**
- **Code Style:** Настроен согласно PEP8
- **Auto-save:** Включен для автоматического сохранения изменений
- **Version Control:** Интеграция с Git для отслеживания изменений
- **Database Tools:** Подключение к PostgreSQL для прямого доступа к данным
- **Test Runner:** Интеграция с pytest для запуска тестов

На данном этапе успешно настроена вся инфраструктура разработки, включая систему контроля версий, виртуальное окружение, базовую структуру проекта и инструменты отладки. Проект готов к дальнейшей разработке функциональных модулей.

---

## Этап 3: Разработка кода программного модуля управления данными клиентов 

### Реализация модуля управления клиентами

**1. Создание базы данных и таблиц:**
```python
# config/database.py
def init_database():
    """Инициализация базы данных и создание таблиц"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # Создание таблицы clients
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            phone VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL,
            registration_date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Создание индексов для ускорения поиска
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_full_name ON clients(full_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_phone ON clients(phone)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_registration_date ON clients(registration_date)")
        
        # Создание триггера для обновления updated_at
        cur.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """)
        
        cur.execute("""
        DROP TRIGGER IF EXISTS update_clients_updated_at ON clients;
        CREATE TRIGGER update_clients_updated_at
        BEFORE UPDATE ON clients
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)
        
        conn.commit()
        print("База данных успешно инициализирована")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при инициализации базы данных: {e}")
        raise
    finally:
        cur.close()
        conn.close()
```

**2. Реализация CRUD операций для клиентов:**
```python
# modules/client_management.py
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
```

**3. Создание основного интерфейса:**
```python
# main.py
import sys
from modules.client_management import ClientManager
from utils.validators import validate_date, validate_email, validate_phone
from datetime import datetime

def main_menu():
    """Основное меню программы"""
    print("\n" + "="*60)
    print("СИСТЕМА УЧЕТА КЛИЕНТОВ МАЛОГО БИЗНЕСА")
    print("="*60)
    print("1. Добавить клиента")
    print("2. Поиск клиентов")
    print("3. Редактировать клиента")
    print("4. Удалить клиента")
    print("5. Просмотреть всех клиентов")
    print("6. Сгенерировать отчет")
    print("7. Управление заказами")
    print("8. Выход")
    print("-"*60)
    
    try:
        choice = int(input("Выберите операцию (1-8): "))
        if choice < 1 or choice > 8:
            raise ValueError
        return choice
    except ValueError:
        print("Неверный выбор. Пожалуйста, введите число от 1 до 8.")
        return None

def add_client_interface(manager):
    """Интерфейс добавления клиента"""
    print("\n" + "-"*60)
    print("ДОБАВЛЕНИЕ НОВОГО КЛИЕНТА")
    print("-"*60)
    
    try:
        full_name = input("ФИО клиента: ").strip()
        while len(full_name) < 3:
            print(" ФИО должно содержать минимум 3 символа")
            full_name = input("ФИО клиента: ").strip()
        
        phone = input("Телефон: ").strip()
        while not validate_phone(phone):
            print(" Неверный формат телефона. Пример: +7(999)123-45-67")
            phone = input("Телефон: ").strip()
        
        email = input("Email: ").strip()
        while not validate_email(email):
            print("Неверный формат email. Пример: client@example.com")
            email = input("Email: ").strip()
        
        date_input = input("Дата регистрации (ДД.ММ.ГГГГ): ").strip()
        registration_date = None
        while registration_date is None:
            try:
                registration_date = validate_date(date_input)
            except ValueError as e:
                print(f"Ошибка {e}")
                date_input = input("Дата регистрации (ДД.ММ.ГГГГ): ").strip()
        
        notes = input("Примечания (опционально): ").strip()
        if notes == "":
            notes = None
        
        # Добавление клиента
        result = manager.add_client(full_name, phone, email, registration_date, notes)
        
        print("\n" + "="*60)
        print(" КЛИЕНТ УСПЕШНО ДОБАВЛЕН")
        print("="*60)
        print(f"ID: {result['id']}")
        print(f"ФИО: {result['full_name']}")
        print(f"Телефон: {result['phone']}")
        print(f"Email: {result['email']}")
        print(f"Дата регистрации: {result['registration_date']}")
        print(f"Дата создания: {result['created_at']}")
        if result['notes']:
            print(f"Примечания: {result['notes']}")
        print("-"*60)
        
    except Exception as e:
        print(f"\n ОШИБКА: {str(e)}")

def search_clients_interface(manager):
    """Интерфейс поиска клиентов"""
    print("\n" + "-"*60)
    print("ПОИСК КЛИЕНТОВ")
    print("-"*60)
    print("1. Поиск по ФИО/телефону/email")
    print("2. Поиск по дате регистрации")
    print("3. Поиск по телефону")
    print("4. Поиск по email")
    print("5. Отмена")
    print("-"*60)
    
    try:
        choice = int(input("Выберите тип поиска (1-5): "))
        if choice < 1 or choice > 5:
            raise ValueError
        
        if choice == 5:
            return
        
        search_params = {}
        
        if choice == 1:
            search_term = input("Введите строку для поиска: ").strip()
            if search_term:
                search_params['search_term'] = search_term
        
        elif choice == 2:
            date_from = input("Дата от (ДД.ММ.ГГГГ, опционально): ").strip()
            date_to = input("Дата до (ДД.ММ.ГГГГ, опционально): ").strip()
            
            if date_from:
                try:
                    search_params['date_from'] = validate_date(date_from)
                except ValueError as e:
                    print(f"Ошибка {e}")
                    return
            
            if date_to:
                try:
                    search_params['date_to'] = validate_date(date_to)
                except ValueError as e:
                    print(f"Ошибка {e}")
                    return
        
        elif choice == 3:
            phone = input("Введите телефон для поиска: ").strip()
            if phone:
                search_params['phone'] = phone
        
        elif choice == 4:
            email = input("Введите email для поиска: ").strip()
            if email:
                search_params['email'] = email
        
        # Выполнение поиска
        results = manager.search_clients(**search_params)
        
        if not results:
            print("\n Клиенты не найдены")
            return
        
        print("\n" + "="*80)
        print(f"НАЙДЕНО КЛИЕНТОВ: {len(results)}")
        print("="*80)
        
        for i, client in enumerate(results, 1):
            print(f"\nКЛИЕНТ #{i}")
            print("-"*40)
            print(f"ID: {client['id']}")
            print(f"ФИО: {client['full_name']}")
            print(f"Телефон: {client['phone']}")
            print(f"Email: {client['email']}")
            print(f"Дата регистрации: {client['registration_date']}")
            if client['notes']:
                print(f"Примечания: {client['notes']}")
        
        print("="*80)
        
    except ValueError:
        print(" Неверный выбор. Пожалуйста, введите число от 1 до 5.")
    except Exception as e:
        print(f"\n ОШИБКА: {str(e)}")

def main():
    """Основная функция программы"""
    print("Инициализация системы...")
    
    try:
        # Инициализация базы данных
        from config.database import init_database
        init_database()
        
        with ClientManager() as manager:
            while True:
                choice = main_menu()
                
                if choice is None:
                    continue
                
                if choice == 8:
                    print("\n" + "="*60)
                    print("ЗАВЕРШЕНИЕ РАБОТЫ СИСТЕМЫ")
                    print("="*60)
                    print("Спасибо за использование системы учета клиентов!")
                    print("-"*60)
                    break
                
                elif choice == 1:
                    add_client_interface(manager)
                
                elif choice == 2:
                    search_clients_interface(manager)
                
                elif choice == 5:
                    # Просмотреть всех клиентов
                    try:
                        clients = manager.get_all_clients()
                        
                        if not clients:
                            print("\n В базе данных нет клиентов")
                            continue
                        
                        print("\n" + "="*80)
                        print(f"ВСЕ КЛИЕНТЫ ({len(clients)}):")
                        print("="*80)
                        
                        for i, client in enumerate(clients, 1):
                            print(f"\nКЛИЕНТ #{i}")
                            print("-"*40)
                            print(f"ID: {client['id']}")
                            print(f"ФИО: {client['full_name']}")
                            print(f"Телефон: {client['phone']}")
                            print(f"Email: {client['email']}")
                            print(f"Дата регистрации: {client['registration_date']}")
                            if client['notes']:
                                print(f"Примечания: {client['notes']}")
                        
                        print("="*80)
                        
                    except Exception as e:
                        print(f"\n ОШИБКА: {str(e)}")
                
                input("\nНажмите Enter для продолжения...")
        
    except Exception as e:
        print(f" ОШИБКА: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Структура программы

**Основные модули и функции:**

1. **config/database.py**
   - `get_db_connection()` - подключение к базе данных
   - `init_database()` - инициализация базы данных и создание таблиц
   - `close_connection()` - закрытие соединения

2. **modules/client_management.py**
   - `ClientManager` - основной класс для управления клиентами
   - `add_client()` - добавление нового клиента
   - `search_clients()` - поиск клиентов по различным параметрам
   - `update_client()` - обновление данных клиента
   - `delete_client()` - удаление клиента
   - `get_all_clients()` - получение всех клиентов

3. **utils/validators.py**
   - `validate_email()` - валидация email-адреса
   - `validate_phone()` - валидация телефонного номера
   - `validate_date()` - валидация и преобразование даты

4. **main.py**
   - `main_menu()` - отображение основного меню
   - `add_client_interface()` - интерфейс добавления клиента
   - `search_clients_interface()` - интерфейс поиска клиентов
   - `main()` - основная функция программы

### Ключевый код с комментариями

**Фрагмент кода с реализацией поиска клиентов:**
```python
def search_clients(self, search_term=None, phone=None, email=None, 
                  date_from=None, date_to=None, limit=100):
    """
    Поиск клиентов по различным параметрам с поддержкой множественных критериев
    
    Args:
        search_term (str, optional): Поиск по ФИО, телефону или email
        phone (str, optional): Поиск по телефону
        email (str, optional): Поиск по email
        date_from (str or date, optional): Начальная дата регистрации
        date_to (str or date, optional): Конечная дата регистрации
        limit (int, optional): Максимальное количество результатов
        
    Returns:
        list: Список найденных клиентов в формате словарей
        
    Raises:
        Exception: При ошибке выполнения SQL запроса
    """
    try:
        cur = self.connection.cursor()
        
        # Начало SQL запроса с базовым SELECT
        query_parts = ["SELECT id, full_name, phone, email, registration_date, notes FROM clients WHERE 1=1"]
        params = []
        
        # Динамическое добавление условий поиска
        if search_term:
            # Поиск по нескольким полям одновременно с использованием ILIKE для регистронезависимого поиска
            query_parts.append("AND (full_name ILIKE %s OR phone ILIKE %s OR email ILIKE %s)")
            like_term = f"%{search_term.strip()}%"
            params.extend([like_term, like_term, like_term])
        
        if phone:
            query_parts.append("AND phone ILIKE %s")
            params.append(f"%{phone.strip()}%")
        
        if email:
            query_parts.append("AND email ILIKE %s")
            params.append(f"%{email.strip()}%")
        
        # Поиск по диапазону дат
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
        
        # Сортировка результатов: сначала по дате регистрации (новые первыми), затем по ФИО
        query_parts.append("ORDER BY registration_date DESC, full_name ASC")
        query_parts.append("LIMIT %s")
        params.append(limit)
        
        # Формирование итогового SQL запроса
        query = " ".join(query_parts)
        cur.execute(query, tuple(params))
        results = cur.fetchall()
        
        # Преобразование результатов в удобный формат
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
```

**Ключевые особенности реализации:**
- **Динамическое формирование SQL запросов** - позволяет гибко комбинировать различные критерии поиска
- **Регистронезависимый поиск** - использование ILIKE для поиска без учета регистра
- **Валидация данных** - все входные данные проходят строгую валидацию перед использованием
- **Обработка ошибок** - полная обработка исключений с откатом транзакций при ошибках
- **Индексация** - создание индексов для ускорения поиска по часто используемым полям
- **Триггеры** - автоматическое обновление поля updated_at при изменении данных

Модуль управления клиентами полностью реализован и готов к тестированию. Следующим этапом будет разработка модуля управления заказами клиентов.
