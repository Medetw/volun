# Backend Docker Deployment

## 🚀 Быстрый запуск

### Запуск только бэкенда с базами данных:
```bash
cd backend
docker-compose up -d
```

### Что будет запущено:
- ✅ **PostgreSQL 15** - база данных (порт 5432)
- ✅ **Redis 7** - кэш и брокер сообщений (порт 6379)  
- ✅ **Django Backend** - API сервер (порт 8000)
- ✅ **Celery Worker** - фоновые задачи
- ✅ **Celery Beat** - планировщик задач

## 📋 Доступ после запуска

### API эндпоинты:
- **API:** http://localhost:8000/api/
- **Документация:** http://localhost:8000/api/docs/
- **Админ панель:** http://localhost:8000/admin/

### Тестовые пользователи:
- **Админ:** admin@example.com / admin123
- **Организация:** org@test.com / testpass123
- **Волонтер:** volunteer@test.com / testpass123

## 🛠️ Управление

### Просмотр логов:
```bash
docker-compose logs -f backend
```

### Перезапуск:
```bash
docker-compose restart backend
```

### Остановка:
```bash
docker-compose down
```

### Полная очистка:
```bash
docker-compose down -v
```

## 📁 Структура

```
backend/
├── Dockerfile              # Конфигурация контейнера Django
├── docker-compose.yml      # Все сервисы бэкенда
├── config/settings/docker.py # Настройки для Docker
└── apps/projects/management/commands/create_initial_data.py
    # Создание начальных данных
```

## 🔧 Особенности

- **Автоматические миграции** при запуске
- **Создание начальных данных** (пользователи, категории, регионы)
- **Health checks** для всех сервисов
- **Non-root пользователь** для безопасности
- **Логирование** в файлы и консоль
- **Volume для медиа** и статических файлов

## 🌐 Подключение к другим сервисам

Для подключения к этому бэкенду из других проектов:
```
API URL: http://localhost:8000/api/
DB: postgresql://postgres:postgres@localhost:5432/volunteering_db
Redis: redis://localhost:6379/0
```
