from services.client_service import ClientService
from services.order_service import OrderService
from services.report_service import ReportService
from services.import_service import ImportService
from utils.validators import validate_russian_name, validate_email, validate_phone
import json
from datetime import datetime

class ClientManagementSystem:
    #Главный класс системы управления клиентами
    
    def __init__(self):
        self.client_service = ClientService()
        self.order_service = OrderService()
        self.report_service = ReportService(self.client_service, self.order_service)
        self.import_service = ImportService(self.client_service, self.order_service)
    
    def display_menu(self):
        """Отображение главного меню"""
        print("\n" + "="*50)
        print("СИСТЕМА УПРАВЛЕНИЯ КЛИЕНТАМИ")
        print("="*50)
        print("1. Добавить клиента")
        print("2. Поиск клиентов")
        print("3. Редактировать клиента")
        print("4. Удалить клиента")
        print("5. Создать заказ")
        print("6. Поиск заказов")
        print("7. Статистика")
        print("8. Импорт данных")
        print("9. Экспорт отчетов")
        print("0. Выход")
        print("="*50)
    
    def add_client_interactive(self):
        """Интерактивное добавление клиента"""
        print("\n--- ДОБАВЛЕНИЕ НОВОГО КЛИЕНТА ---")
        
        first_name = input("Имя: ").strip()
        last_name = input("Фамилия: ").strip()
        patronymic = input("Отчество (необязательно): ").strip() or None
        email = input("Email (необязательно): ").strip() or None
        phone = input("Телефон (+7XXXXXXXXXX): ").strip() or None
        city = input("Город: ").strip() or None
        notes = input("Примечания (необязательно): ").strip() or None
        
        # Валидация данных
        is_valid, error = validate_russian_name(first_name)
        if not is_valid:
            print(f"Ошибка в имени: {error}")
            return
        
        is_valid, error = validate_russian_name(last_name)
        if not is_valid:
            print(f"Ошибка в фамилии: {error}")
            return
        
        if email:
            is_valid, error = validate_email(email)
            if not is_valid:
                print(f"Ошибка в email: {error}")
                return
        
        if phone:
            is_valid, error = validate_phone(phone)
            if not is_valid:
                print(f"Ошибка в телефоне: {error}")
                return
        
        # Создание клиента
        client_data = {
            'first_name': first_name,
            'last_name': last_name,
            'patronymic': patronymic,
            'email': email,
            'phone': phone,
            'city': city,
            'notes': notes
        }
        
        result = self.client_service.add_client(client_data)
        
        if result['success']:
            print("Клиент успешно добавлен!")
            print(f"ID клиента: {result['client']['id']}")
        else:
            print("Ошибки при добавлении клиента:")
            for error in result['errors']:
                print(f"   - {error}")
    
    def search_clients_interactive(self):
        """Интерактивный поиск клиентов"""
        print("\n--- ПОИСК КЛИЕНТОВ ---")
        
        print("Введите параметры поиска (оставьте пустым для пропуска):")
        first_name = input("Имя: ").strip() or None
        last_name = input("Фамилия: ").strip() or None
        email = input("Email: ").strip() or None
        phone = input("Телефон: ").strip() or None
        city = input("Город: ").strip() or None
        
        search_params = {}
        if first_name:
            search_params['first_name'] = first_name
        if last_name:
            search_params['last_name'] = last_name
        if email:
            search_params['email'] = email
        if phone:
            search_params['phone'] = phone
        if city:
            search_params['city'] = city
        
        clients = self.client_service.search_clients(search_params)
        
        print(f"\nНайдено клиентов: {len(clients)}")
        for client in clients:
            print(f"\nID: {client['id']}")
            print(f"ФИО: {client['last_name']} {client['first_name']} {client['patronymic'] or ''}")
            print(f"Email: {client['email'] or 'не указан'}")
            print(f"Телефон: {client['phone'] or 'не указан'}")
            print(f"Город: {client['city'] or 'не указан'}")
            print(f"Статус: {client['status']}")
            print(f"Заказов: {client['total_orders']}, Выручка: {client['total_revenue']} руб.")
            print("-" * 30)
    
    def run(self):
        """Запуск системы"""
        while True:
            self.display_menu()
            choice = input("Выберите действие: ").strip()
            
            if choice == '1':
                self.add_client_interactive()
            elif choice == '2':
                self.search_clients_interactive()
            elif choice == '3':
                self.edit_client_interactive()
            elif choice == '4':
                self.delete_client_interactive()
            elif choice == '5':
                self.create_order_interactive()
            elif choice == '6':
                self.search_orders_interactive()
            elif choice == '7':
                self.show_stats()
            elif choice == '8':
                self.import_data()
            elif choice == '9':
                self.export_reports()
            elif choice == '0':
                print("Выход из системы...")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")
            
            input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    system = ClientManagementSystem()
    system.run()
