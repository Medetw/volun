#!/bin/bash

# Финальный скрипт для запуска всех тестов
# Использование: ./run_all_tests.sh

set -e

echo "🚀 Запуск всех тестов для Volunteer Platform..."

# Проверяем, что мы в правильной директории
if [ ! -f "manage.py" ]; then
    echo "❌ Ошибка: manage.py не найден. Убедитесь, что вы в директории backend/"
    exit 1
fi

# Устанавливаем переменную окружения
export DJANGO_SETTINGS_MODULE=config.settings

# Очищаем кэш
echo "🧹 Очистка кэша..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Запускаем тесты
echo "🧪 Запуск тестов..."
echo "=================================================="

# Запуск всех тестов моделей
pytest apps/users/tests/test_user_models.py \
       apps/projects/tests/test_project_models.py \
       apps/applications/tests/test_application_models.py \
       apps/reports/tests/test_report_models.py \
       -v \
       --tb=short

echo "=================================================="
echo "✅ Все тесты успешно пройдены!"

# Опционально: запуск с покрытием
if [ "$1" = "--cov" ]; then
    echo ""
    echo "📊 Запуск тестов с покрытием кода..."
    pytest apps/users/tests/test_user_models.py \
           apps/projects/tests/test_project_models.py \
           apps/applications/tests/test_application_models.py \
           apps/reports/tests/test_report_models.py \
           --cov=apps \
           --cov-report=html \
           --cov-report=term-missing
    
    echo ""
    echo "📈 HTML отчет о покрытии создан: htmlcov/index.html"
fi

echo ""
echo "🎉 Тестирование завершено!"
