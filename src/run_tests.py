#!/usr/bin/env python3
"""
Скрипт автоматического запуска всех тестов
"""

import unittest
import sys
import os
import coverage
import argparse
from datetime import datetime

def run_all_tests():
    """Запуск всех тестов"""
    print("🔍 Поиск тестов...")
    
    # Настройка coverage
    cov = coverage.Coverage(
        source=['src'],
        omit=['*/tests/*', '*/__pycache__/*']
    )
    cov.start()
    
    # Обнаружение и запуск тестов
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    print("🚀 Запуск автоматического тестирования...")
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Остановка coverage и генерация отчета
    cov.stop()
    cov.save()
    
    # Вывод отчетов
    print("\n📊 ОТЧЕТ О ПОКРЫТИИ КОДА:")
    cov.report(show_missing=True)
    
    # Генерация HTML отчета
    cov.html_report(directory='htmlcov')
    print(f"📁 HTML отчет сохранен в: htmlcov/index.html")
    
    return result

def run_specific_tests(test_pattern):
    """Запуск конкретных тестов"""
    print(f"🔍 Поиск тестов по шаблону: {test_pattern}")
    
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern=test_pattern)
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(test_suite)

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description='Автоматическое тестирование системы')
    parser.add_argument('--pattern', '-p', help='Шаблон для поиска тестов (например: test_client*)')
    parser.add_argument('--coverage', '-c', action='store_true', help='Включить анализ покрытия кода')
    
    args = parser.parse_args()
    
    start_time = datetime.now()
    print(f"⏰ Начало тестирования: {start_time}")
    
    try:
        if args.pattern:
            result = run_specific_tests(args.pattern)
        else:
            result = run_all_tests()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n{'='*60}")
        print("🎯 ИТОГИ АВТОМАТИЧЕСКОГО ТЕСТИРОВАНИЯ")
        print(f"{'='*60}")
        print(f"⏱️  Время выполнения: {duration}")
        print(f"📋 Всего тестов: {result.testsRun}")
        print(f"✅ Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"❌ Провалено: {len(result.failures)}")
        print(f"💥 Ошибок: {len(result.errors)}")
        
        # Возвращаем код выхода для CI/CD
        if result.wasSuccessful():
            print("🎉 Все тесты пройдены успешно!")
            sys.exit(0)
        else:
            print("💥 Обнаружены проблемы в тестах!")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Ошибка при запуске тестов: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
