import pandas as pd
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

from src.services.client_service import ClientService
from src.services.order_service import OrderService

class ReportService:
    """Сервис для генерации отчетов и визуализации данных"""
    
    def __init__(self, client_service: ClientService, order_service: OrderService):
        self.client_service = client_service
        self.order_service = order_service
        self.logger = logging.getLogger(__name__)
    
    def export_clients_to_excel(self, filters: Dict = None, filename: str = None) -> str:
        """Экспорт клиентов в Excel с расширенной информацией"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clients_export_{timestamp}.xlsx"
        
        # Получаем клиентов
        clients = self.client_service.search_clients(filters or {})
        
        if not clients:
            raise ValueError("Нет данных для экспорта")
        
        # Подготавливаем данные
        data = []
        for client in clients:
            # Получаем заказы клиента
            orders = self.order_service.get_client_orders(client['id'])
            last_order_date = max([order['order_date'] for order in orders]) if orders else None
            
            data.append({
                'ID': client['id'],
                'Фамилия': client['last_name'],
                'Имя': client['first_name'],
                'Отчество': client.get('patronymic', ''),
                'Email': client.get('email', ''),
                'Телефон': client.get('phone', ''),
                'Город': client.get('city', ''),
                'Статус': client['status'],
                'Всего заказов': client['total_orders'],
                'Общая выручка': client['total_revenue'],
                'Дата регистрации': client['registration_date'],
                'Последний заказ': last_order_date,
                'Примечания': client.get('notes', '')
            })
        
        # Создаем Excel файл
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Основной лист с клиентами
            df_clients = pd.DataFrame(data)
            df_clients.to_excel(writer, sheet_name='Клиенты', index=False)
            
            # Лист со статистикой
            self._create_clients_statistics_sheet(writer, clients)
            
            # Форматирование
            self._format_excel_file(writer)
        
        self.logger.info(f"Экспортировано {len(clients)} клиентов в {filename}")
        return filename
    
    def export_orders_to_excel(self, filters: Dict = None, filename: str = None) -> str:
        """Экспорт заказов в Excel с детализацией"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"orders_export_{timestamp}.xlsx"
        
        # Получаем заказы
        search_result = self.order_service.search_orders(filters or {})
        if not search_result['success']:
            raise ValueError(f"Ошибка получения заказов: {search_result['errors']}")
        
        orders = search_result['orders']
        
        if not orders:
            raise ValueError("Нет данных для экспорта")
        
        # Подготавливаем данные
        orders_data = []
        for order in orders:
            orders_data.append({
                'ID заказа': order['id'],
                'Номер заказа': order['order_number'],
                'ID клиента': order['client_id'],
                'Клиент': order.get('client_name', ''),
                'Дата заказа': order['order_date'],
                'Статус': self._get_status_display(order['status']),
                'Сумма': order['total_amount'],
                'Описание': order.get('description', ''),
                'Создан': order['created_at'],
                'Обновлен': order['updated_at']
            })
        
        # Создаем Excel файл
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Лист с заказами
            df_orders = pd.DataFrame(orders_data)
            df_orders.to_excel(writer, sheet_name='Заказы', index=False)
            
            # Лист со статистикой
            self._create_orders_statistics_sheet(writer, orders)
            
            # Лист с аналитикой
            self._create_analytics_sheet(writer, orders)
            
            # Форматирование
            self._format_excel_file(writer)
        
        self.logger.info(f"Экспортировано {len(orders)} заказов в {filename}")
        return filename
    
    def _get_status_display(self, status: str) -> str:
        """Получение читаемого статуса"""
        status_map = {
            'pending': 'В обработке',
            'completed': 'Выполнен',
            'cancelled': 'Отменен'
        }
        return status_map.get(status, status)
    
    def _create_clients_statistics_sheet(self, writer, clients: List[Dict]):
        """Создание листа со статистикой клиентов"""
        stats_data = []
        
        # Основная статистика
        total_clients = len(clients)
        active_clients = len([c for c in clients if c['status'] == 'active'])
        total_revenue = sum(client['total_revenue'] for client in clients)
        total_orders = sum(client['total_orders'] for client in clients)
        
        stats_data.append({'Показатель': 'Всего клиентов', 'Значение': total_clients})
        stats_data.append({'Показатель': 'Активных клиентов', 'Значение': active_clients})
        stats_data.append({'Показатель': 'Общая выручка', 'Значение': total_revenue})
        stats_data.append({'Показатель': 'Всего заказов', 'Значение': total_orders})
        stats_data.append({'Показатель': 'Средняя выручка на клиента', 'Значение': total_revenue / total_clients if total_clients > 0 else 0})
        stats_data.append({'Показатель': 'Среднее количество заказов на клиента', 'Значение': total_orders / total_clients if total_clients > 0 else 0})
        
        # Статистика по городам
        city_stats = {}
        for client in clients:
            city = client.get('city', 'Не указан')
            city_stats[city] = city_stats.get(city, 0) + 1
        
        for city, count in sorted(city_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            stats_data.append({'Показатель': f'Клиентов в г. {city}', 'Значение': count})
        
        df_stats = pd.DataFrame(stats_data)
        df_stats.to_excel(writer, sheet_name='Статистика', index=False)
    
    def _create_orders_statistics_sheet(self, writer, orders: List[Dict]):
        """Создание листа со статистикой заказов"""
        stats_data = []
        
        # Основная статистика
        total_orders = len(orders)
        total_revenue = sum(order['total_amount'] for order in orders)
        
        # Статистика по статусам
        status_stats = {}
        for order in orders:
            status = order['status']
            status_stats[status] = status_stats.get(status, 0) + 1
        
        stats_data.append({'Показатель': 'Всего заказов', 'Значение': total_orders})
        stats_data.append({'Показатель': 'Общая выручка', 'Значение': total_revenue})
        stats_data.append({'Показатель': 'Средний чек', 'Значение': total_revenue / total_orders if total_orders > 0 else 0})
        
        for status, count in status_stats.items():
            status_display = self._get_status_display(status)
            stats_data.append({'Показатель': f'Заказов со статусом "{status_display}"', 'Значение': count})
        
        # Статистика по датам
        date_stats = {}
        for order in orders:
            date = order['order_date'][:10]  # Берем только дату
            date_stats[date] = date_stats.get(date, 0) + 1
        
        for date, count in sorted(date_stats.items(), key=lambda x: x[0], reverse=True)[:10]:
            stats_data.append({'Показатель': f'Заказов за {date}', 'Значение': count})
        
        df_stats = pd.DataFrame(stats_data)
        df_stats.to_excel(writer, sheet_name='Статистика заказов', index=False)
    
    def _create_analytics_sheet(self, writer, orders: List[Dict]):
        """Создание листа с аналитикой"""
        analytics_data = []
        
        # Анализ по дням недели
        day_stats = {}
        for order in orders:
            try:
                order_date = datetime.fromisoformat(order['order_date'].replace('Z', '+00:00'))
                day_name = order_date.strftime('%A')
                day_stats[day_name] = day_stats.get(day_name, 0) + 1
            except:
                continue
        
        for day, count in day_stats.items():
            analytics_data.append({'День недели': day, 'Количество заказов': count})
        
        df_analytics = pd.DataFrame(analytics_data)
        df_analytics.to_excel(writer, sheet_name='Аналитика', index=False)
    
    def _format_excel_file(self, writer):
        """Форматирование Excel файла"""
        workbook = writer.book
        
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            
            # Автоматическая ширина колонок
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Заголовки жирным
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True)
    
    def generate_dashboard_data(self) -> Dict:
        """Генерация данных для дашборда"""
        # Статистика клиентов
        client_stats = self.client_service.get_client_statistics()
        
        # Статистика заказов
        order_stats = self.order_service.get_order_statistics(period_days=30)
        
        # Последние заказы
        recent_orders_result = self.order_service.search_orders({
            'per_page': 10,
            'sort_by': 'order_date',
            'sort_order': 'desc'
        })
        recent_orders = recent_orders_result.get('orders', []) if recent_orders_result['success'] else []
        
        # Топ клиенты
        top_clients = self.client_service.search_clients({})
        top_clients = sorted(top_clients, key=lambda x: x['total_revenue'], reverse=True)[:5]
        
        return {
            'client_stats': client_stats,
            'order_stats': order_stats,
            'recent_orders': recent_orders,
            'top_clients': top_clients,
            'generated_at': datetime.now().isoformat()
        }
