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
            print("ФИО должно содержать минимум 3 символа")
            full_name = input("ФИО клиента: ").strip()
        
        phone = input("Телефон: ").strip()
        while not validate_phone(phone):
            print(" Неверный формат телефона. Пример: +7(999)123-45-67")
            phone = input("Телефон: ").strip()
        
        email = input("Email: ").strip()
        while not validate_email(email):
            print(" Неверный формат email. Пример: client@example.com")
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
        print("КЛИЕНТ УСПЕШНО ДОБАВЛЕН")
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
            print("\nКлиенты не найдены")
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
        print("Неверный выбор. Пожалуйста, введите число от 1 до 5.")
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
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
