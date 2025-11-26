import requests
import json
import logging
from typing import Dict, List, Optional

class MetabaseService:
    """Сервис для интеграции с Metabase"""
    
    def __init__(self, metabase_url: str, username: str, password: str):
        self.metabase_url = metabase_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        self.logger = logging.getLogger(__name__)
        
        self._authenticate(username, password)
    
    def _authenticate(self, username: str, password: str):
        """Аутентификация в Metabase"""
        auth_data = {
            'username': username,
            'password': password
        }
        
        try:
            response = self.session.post(
                f"{self.metabase_url}/api/session",
                json=auth_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                self.token = response.json()['id']
                self.session.headers.update({
                    'X-Metabase-Session': self.token
                })
                self.logger.info("Успешная аутентификация в Metabase")
            else:
                raise Exception(f"Ошибка аутентификации: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Ошибка подключения к Metabase: {e}")
            raise
    
    def setup_analytics_dashboard(self, report_service) -> Dict:
        """Настройка дашборда аналитики в Metabase"""
        try:
            # Создаем дашборд
            dashboard_id = self.create_dashboard(
                "Аналитика клиентов и заказов",
                "Дашборд для анализа клиентской базы и заказов"
            )
            
            if not dashboard_id:
                return {'success': False, 'error': 'Не удалось создать дашборд'}
            
            # Генерируем данные для вопросов
            dashboard_data = report_service.generate_dashboard_data()
            
            # Создаем вопросы (визуализации)
            questions = [
                self._create_clients_by_city_question(dashboard_data),
                self._create_orders_timeline_question(dashboard_data),
                self._create_revenue_by_status_question(dashboard_data),
                self._create_top_clients_question(dashboard_data)
            ]
            
            # Добавляем вопросы на дашборд
            position = {'col': 0, 'row': 0}
            for question_config in questions:
                if question_config:
                    question_id = self.create_question(question_config)
                    if question_id:
                        self.add_question_to_dashboard(dashboard_id, question_id, position)
                        position['col'] += 6
                        if position['col'] >= 12:
                            position['col'] = 0
                            position['row'] += 4
            
            dashboard_url = self.get_dashboard_url(dashboard_id)
            
            return {
                'success': True,
                'dashboard_id': dashboard_id,
                'dashboard_url': dashboard_url,
                'message': 'Дашборд успешно создан'
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки дашборда: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_clients_by_city_question(self, data: Dict) -> Dict:
        """Создание вопроса по распределению клиентов по городам"""
        city_stats = data['client_stats'].get('city_stats', [])
        
        question_data = {
            'name': 'Клиенты по городам',
            'display': 'bar',
            'dataset_query': {
                'type': 'native',
                'native': {
                    'query': """
                    SELECT city as "Город", COUNT(*) as "Количество клиентов"
                    FROM clients 
                    WHERE city IS NOT NULL 
                    GROUP BY city 
                    ORDER BY COUNT(*) DESC
                    LIMIT 10
                    """
                }
            },
            'visualization_settings': {
                'graph.dimensions': ['Город'],
                'graph.metrics': ['Количество клиентов']
            }
        }
        
        return question_data
    
    def _create_orders_timeline_question(self, data: Dict) -> Dict:
        """Создание вопроса по динамике заказов"""
        question_data = {
            'name': 'Динамика заказов',
            'display': 'line',
            'dataset_query': {
                'type': 'native',
                'native': {
                    'query': """
                    SELECT 
                        DATE(order_date) as "Дата", 
                        COUNT(*) as "Количество заказов",
                        SUM(total_amount) as "Выручка"
                    FROM orders 
                    WHERE order_date >= date('now', '-30 days')
                    GROUP BY DATE(order_date)
                    ORDER BY DATE(order_date)
                    """
                }
            },
            'visualization_settings': {
                'graph.dimensions': ['Дата'],
                'graph.metrics': ['Количество заказов', 'Выручка']
            }
        }
        
        return question_data
    
    def _create_revenue_by_status_question(self, data: Dict) -> Dict:
        """Создание вопроса по выручке по статусам"""
        question_data = {
            'name': 'Выручка по статусам заказов',
            'display': 'pie',
            'dataset_query': {
                'type': 'native',
                'native': {
                    'query': """
                    SELECT 
                        CASE status 
                            WHEN 'pending' THEN 'В обработке'
                            WHEN 'completed' THEN 'Выполнен' 
                            WHEN 'cancelled' THEN 'Отменен'
                            ELSE status 
                        END as "Статус",
                        SUM(total_amount) as "Выручка"
                    FROM orders 
                    GROUP BY status
                    """
                }
            },
            'visualization_settings': {
                'pie.dimension': 'Статус',
                'pie.metric': 'Выручка'
            }
        }
        
        return question_data
    
    def _create_top_clients_question(self, data: Dict) -> Dict:
        """Создание вопроса по топ клиентам"""
        question_data = {
            'name': 'Топ клиенты по выручке',
            'display': 'table',
            'dataset_query': {
                'type': 'native',
                'native': {
                    'query': """
                    SELECT 
                        first_name || ' ' || last_name as "Клиент",
                        email as "Email",
                        total_orders as "Заказов",
                        total_revenue as "Выручка"
                    FROM clients 
                    WHERE total_revenue > 0
                    ORDER BY total_revenue DESC
                    LIMIT 10
                    """
                }
            }
        }
        
        return question_data
    
    def create_dashboard(self, title: str, description: str = "") -> Optional[str]:
        """Создание дашборда"""
        dashboard_data = {
            'name': title,
            'description': description,
            'parameters': [],
            'collection_id': None
        }
        
        try:
            response = self.session.post(
                f"{self.metabase_url}/api/dashboard",
                json=dashboard_data
            )
            
            if response.status_code == 200:
                dashboard_id = response.json()['id']
                self.logger.info(f"Создан дашборд: {title} (ID: {dashboard_id})")
                return dashboard_id
            else:
                self.logger.error(f"Ошибка создания дашборда: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка при создании дашборда: {e}")
            return None
    
    def create_question(self, question_data: Dict) -> Optional[str]:
        """Создание вопроса"""
        try:
            response = self.session.post(
                f"{self.metabase_url}/api/card",
                json=question_data
            )
            
            if response.status_code == 200:
                question_id = response.json()['id']
                self.logger.info(f"Создан вопрос: {question_data.get('name', 'Unnamed')}")
                return question_id
            else:
                self.logger.error(f"Ошибка создания вопроса: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка при создании вопроса: {e}")
            return None
    
    def add_question_to_dashboard(self, dashboard_id: str, question_id: str, position: Dict = None):
        """Добавление вопроса на дашборд"""
        if position is None:
            position = {'col': 0, 'row': 0}
        
        card_data = {
            'cardId': question_id,
            'sizeX': 6,
            'sizeY': 4,
            **position
        }
        
        try:
            response = self.session.post(
                f"{self.metabase_url}/api/dashboard/{dashboard_id}/cards",
                json=card_data
            )
            
            if response.status_code == 200:
                self.logger.info(f"Вопрос {question_id} добавлен на дашборд {dashboard_id}")
                return True
            else:
                self.logger.error(f"Ошибка добавления вопроса на дашборд: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении вопроса на дашборд: {e}")
            return False
    
    def get_dashboard_url(self, dashboard_id: str) -> str:
        """Получение URL дашборда"""
        return f"{self.metabase_url}/dashboard/{dashboard_id}"
