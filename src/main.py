import sys
from datetime import datetime
from utils.validators import validate_date, validate_email, validate_phone
from modules.client_management import ClientManager
from modules.interface import main_menu, add_client_interface, search_clients_interface
from modules.config_database import init_database
from config.database import get_db_connection

def main():
    """Основная функция программы"""
    print("Инициализация системы...")
    
    try:
        # Инициализация базы данных
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