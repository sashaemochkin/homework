import sys
import os
import logging
from datetime import datetime, date
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('client_management.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.client_service import ClientService
from src.services.order_service import OrderService
from src.services.import_service import ImportService
from src.services.report_service import ReportService
from src.services.metabase_service import MetabaseService
from src.validators.client_validators import ClientValidator
from src.validators.order_validators import OrderValidator

class ClientManagementSystem:
    """Главный класс системы управления клиентами и заказами"""
    
    def __init__(self):
        self.client_service = ClientService()
        self.order_service = OrderService()
        self.import_service = ImportService(self.client_service, self.order_service)
        self.report_service = ReportService(self.client_service, self.order_service)
        self.client_validator = ClientValidator()
        self.order_validator = OrderValidator()
        
        # Инициализация Metabase (опционально)
        self.metabase_service = None
        self._init_metabase()
        
        self.logger = logging.getLogger(__name__)
    
    def _init_metabase(self):
        """Инициализация подключения к Metabase"""
        try:
            # Конфигурация из переменных окружения или конфиг файла
            metabase_url = os.getenv('METABASE_URL', 'http://localhost:3000')
            username = os.getenv('METABASE_USERNAME', 'admin@example.com')
            password = os.getenv('METABASE_PASSWORD', 'password')
            
            if metabase_url and username and password:
                self.metabase_service = MetabaseService(metabase_url, username, password)
                print("✅ Metabase подключен")
            else:
                print("⚠️  Metabase не настроен (проверьте переменные окружения)")
        except Exception as e:
            print(f"⚠️  Metabase не доступен: {e}")
    
    def display_main_menu(self):
        """Главное меню системы"""
        print("\n" + "="*60)
        print("🎯 СИСТЕМА УПРАВЛЕНИЯ КЛИЕНТАМИ И ЗАКАЗАМИ")
        print("="*60)
        print("1. 📋 Управление клиентами")
        print("2. 📦 Управление заказами")
        print("3. 📊 Отчеты и аналитика")
        print("4. 📥 Импорт данных")
        print("5. 📤 Экспорт данных")
        print("6. 📈 Metabase аналитика")
        print("7. 🧪 Тестирование системы")
        print("0. 🚪 Выход")
        print("="*60)
    
    def display_clients_menu(self):
        """Меню управления клиентами"""
        print("\n--- 📋 УПРАВЛЕНИЕ КЛИЕНТАМИ ---")
        print("1. 👤 Добавить клиента")
        print("2. 🔍 Поиск клиентов")
        print("3. ✏️  Редактировать клиента")
        print("4. 🗑️  Удалить клиента")
        print("5. 📊 Статистика клиентов")
        print("0. ↩️  Назад")
    
    def display_orders_menu(self):
        """Меню управления заказами"""
        print("\n--- 📦 УПРАВЛЕНИЕ ЗАКАЗАМИ ---")
        print("1. 🆕 Создать заказ")
        print("2. 🔍 Поиск заказов")
        print("3. 👀 Заказы клиента")
        print("4. 🔄 Обновить статус заказа")
        print("5. 👁️  Просмотр заказа")
        print("6. 🗑️  Удалить заказ")
        print("7. 📈 Статистика заказов")
        print("0. ↩️  Назад")
    
    def display_reports_menu(self):
        """Меню отчетов и аналитики"""
        print("\n--- 📊 ОТЧЕТЫ И АНАЛИТИКА ---")
        print("1. 📈 Общая статистика")
        print("2. 👥 Отчет по клиентам")
        print("3. 📦 Отчет по заказам")
        print("4. 📅 Отчет за период")
        print("0. ↩️  Назад")
    
    def display_import_menu(self):
        """Меню импорта данных"""
        print("\n--- 📥 ИМПОРТ ДАННЫХ ---")
        print("1. 👥 Импорт клиентов из Excel")
        print("2. 📦 Импорт заказов из Excel")
        print("3. 📋 Создать шаблон импорта")
        print("0. ↩️  Назад")
    
    def display_export_menu(self):
        """Меню экспорта данных"""
        print("\n--- 📤 ЭКСПОРТ ДАННЫХ ---")
        print("1. 👥 Экспорт клиентов в Excel")
        print("2. 📦 Экспорт заказов в Excel")
        print("3. 📊 Комплексный отчет")
        print("0. ↩️  Назад")
    
    def display_metabase_menu(self):
        """Меню Metabase аналитики"""
        print("\n--- 📈 METABASE АНАЛИТИКА ---")
        print("1. 🎯 Настроить дашборд")
        print("2. 🔗 Получить ссылку на дашборд")
        print("3. 📊 Просмотреть статистику")
        print("0. ↩️  Назад")
    
    def display_testing_menu(self):
        """Меню тестирования системы"""
        print("\n--- 🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ ---")
        print("1. ✅ Функциональное тестирование")
        print("2. 🔧 Модульное тестирование")
        print("3. 📊 Тест производительности")
        print("4. 🐛 Тест обработки ошибок")
        print("0. ↩️  Назад")

    # ==================== МЕТОДЫ ДЛЯ КЛИЕНТОВ ====================

    def run_clients_management(self):
        """Запуск меню управления клиентами"""
        while True:
            self.display_clients_menu()
            choice = input("\n🎯 Выберите действие: ").strip()
            
            if choice == '1':
                self.add_client_interactive()
            elif choice == '2':
                self.search_clients_interactive()
            elif choice == '3':
                self.edit_client_interactive()
            elif choice == '4':
                self.delete_client_interactive()
            elif choice == '5':
                self.show_client_statistics()
            elif choice == '0':
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
            input("\n⏎ Нажмите Enter для продолжения...")

    def add_client_interactive(self):
        """Интерактивное добавление клиента"""
        print("\n" + "="*50)
        print("👤 ДОБАВЛЕНИЕ НОВОГО КЛИЕНТА")
        print("="*50)
        
        client_data = {}
        client_data['first_name'] = input("Имя: ").strip()
        client_data['last_name'] = input("Фамилия: ").strip()
        client_data['patronymic'] = input("Отчество (необязательно): ").strip() or None
        client_data['email'] = input("Email (необязательно): ").strip() or None
        client_data['phone'] = input("Телефон (+7XXXXXXXXXX): ").strip() or None
        client_data['city'] = input("Город: ").strip() or None
        client_data['notes'] = input("Примечания (необязательно): ").strip() or None
        
        # Валидация данных
        is_valid, errors = self.client_validator.validate_client_data(client_data)
        if not is_valid:
            print("❌ Ошибки при вводе данных:")
            for error in errors:
                print(f"   - {error}")
            return
        
        # Создание клиента
        result = self.client_service.add_client(client_data)
        
        if result['success']:
            print(f"✅ Клиент успешно добавлен! ID: {result['client']['id']}")
            self.logger.info(f"Добавлен новый клиент: {client_data['first_name']} {client_data['last_name']}")
        else:
            print("❌ Ошибки при добавлении клиента:")
            for error in result['errors']:
                print(f"   - {error}")

    def search_clients_interactive(self):
        """Интерактивный поиск клиентов"""
        print("\n" + "="*50)
        print("🔍 ПОИСК КЛИЕНТОВ")
        print("="*50)
        
        print("Введите параметры поиска (оставьте пустым для пропуска):")
        search_params = {}
        
        fields = [
            ('first_name', 'Имя'),
            ('last_name', 'Фамилия'),
            ('patronymic', 'Отчество'),
            ('email', 'Email'),
            ('phone', 'Телефон'),
            ('city', 'Город'),
            ('status', 'Статус (active/inactive)')
        ]
        
        for field, label in fields:
            value = input(f"{label}: ").strip()
            if value:
                search_params[field] = value
        
        clients = self.client_service.search_clients(search_params)
        
        print(f"\n📊 Найдено клиентов: {len(clients)}")
        
        if clients:
            print("\n" + "-" * 80)
            print(f"{'ID':<5} {'ФИО':<30} {'Email':<20} {'Телефон':<15} {'Город':<15}")
            print("-" * 80)
            
            for client in clients:
                full_name = f"{client['last_name']} {client['first_name']}"
                if client['patronymic']:
                    full_name += f" {client['patronymic']}"
                
                if len(full_name) > 28:
                    full_name = full_name[:25] + "..."
                
                email = client['email'] or '-'
                phone = client['phone'] or '-'
                city = client['city'] or '-'
                
                print(f"{client['id']:<5} {full_name:<30} {email:<20} {phone:<15} {city:<15}")
        
        input("\n⏎ Нажмите Enter для продолжения...")

    def edit_client_interactive(self):
        """Редактирование клиента"""
        print("\n" + "="*50)
        print("✏️  РЕДАКТИРОВАНИЕ КЛИЕНТА")
        print("="*50)
        
        try:
            client_id = int(input("ID клиента для редактирования: "))
            
            # Получаем текущие данные клиента
            client = self.client_service.get_client(client_id)
            if not client:
                print("❌ Клиент не найден")
                return
            
            print(f"\n📋 Текущие данные клиента: {client['first_name']} {client['last_name']}")
            print("Введите новые значения (оставьте пустым для сохранения текущего):")
            
            updates = {}
            fields = [
                ('first_name', 'Имя', client['first_name']),
                ('last_name', 'Фамилия', client['last_name']),
                ('patronymic', 'Отчество', client.get('patronymic', '')),
                ('email', 'Email', client.get('email', '')),
                ('phone', 'Телефон', client.get('phone', '')),
                ('city', 'Город', client.get('city', '')),
                ('notes', 'Примечания', client.get('notes', '')),
                ('status', 'Статус', client['status'])
            ]
            
            for field, label, current_value in fields:
                new_value = input(f"{label} [{current_value}]: ").strip()
                if new_value:
                    updates[field] = new_value
                elif new_value == "" and field in ['patronymic', 'email', 'phone', 'city', 'notes']:
                    updates[field] = None
            
            if updates:
                result = self.client_service.update_client(client_id, updates)
                if result['success']:
                    print("✅ Данные клиента успешно обновлены")
                    self.logger.info(f"Обновлен клиент ID {client_id}")
                else:
                    print("❌ Ошибки при обновлении:")
                    for error in result['errors']:
                        print(f"   - {error}")
            else:
                print("ℹ️  Данные не изменены")
                
        except ValueError:
            print("❌ Неверный формат ID клиента")

    def delete_client_interactive(self):
        """Удаление клиента"""
        print("\n" + "="*50)
        print("🗑️  УДАЛЕНИЕ КЛИЕНТА")
        print("="*50)
        
        try:
            client_id = int(input("ID клиента для удаления: "))
            
            # Получаем информацию о клиенте
            client = self.client_service.get_client(client_id)
            if not client:
                print("❌ Клиент не найден")
                return
            
            print(f"Клиент: {client['first_name']} {client['last_name']}")
            print(f"Email: {client.get('email', 'не указан')}")
            print(f"Заказов: {client['total_orders']}")
            print(f"Выручка: {client['total_revenue']} руб.")
            
            confirm = input("\n❓ Вы уверены, что хотите удалить клиента? (y/n): ").lower()
            if confirm != 'y':
                print("Удаление отменено")
                return
            
            result = self.client_service.delete_client(client_id)
            if result['success']:
                print("✅ Клиент успешно удален")
                self.logger.info(f"Удален клиент ID {client_id}")
            else:
                print("❌ Ошибка при удалении клиента:")
                for error in result['errors']:
                    print(f"   - {error}")
                    
        except ValueError:
            print("❌ Неверный формат ID клиента")

    def show_client_statistics(self):
        """Показать статистику клиентов"""
        print("\n" + "="*50)
        print("📊 СТАТИСТИКА КЛИЕНТОВ")
        print("="*50)
        
        stats = self.client_service.get_client_statistics()
        
        print(f"👥 Всего клиентов: {stats['total_clients']}")
        print(f"✅ Активных клиентов: {stats['active_clients']}")
        print(f"💰 Общая выручка: {stats['total_revenue']:.2f} руб.")
        print(f"📦 Всего заказов: {stats['total_orders']}")
        print(f"📊 Средняя выручка на клиента: {stats['total_revenue'] / stats['total_clients']:.2f} руб.")
        
        if stats['city_stats']:
            print("\n🏙️  Распределение по городам:")
            for city_stat in sorted(stats['city_stats'], key=lambda x: x['count'], reverse=True)[:10]:
                print(f"   {city_stat['city']}: {city_stat['count']} клиентов, {city_stat['revenue']:.2f} руб.")

    # ==================== МЕТОДЫ ДЛЯ ЗАКАЗОВ ====================

    def run_orders_management(self):
        """Запуск меню управления заказами"""
        while True:
            self.display_orders_menu()
            choice = input("\n🎯 Выберите действие: ").strip()
            
            if choice == '1':
                self.create_order_interactive()
            elif choice == '2':
                self.search_orders_interactive()
            elif choice == '3':
                self.view_client_orders_interactive()
            elif choice == '4':
                self.update_order_status_interactive()
            elif choice == '5':
                self.view_order_interactive()
            elif choice == '6':
                self.delete_order_interactive()
            elif choice == '7':
                self.show_order_statistics()
            elif choice == '0':
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
            input("\n⏎ Нажмите Enter для продолжения...")

    def create_order_interactive(self):
        """Интерактивное создание заказа"""
        print("\n" + "="*50)
        print("🆕 СОЗДАНИЕ НОВОГО ЗАКАЗА")
        print("="*50)
        
        try:
            # Получаем ID клиента
            client_id = int(input("ID клиента: "))
            
            # Проверяем существование клиента
            client = self.client_service.get_client(client_id)
            if not client:
                print("❌ Клиент не найден")
                return
            
            print(f"👤 Клиент: {client['first_name']} {client['last_name']}")
            print(f"📧 Email: {client.get('email', 'не указан')}")
            print(f"📞 Телефон: {client.get('phone', 'не указан')}")
            print("-" * 40)
            
            # Ввод данных заказа
            order_data = {}
            order_data['client_id'] = client_id
            
            # Сумма заказа
            while True:
                try:
                    total_amount = float(input("💰 Сумма заказа: "))
                    if total_amount <= 0:
                        print("❌ Сумма должна быть положительной")
                        continue
                    order_data['total_amount'] = total_amount
                    break
                except ValueError:
                    print("❌ Введите корректную сумму")
            
            # Статус заказа
            print("\n📋 Статус заказа:")
            print("  1 - pending (в обработке)")
            print("  2 - completed (выполнен)")
            print("  3 - cancelled (отменен)")
            
            status_choice = input("Выберите статус (1-3, по умолчанию 1): ").strip()
            status_map = {'1': 'pending', '2': 'completed', '3': 'cancelled'}
            order_data['status'] = status_map.get(status_choice, 'pending')
            
            # Дата заказа
            date_str = input("📅 Дата заказа (ГГГГ-ММ-ДД, по умолчанию - сегодня): ").strip()
            if date_str:
                try:
                    order_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    order_data['order_date'] = order_date
                except ValueError:
                    print("❌ Неверный формат даты, используется сегодняшняя дата")
                    order_data['order_date'] = date.today()
            else:
                order_data['order_date'] = date.today()
            
            # Описание
            description = input("📝 Описание заказа (необязательно): ").strip()
            if description:
                order_data['description'] = description
            
            # Создание заказа
            result = self.order_service.create_order(order_data)
            
            if result['success']:
                order = result['order']
                print(f"\n✅ Заказ успешно создан!")
                print(f"📦 Номер заказа: {order['order_number']}")
                print(f"💰 Сумма: {order['total_amount']:.2f} руб.")
                print(f"📋 Статус: {order['status']}")
                print(f"📅 Дата: {order['order_date']}")
                self.logger.info(f"Создан заказ {order['order_number']} для клиента {client_id}")
            else:
                print("❌ Ошибки при создании заказа:")
                for error in result['errors']:
                    print(f"   - {error}")
                    
        except ValueError:
            print("❌ Неверный формат данных")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def search_orders_interactive(self):
        """Интерактивный поиск заказов"""
        print("\n" + "="*50)
        print("🔍 ПОИСК ЗАКАЗОВ")
        print("="*50)
        
        search_params = {}
        
        print("Введите параметры поиска (оставьте пустым для пропуска):")
        
        # Основные параметры
        client_id_str = input("👤 ID клиента: ").strip()
        if client_id_str:
            try:
                search_params['client_id'] = int(client_id_str)
            except ValueError:
                print("❌ Неверный формат ID клиента")
                return
        
        order_number = input("📦 Номер заказа: ").strip()
        if order_number:
            search_params['order_number'] = order_number
        
        client_name = input("👥 Имя клиента: ").strip()
        if client_name:
            search_params['client_name'] = client_name
        
        # Статус
        print("\n📋 Статусы: pending, completed, cancelled")
        status = input("Статус заказа: ").strip()
        if status:
            search_params['status'] = status
        
        # Суммы
        min_amount_str = input("💰 Минимальная сумма: ").strip()
        if min_amount_str:
            try:
                search_params['min_amount'] = float(min_amount_str)
            except ValueError:
                print("❌ Неверный формат суммы")
                return
        
        max_amount_str = input("💰 Максимальная сумма: ").strip()
        if max_amount_str:
            try:
                search_params['max_amount'] = float(max_amount_str)
            except ValueError:
                print("❌ Неверный формат суммы")
                return
        
        # Даты
        start_date_str = input("📅 Дата начала (ГГГГ-ММ-ДД): ").strip()
        if start_date_str:
            try:
                search_params['start_date'] = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                print("❌ Неверный формат даты")
                return
        
        end_date_str = input("📅 Дата окончания (ГГГГ-ММ-ДД): ").strip()
        if end_date_str:
            try:
                search_params['end_date'] = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                print("❌ Неверный формат даты")
                return
        
        # Пагинация
        per_page_str = input("📄 Записей на странице (по умолчанию 50): ").strip()
        if per_page_str:
            try:
                search_params['per_page'] = int(per_page_str)
            except ValueError:
                print("❌ Неверный формат числа")
                return
        
        # Выполняем поиск
        result = self.order_service.search_orders(search_params)
        
        if result['success']:
            orders = result['orders']
            total_count = result['total_count']
            page = result.get('page', 1)
            total_pages = result.get('total_pages', 1)
            
            print(f"\n📊 Найдено заказов: {total_count}")
            print(f"📄 Страница: {page} из {total_pages}")
            
            if orders:
                print("\n" + "="*100)
                print(f"{'ID':<5} {'Номер':<15} {'Клиент':<25} {'Дата':<12} {'Статус':<12} {'Сумма':<10}")
                print("="*100)
                
                for order in orders:
                    status_display = {
                        'pending': '🟡 Обработка',
                        'completed': '🟢 Выполнен',
                        'cancelled': '🔴 Отменен'
                    }.get(order['status'], order['status'])
                    
                    client_name = order.get('client_name', 'Неизвестно')
                    if len(client_name) > 23:
                        client_name = client_name[:20] + "..."
                    
                    print(f"{order['id']:<5} {order['order_number']:<15} {client_name:<25} "
                          f"{order['order_date']:<12} {status_display:<12} {order['total_amount']:<10.2f}")
            else:
                print("❌ Заказы не найдены")
        else:
            print("❌ Ошибки при поиске:")
            for error in result['errors']:
                print(f"   - {error}")

    def view_client_orders_interactive(self):
        """Просмотр заказов клиента"""
        print("\n" + "="*50)
        print("👀 ЗАКАЗЫ КЛИЕНТА")
        print("="*50)
        
        try:
            client_id = int(input("👤 ID клиента: "))
            
            # Проверяем существование клиента
            client = self.client_service.get_client(client_id)
            if not client:
                print("❌ Клиент не найден")
                return
            
            print(f"\n👤 Клиент: {client['first_name']} {client['last_name']}")
            print(f"📧 Email: {client.get('email', 'не указан')}")
            print(f"📞 Телефон: {client.get('phone', 'не указан')}")
            print("=" * 60)
            
            orders = self.order_service.get_client_orders(client_id)
            
            if orders:
                print(f"📦 Всего заказов: {len(orders)}")
                total_revenue = sum(order['total_amount'] for order in orders)
                print(f"💰 Общая выручка: {total_revenue:.2f} руб.")
                print()
                
                for order in orders:
                    status_display = {
                        'pending': '🟡 В обработке',
                        'completed': '🟢 Выполнен',
                        'cancelled': '🔴 Отменен'
                    }.get(order['status'], order['status'])
                    
                    print(f"📦 {order['order_number']}")
                    print(f"   📅 Дата: {order['order_date']}")
                    print(f"   📋 Статус: {status_display}")
                    print(f"   💰 Сумма: {order['total_amount']:.2f} руб.")
                    if order['description']:
                        print(f"   📝 Описание: {order['description']}")
                    print()
            else:
                print("❌ У клиента нет заказов")
                
        except ValueError:
            print("❌ Неверный формат ID клиента")

    def update_order_status_interactive(self):
        """Обновление статуса заказа"""
        print("\n" + "="*50)
        print("🔄 ОБНОВЛЕНИЕ СТАТУСА ЗАКАЗА")
        print("="*50)
        
        try:
            order_id = int(input("📦 ID заказа: "))
            
            # Получаем информацию о заказе
            order_result = self.order_service.get_order(order_id)
            if not order_result['success']:
                print("❌ Заказ не найден")
                return
            
            order = order_result['order']
            print(f"📦 Заказ: #{order['order_number']}")
            print(f"👤 Клиент ID: {order['client_id']}")
            print(f"💰 Сумма: {order['total_amount']:.2f} руб.")
            print(f"📅 Дата: {order['order_date']}")
            print(f"📋 Текущий статус: {order['status']}")
            
            print("\n🔄 Доступные статусы:")
            print("  1 - pending (в обработке)")
            print("  2 - completed (выполнен)") 
            print("  3 - cancelled (отменен)")
            
            status_choice = input("Выберите новый статус (1-3): ").strip()
            status_map = {'1': 'pending', '2': 'completed', '3': 'cancelled'}
            
            if status_choice not in status_map:
                print("❌ Неверный выбор статуса")
                return
            
            new_status = status_map[status_choice]
            
            result = self.order_service.update_order_status(order_id, new_status)
            
            if result['success']:
                print(f"✅ Статус заказа успешно обновлен на: {new_status}")
                self.logger.info(f"Обновлен статус заказа {order_id} на {new_status}")
            else:
                print("❌ Ошибки при обновлении статуса:")
                for error in result['errors']:
                    print(f"   - {error}")
                    
        except ValueError:
            print("❌ Неверный формат ID заказа")

    def view_order_interactive(self):
        """Просмотр детальной информации о заказе"""
        print("\n" + "="*50)
        print("👁️  ПРОСМОТР ЗАКАЗА")
        print("="*50)
        
        try:
            order_id = int(input("📦 ID заказа: "))
            
            result = self.order_service.get_order(order_id)
            if not result['success']:
                print("❌ Заказ не найден")
                return
            
            order = result['order']
            
            print(f"\n📦 ЗАКАЗ #{order['order_number']}")
            print("=" * 50)
            print(f"🆔 ID: {order['id']}")
            print(f"👤 Клиент ID: {order['client_id']}")
            print(f"📅 Дата заказа: {order['order_date']}")
            
            status_display = {
                'pending': '🟡 В обработке',
                'completed': '🟢 Выполнен', 
                'cancelled': '🔴 Отменен'
            }.get(order['status'], order['status'])
            print(f"📋 Статус: {status_display}")
            
            print(f"💰 Сумма: {order['total_amount']:.2f} руб.")
            
            if order['description']:
                print(f"📝 Описание: {order['description']}")
            
            print(f"🕐 Создан: {order['created_at']}")
            print(f"🔄 Обновлен: {order['updated_at']}")
            
        except ValueError:
            print("❌ Неверный формат ID заказа")

    def delete_order_interactive(self):
        """Удаление заказа"""
        print("\n" + "="*50)
        print("🗑️  УДАЛЕНИЕ ЗАКАЗА")
        print("="*50)
        
        try:
            order_id = int(input("📦 ID заказа для удаления: "))
            
            # Получаем информацию о заказе для подтверждения
            order_result = self.order_service.get_order(order_id)
            if not order_result['success']:
                print("❌ Заказ не найден")
                return
            
            order = order_result['order']
            print(f"📦 Заказ для удаления: #{order['order_number']}")
            print(f"👤 Клиент ID: {order['client_id']}")
            print(f"💰 Сумма: {order['total_amount']:.2f} руб.")
            print(f"📋 Статус: {order['status']}")
            
            confirm = input("\n❓ Вы уверены, что хотите удалить заказ? (y/n): ").lower()
            if confirm != 'y':
                print("Удаление отменено")
                return
            
            result = self.order_service.delete_order(order_id)
            if result['success']:
                print("✅ Заказ успешно удален")
                self.logger.info(f"Удален заказ {order_id}")
            else:
                print("❌ Ошибки при удалении заказа:")
                for error in result['errors']:
                    print(f"   - {error}")
                    
        except ValueError:
            print("❌ Неверный формат ID заказа")

    def show_order_statistics(self):
        """Показать статистику заказов"""
        print("\n" + "="*50)
        print("📈 СТАТИСТИКА ЗАКАЗОВ")
        print("="*50)
        
        try:
            period_days = int(input("📅 Период в днях (по умолчанию 30): ") or "30")
            client_id_str = input("👤 ID клиента (оставьте пустым для общей статистики): ").strip()
            
            client_id = None
            if client_id_str:
                client_id = int(client_id_str)
            
            stats = self.order_service.get_order_statistics(period_days, client_id)
            
            print(f"\n📊 Статистика за период: {stats['period']['days']} дней")
            print(f"📅 С {stats['period']['start_date']} по {stats['period']['end_date']}")
            print(f"📦 Всего заказов: {stats['total_orders']}")
            print(f"💰 Общая выручка: {stats['total_revenue']:.2f} руб.")
            print(f"📊 Средний чек: {stats['average_order_value']:.2f} руб.")
            
            if stats['status_stats']:
                print("\n📋 Распределение по статусам:")
                for status_stat in stats['status_stats']:
                    status_display = {
                        'pending': '🟡 В обработке',
                        'completed': '🟢 Выполнен',
                        'cancelled': '🔴 Отменен'
                    }.get(status_stat['status'], status_stat['status'])
                    print(f"   {status_display}: {status_stat['count']} заказов, {status_stat['revenue']:.2f} руб.")
            
            if stats['top_clients']:
                print("\n🏆 Топ клиенты по выручке:")
                for client in stats['top_clients'][:5]:
                    print(f"   {client['name']}: {client['orders']} заказов, {client['revenue']:.2f} руб.")
                    
        except ValueError:
            print("❌ Неверный формат данных")

    # ==================== МЕТОДЫ ДЛЯ ОТЧЕТОВ ====================

    def run_reports(self):
        """Запуск меню отчетов"""
        while True:
            self.display_reports_menu()
            choice = input("\n🎯 Выберите действие: ").strip()
            
            if choice == '1':
                self.show_general_statistics()
            elif choice == '2':
                self.show_clients_report()
            elif choice == '3':
                self.show_orders_report()
            elif choice == '4':
                self.show_period_report()
            elif choice == '0':
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
            input("\n⏎ Нажмите Enter для продолжения...")

    def show_general_statistics(self):
        """Показать общую статистику"""
        print("\n" + "="*50)
        print("📈 ОБЩАЯ СТАТИСТИКА СИСТЕМЫ")
        print("="*50)
        
        # Статистика клиентов
        client_stats = self.client_service.get_client_statistics()
        
        # Статистика заказов
        order_stats = self.order_service.get_order_statistics(30)
        
        print("👥 КЛИЕНТЫ:")
        print(f"   Всего клиентов: {client_stats['total_clients']}")
        print(f"   Активных клиентов: {client_stats['active_clients']}")
        print(f"   Общая выручка: {client_stats['total_revenue']:.2f} руб.")
        print(f"   Всего заказов: {client_stats['total_orders']}")
        
        print("\n📦 ЗАКАЗЫ (за 30 дней):")
        print(f"   Всего заказов: {order_stats['total_orders']}")
        print(f"   Общая выручка: {order_stats['total_revenue']:.2f} руб.")
        print(f"   Средний чек: {order_stats['average_order_value']:.2f} руб.")
        
        print("\n📊 СТАТУСЫ ЗАКАЗОВ:")
        for status_stat in order_stats['status_stats']:
            status_display = {
                'pending': 'В обработке',
                'completed': 'Выполнено',
                'cancelled': 'Отменено'
            }.get(status_stat['status'], status_stat['status'])
            print(f"   {status_display}: {status_stat['count']} заказов")

    def show_clients_report(self):
        """Отчет по клиентам"""
        print("\n" + "="*50)
        print("👥 ОТЧЕТ ПО КЛИЕНТАМ")
        print("="*50)
        
        clients = self.client_service.search_clients({})
        
        if not clients:
            print("❌ Нет данных о клиентах")
            return
        
        # Сортируем клиентов по выручке
        sorted_clients = sorted(clients, key=lambda x: x['total_revenue'], reverse=True)
        
        print(f"📊 Всего клиентов: {len(clients)}")
        print("\n🏆 Топ клиентов по выручке:")
        print("-" * 80)
        print(f"{'ФИО':<30} {'Заказов':<10} {'Выручка':<15} {'Город':<15}")
        print("-" * 80)
        
        for client in sorted_clients[:15]:  # Топ 15
            full_name = f"{client['last_name']} {client['first_name']}"
            if client['patronymic']:
                full_name += f" {client['patronymic']}"
            
            if len(full_name) > 28:
                full_name = full_name[:25] + "..."
            
            city = client.get('city', 'Не указан')
            if len(city) > 13:
                city = city[:10] + "..."
            
            print(f"{full_name:<30} {client['total_orders']:<10} {client['total_revenue']:<15.2f} {city:<15}")

    def show_orders_report(self):
        """Отчет по заказам"""
        print("\n" + "="*50)
        print("📦 ОТЧЕТ ПО ЗАКАЗАМ")
        print("="*50)
        
        # Получаем все заказы
        search_result = self.order_service.search_orders({'per_page': 100})
        if not search_result['success']:
            print("❌ Ошибка при получении заказов")
            return
        
        orders = search_result['orders']
        
        if not orders:
            print("❌ Нет данных о заказах")
            return
        
        # Сортируем заказы по сумме
        sorted_orders = sorted(orders, key=lambda x: x['total_amount'], reverse=True)
        
        print(f"📊 Всего заказов: {len(orders)}")
        print("\n🏆 Топ заказов по сумме:")
        print("-" * 90)
        print(f"{'Номер':<15} {'Дата':<12} {'Статус':<12} {'Сумма':<15} {'Клиент':<25}")
        print("-" * 90)
        
        for order in sorted_orders[:20]:  # Топ 20
            status_display = {
                'pending': 'Обработка',
                'completed': 'Выполнен',
                'cancelled': 'Отменен'
            }.get(order['status'], order['status'])
            
            client_name = order.get('client_name', 'Неизвестно')
            if len(client_name) > 23:
                client_name = client_name[:20] + "..."
            
            print(f"{order['order_number']:<15} {order['order_date']:<12} {status_display:<12} "
                  f"{order['total_amount']:<15.2f} {client_name:<25}")

    def show_period_report(self):
        """Отчет за период"""
        print("\n" + "="*50)
        print("📅 ОТЧЕТ ЗА ПЕРИОД")
        print("="*50)
        
        try:
            period_days = int(input("📅 Период в днях: ") or "30")
            
            # Статистика заказов за период
            order_stats = self.order_service.get_order_statistics(period_days)
            
            print(f"\n📊 Отчет за {period_days} дней:")
            print(f"📅 Период: с {order_stats['period']['start_date']} по {order_stats['period']['end_date']}")
            print(f"📦 Всего заказов: {order_stats['total_orders']}")
            print(f"💰 Общая выручка: {order_stats['total_revenue']:.2f} руб.")
            print(f"📊 Средний чек: {order_stats['average_order_value']:.2f} руб.")
            
            if order_stats['daily_stats']:
                print(f"\n📈 Ежедневная статистика (последние 7 дней):")
                for daily in order_stats['daily_stats'][-7:]:
                    print(f"   {daily['date']}: {daily['orders']} заказов, {daily['revenue']:.2f} руб.")
            
            if order_stats['top_clients']:
                print(f"\n🏆 Топ клиентов за период:")
                for client in order_stats['top_clients'][:5]:
                    print(f"   {client['name']}: {client['orders']} заказов, {client['revenue']:.2f} руб.")
                    
        except ValueError:
            print("❌ Неверный формат данных")

    # ==================== МЕТОДЫ ДЛЯ ИМПОРТА ====================

    def run_import(self):
        """Запуск меню импорта данных"""
        while True:
            self.display_import_menu()
            choice = input("\n🎯 Выберите действие: ").strip()
            
            if choice == '1':
                self.import_clients()
            elif choice == '2':
                self.import_orders()
            elif choice == '3':
                self.create_import_template()
            elif choice == '0':
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
            input("\n⏎ Нажмите Enter для продолжения...")

    def import_clients(self):
        """Импорт клиентов из Excel"""
        print("\n" + "="*50)
        print("📥 ИМПОРТ КЛИЕНТОВ ИЗ EXCEL")
        print("="*50)
        
        file_path = input("📁 Путь к файлу Excel: ").strip()
        
        if not file_path:
            print("❌ Путь к файлу не указан")
            return
        
        if not Path(file_path).exists():
            print("❌ Файл не найден")
            return
        
        print("🔄 Импорт клиентов...")
        result = self.import_service.import_clients_from_excel(file_path)
        
        if result['success']:
            results = result['results']
            print(f"\n✅ Импорт завершен!")
            print(f"📊 Всего строк: {results['total_rows']}")
            print(f"✅ Импортировано: {results['imported']}")
            print(f"🔄 Обновлено: {results['updated']}")
            print(f"⏭️  Пропущено: {results['skipped']}")
            
            if results['errors']:
                print(f"\n❌ Ошибки ({len(results['errors'])}):")
                for error in results['errors'][:5]:  # Показываем первые 5 ошибок
                    print(f"   Строка {error['row']}: {error['error']}")
        else:
            print("❌ Ошибка импорта:")
            for error in result['errors']:
                print(f"   - {error}")

    def import_orders(self):
        """Импорт заказов из Excel"""
        print("\n" + "="*50)
        print("📥 ИМПОРТ ЗАКАЗОВ ИЗ EXCEL")
        print("="*50)
        
        file_path = input("📁 Путь к файлу Excel: ").strip()
        
        if not file_path:
            print("❌ Путь к файлу не указан")
            return
        
        if not Path(file_path).exists():
            print("❌ Файл не найден")
            return
        
        print("🔄 Импорт заказов...")
        result = self.import_service.import_orders_from_excel(file_path)
        
        if result['success']:
            results = result['results']
            print(f"\n✅ Импорт завершен!")
            print(f"📊 Всего строк: {results['total_rows']}")
            print(f"✅ Импортировано: {results['imported']}")
            print(f"⏭️  Пропущено: {results['skipped']}")
            
            if results['errors']:
                print(f"\n❌ Ошибки ({len(results['errors'])}):")
                for error in results['errors'][:5]:
                    print(f"   Строка {error['row']}: {error['error']}")
        else:
            print("❌ Ошибка импорта:")
            for error in result['errors']:
                print(f"   - {error}")

    def create_import_template(self):
        """Создание шаблона импорта"""
        print("\n" + "="*50)
        print("📋 СОЗДАНИЕ ШАБЛОНА ИМПОРТА")
        print("="*50)
        
        print("1. 👥 Шаблон для клиентов")
        print("2. 📦 Шаблон для заказов")
        
        choice = input("Выберите тип шаблона: ").strip()
        
        try:
            if choice == '1':
                filename = self.import_service.create_import_template('clients')
                print(f"✅ Шаблон для клиентов создан: {filename}")
            elif choice == '2':
                filename = self.import_service.create_import_template('orders')
                print(f"✅ Шаблон для заказов создан: {filename}")
            else:
                print("❌ Неверный выбор")
        except Exception as e:
            print(f"❌ Ошибка создания шаблона: {e}")

    # ==================== МЕТОДЫ ДЛЯ ЭКСПОРТА ====================

    def run_export(self):
        """Запуск меню экспорта данных"""
        while True:
            self.display_export_menu()
            choice = input("\n🎯 Выберите действие: ").strip()
            
            if choice == '1':
                self.export_clients()
            elif choice == '2':
                self.export_orders()
            elif choice == '3':
                self.export_comprehensive_report()
            elif choice == '0':
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
            input("\n⏎ Нажмите Enter для продолжения...")

    def export_clients(self):
        """Экспорт клиентов в Excel"""
        print("\n" + "="*50)
        print("📤 ЭКСПОРТ КЛИЕНТОВ В EXCEL")
        print("="*50)
        
        filename = input("📁 Имя файла (оставьте пустым для автоимени): ").strip() or None
        
        try:
            print("🔄 Экспорт клиентов...")
            exported_file = self.report_service.export_clients_to_excel(filename=filename)
            print(f"✅ Клиенты экспортированы в: {exported_file}")
            self.logger.info(f"Экспорт клиентов в {exported_file}")
        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")

    def export_orders(self):
        """Экспорт заказов в Excel"""
        print("\n" + "="*50)
        print("📤 ЭКСПОРТ ЗАКАЗОВ В EXCEL")
        print("="*50)
        
        filename = input("📁 Имя файла (оставьте пустым для автоимени): ").strip() or None
        
        try:
            print("🔄 Экспорт заказов...")
            exported_file = self.report_service.export_orders_to_excel(filename=filename)
            print(f"✅ Заказы экспортированы в: {exported_file}")
            self.logger.info(f"Экспорт заказов в {exported_file}")
        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")

    def export_comprehensive_report(self):
        """Экспорт комплексного отчета"""
        print("\n" + "="*50)
        print("📊 КОМПЛЕКСНЫЙ ОТЧЕТ")
        print("="*50)
        
        filename = input("📁 Имя файла (оставьте пустым для автоимени): ").strip() or None
        
        try:
            print("🔄 Создание комплексного отчета...")
            
            # Создаем временный файл для комплексного отчета
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"comprehensive_report_{timestamp}.xlsx"
            
            # Экспортируем клиентов и заказы
            clients_file = self.report_service.export_clients_to_excel()
            orders_file = self.report_service.export_orders_to_excel()
            
            print(f"✅ Комплексный отчет создан:")
            print(f"   👥 Клиенты: {clients_file}")
            print(f"   📦 Заказы: {orders_file}")
            self.logger.info(f"Создан комплексный отчет: {clients_file}, {orders_file}")
            
        except Exception as e:
            print(f"❌ Ошибка создания отчета: {e}")

    # ==================== МЕТОДЫ ДЛЯ METABASE ====================

    def run_metabase(self):
        """Запуск меню Metabase аналитики"""
        if not self.metabase_service:
            print("❌ Metabase не настроен")
            print("ℹ️  Убедитесь, что установлены переменные окружения:")
            print("   - METABASE_URL")
            print("   - METABASE_USERNAME") 
            print("   - METABASE_PASSWORD")
            return
        
        while True:
            self.display_metabase_menu()
            choice = input("\n🎯 Выберите действие: ").strip()
            
            if choice == '1':
                self.setup_metabase_dashboard()
            elif choice == '2':
                self.get_metabase_dashboard_url()
            elif choice == '3':
                self.show_metabase_statistics()
            elif choice == '0':
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
            input("\n⏎ Нажмите Enter для продолжения...")

    def setup_metabase_dashboard(self):
        """Настройка дашборда в Metabase"""
        print("\n" + "="*50)
        print("🎯 НАСТРОЙКА METABASE DASHBOARD")
        print("="*50)
        
        print("🔄 Настройка дашборда аналитики...")
        
        result = self.metabase_service.setup_analytics_dashboard(self.report_service)
        
        if result['success']:
            print(f"✅ Дашборд успешно создан!")
            print(f"🆔 ID дашборда: {result['dashboard_id']}")
            print(f"🔗 Ссылка: {result['dashboard_url']}")
            self.logger.info(f"Создан Metabase дашборд: {result['dashboard_url']}")
        else:
            print(f"❌ Ошибка создания дашборда: {result['error']}")

    def get_metabase_dashboard_url(self):
        """Получение ссылки на дашборд"""
        print("\n" + "="*50)
        print("🔗 ПОЛУЧЕНИЕ ССЫЛКИ НА DASHBOARD")
        print("="*50)
        
        dashboard_id = input("🆔 ID дашборда: ").strip()
        
        if not dashboard_id:
            print("❌ ID дашборда не указан")
            return
        
        try:
            dashboard_url = self.metabase_service.get_dashboard_url(dashboard_id)
            print(f"🔗 Ссылка на дашборд: {dashboard_url}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def show_metabase_statistics(self):
        """Показать статистику для Metabase"""
        print("\n" + "="*50)
        print("📊 СТАТИСТИКА ДЛЯ METABASE")
        print("="*50)
        
        dashboard_data = self.report_service.generate_dashboard_data()
        
        print("👥 КЛИЕНТЫ:")
        print(f"   Всего: {dashboard_data['client_stats']['total_clients']}")
        print(f"   Активных: {dashboard_data['client_stats']['active_clients']}")
        print(f"   Выручка: {dashboard_data['client_stats']['total_revenue']:.2f} руб.")
        
        print("\n📦 ЗАКАЗЫ (30 дней):")
        print(f"   Всего: {dashboard_data['order_stats']['total_orders']}")
        print(f"   Выручка: {dashboard_data['order_stats']['total_revenue']:.2f} руб.")
        
        print(f"\n🕐 Данные сгенерированы: {dashboard_data['generated_at']}")

    # ==================== МЕТОДЫ ДЛЯ ТЕСТИРОВАНИЯ ====================

    def run_testing(self):
        """Запуск меню тестирования"""
        while True:
            self.display_testing_menu()
            choice = input("\n🎯 Выберите действие: ").strip()
            
            if choice == '1':
                self.run_functional_tests()
            elif choice == '2':
                self.run_unit_tests()
            elif choice == '3':
                self.run_performance_tests()
            elif choice == '4':
                self.run_error_handling_tests()
            elif choice == '0':
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
            
            input("\n⏎ Нажмите Enter для продолжения...")

    def run_functional_tests(self):
        """Запуск функциональных тестов"""
        print("\n" + "="*50)
        print("✅ ФУНКЦИОНАЛЬНОЕ ТЕСТИРОВАНИЕ")
        print("="*50)
        
        print("🧪 Запуск функциональных тестов...")
        
        # Тест создания клиента
        print("1. Тест создания клиента...")
        test_client_data = {
            'first_name': 'Тест',
            'last_name': 'Тестовый',
            'email': 'test@example.com',
            'phone': '+79161234567',
            'city': 'Москва'
        }
        
        result = self.client_service.add_client(test_client_data)
        if result['success']:
            print("   ✅ Клиент создан успешно")
            test_client_id = result['client']['id']
            
            # Тест создания заказа
            print("2. Тест создания заказа...")
            test_order_data = {
                'client_id': test_client_id,
                'total_amount': 1000.0,
                'description': 'Тестовый заказ'
            }
            
            order_result = self.order_service.create_order(test_order_data)
            if order_result['success']:
                print("   ✅ Заказ создан успешно")
                test_order_id = order_result['order']['id']
                
                # Тест поиска
                print("3. Тест поиска клиентов...")
                clients = self.client_service.search_clients({'first_name': 'Тест'})
                if clients:
                    print("   ✅ Поиск клиентов работает")
                
                # Тест поиска заказов
                print("4. Тест поиска заказов...")
                orders_result = self.order_service.search_orders({'client_id': test_client_id})
                if orders_result['success'] and orders_result['orders']:
                    print("   ✅ Поиск заказов работает")
                
                # Очистка тестовых данных
                print("5. Очистка тестовых данных...")
                self.order_service.delete_order(test_order_id)
                self.client_service.delete_client(test_client_id)
                print("   ✅ Тестовые данные удалены")
                
            else:
                print("   ❌ Ошибка создания заказа")
                # Удаляем тестового клиента
                self.client_service.delete_client(test_client_id)
        else:
            print("   ❌ Ошибка создания клиента")
        
        print("\n✅ Функциональное тестирование завершено")

    def run_unit_tests(self):
        """Запуск модульных тестов"""
        print("\n" + "="*50)
        print("🔧 МОДУЛЬНОЕ ТЕСТИРОВАНИЕ")
        print("="*50)
        
        print("🧪 Запуск модульных тестов...")
        
        # Тесты валидаторов
        print("1. Тест валидаторов...")
        
        # Тест валидации клиента
        test_client_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'phone': '+79161234567'
        }
        
        is_valid, errors = self.client_validator.validate_client_data(test_client_data)
        if is_valid:
            print("   ✅ Валидация клиента работает")
        else:
            print("   ❌ Валидация клиента не работает")
        
        # Тест валидации заказа
        test_order_data = {
            'client_id': 1,
            'total_amount': 1000.0
        }
        
        is_valid, errors = self.order_validator.validate_order_data(test_order_data)
        if is_valid:
            print("   ✅ Валидация заказа работает")
        else:
            print("   ❌ Валидация заказа не работает")
        
        # Тест поиска с неверными параметрами
        print("2. Тест обработки ошибок...")
        try:
            clients = self.client_service.search_clients({'invalid_param': 'value'})
            print("   ✅ Обработка неверных параметров работает")
        except Exception as e:
            print(f"   ❌ Ошибка обработки параметров: {e}")
        
        print("\n✅ Модульное тестирование завершено")

    def run_performance_tests(self):
        """Запуск тестов производительности"""
        print("\n" + "="*50)
        print("📊 ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
        print("="*50)
        
        print("🧪 Тестирование производительности...")
        
        import time
        
        # Тест скорости поиска
        start_time = time.time()
        clients = self.client_service.search_clients({})
        search_time = time.time() - start_time
        
        print(f"1. Поиск {len(clients)} клиентов: {search_time:.3f} сек")
        
        # Тест скорости создания отчета
        start_time = time.time()
        try:
            self.report_service.export_clients_to_excel(filename='perf_test.xlsx')
            report_time = time.time() - start_time
            print(f"2. Создание отчета: {report_time:.3f} сек")
            
            # Удаляем временный файл
            if Path('perf_test.xlsx').exists():
                Path('perf_test.xlsx').unlink()
        except Exception as e:
            print(f"2. Ошибка создания отчета: {e}")
        
        print("\n✅ Тестирование производительности завершено")

    def run_error_handling_tests(self):
        """Запуск тестов обработки ошибок"""
        print("\n" + "="*50)
        print("🐛 ТЕСТ ОБРАБОТКИ ОШИБОК")
        print("="*50)
        
        print("🧪 Тестирование обработки ошибок...")
        
        # Тест с неверными данными клиента
        print("1. Тест с неверными данными клиента...")
        invalid_client_data = {
            'first_name': 'John',  # латиница
            'last_name': '123',    # цифры
            'email': 'invalid-email',
            'phone': '123'
        }
        
        result = self.client_service.add_client(invalid_client_data)
        if not result['success']:
            print("   ✅ Ошибки валидации обрабатываются корректно")
        else:
            print("   ❌ Ошибки валидации не обрабатываются")
        
        # Тест с несуществующим клиентом
        print("2. Тест с несуществующим клиентом...")
        order_result = self.order_service.create_order({
            'client_id': 99999,
            'total_amount': 1000.0
        })
        
        if not order_result['success']:
            print("   ✅ Ошибка несуществующего клиента обрабатывается")
        else:
            print("   ❌ Ошибка несуществующего клиента не обрабатывается")
        
        # Тест с неверной суммой заказа
        print("3. Тест с неверной суммой заказа...")
        order_result = self.order_service.create_order({
            'client_id': 1,
            'total_amount': -100.0  # отрицательная сумма
        })
        
        if not order_result['success']:
            print("   ✅ Ошибка неверной суммы обрабатывается")
        else:
            print("   ❌ Ошибка неверной суммы не обрабатывается")
        
        print("\n✅ Тестирование обработки ошибок завершено")

    # ==================== ГЛАВНЫЙ МЕТОД ЗАПУСКА ====================

    def run(self):
        """Главный цикл системы"""
        print("🚀 Запуск системы управления клиентами и заказами...")
        print("📊 Версия: 1.0")
        print("📅 Дата запуска:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        try:
            while True:
                self.display_main_menu()
                choice = input("\n🎯 Выберите раздел: ").strip()
                
                if choice == '1':
                    self.run_clients_management()
                elif choice == '2':
                    self.run_orders_management()
                elif choice == '3':
                    self.run_reports()
                elif choice == '4':
                    self.run_import()
                elif choice == '5':
                    self.run_export()
                elif choice == '6':
                    self.run_metabase()
                elif choice == '7':
                    self.run_testing()
                elif choice == '0':
                    print("\n👋 Выход из системы...")
                    print("📝 Логи сохранены в client_management.log")
                    break
                else:
                    print("❌ Неверный выбор. Попробуйте снова.")
                    
        except KeyboardInterrupt:
            print("\n\n⚠️  Программа прервана пользователем")
        except Exception as e:
            print(f"\n💥 Критическая ошибка: {e}")
            self.logger.error(f"Критическая ошибка: {e}")
        finally:
            print("✅ Работа системы завершена")

if __name__ == "__main__":
    # Создаем экземпляр системы и запускаем
    system = ClientManagementSystem()
    system.run()
