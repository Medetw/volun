#!/usr/bin/env python3
"""
Скрипт для просмотра логов волонтерской платформы
Использование: python view_logs.py [options]
"""

import os
import sys
import argparse
from datetime import datetime, timedelta

# Добавляем путь к Django проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_django():
    """Настройка Django для доступа к логам"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        import django
        django.setup()
    except ImportError:
        pass  # Django не нужен для просмотра логов

def get_log_files():
    """Получить список лог файлов"""
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    return {
        'main': os.path.join(logs_dir, 'volunteering_platform.log'),
        'errors': os.path.join(logs_dir, 'errors.log')
    }

def tail_file(filename, lines=50):
    """Показать последние N строк файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            file_lines = f.readlines()
            return file_lines[-lines:] if len(file_lines) > lines else file_lines
    except FileNotFoundError:
        return [f"Файл {filename} не найден\n"]
    except Exception as e:
        return [f"Ошибка чтения файла {filename}: {e}\n"]

def search_logs(filename, pattern, lines=50):
    """Поиск по логам"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            file_lines = f.readlines()
            matching_lines = []
            for line in file_lines:
                if pattern.lower() in line.lower():
                    matching_lines.append(line)
            return matching_lines[-lines:] if len(matching_lines) > lines else matching_lines
    except FileNotFoundError:
        return [f"Файл {filename} не найден\n"]
    except Exception as e:
        return [f"Ошибка чтения файла {filename}: {e}\n"]

def show_recent_logs(log_type='main', lines=50):
    """Показать последние логи"""
    log_files = get_log_files()
    filename = log_files.get(log_type, log_files['main'])
    
    print(f"\n📋 Последние {lines} строк из {log_type} лога:")
    print("=" * 80)
    
    for line in tail_file(filename, lines):
        print(line.rstrip())

def search_in_logs(pattern, log_type='all', lines=50):
    """Поиск в логах"""
    log_files = get_log_files()
    
    if log_type == 'all':
        files_to_search = log_files.values()
    else:
        files_to_search = [log_files.get(log_type, log_files['main'])]
    
    print(f"\n🔍 Поиск '{pattern}' в логах:")
    print("=" * 80)
    
    for filename in files_to_search:
        log_name = os.path.basename(filename)
        print(f"\n📄 {log_name}:")
        matching_lines = search_logs(filename, pattern, lines)
        if matching_lines:
            for line in matching_lines:
                print(line.rstrip())
        else:
            print("  (ничего не найдено)")

def show_log_stats():
    """Показать статистику логов"""
    log_files = get_log_files()
    
    print("\n📊 Статистика лог файлов:")
    print("=" * 50)
    
    for log_type, filename in log_files.items():
        try:
            stat = os.stat(filename)
            size_mb = stat.st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(stat.st_mtime)
            
            print(f"📄 {log_type}:")
            print(f"   Размер: {size_mb:.2f} MB")
            print(f"   Последнее изменение: {mtime}")
            print(f"   Путь: {filename}")
            print()
        except FileNotFoundError:
            print(f"📄 {log_type}: файл не найден")
            print()

def main():
    parser = argparse.ArgumentParser(description='Просмотр логов волонтерской платформы')
    parser.add_argument('--tail', '-t', type=int, default=50, 
                       help='Показать последние N строк (по умолчанию: 50)')
    parser.add_argument('--search', '-s', type=str, 
                       help='Поиск по логам')
    parser.add_argument('--type', choices=['main', 'errors', 'all'], default='main',
                       help='Тип лога (main, errors, all)')
    parser.add_argument('--stats', action='store_true',
                       help='Показать статистику лог файлов')
    
    args = parser.parse_args()
    
    if args.stats:
        show_log_stats()
    elif args.search:
        search_in_logs(args.search, args.type, args.tail)
    else:
        show_recent_logs(args.type, args.tail)

if __name__ == '__main__':
    main()
