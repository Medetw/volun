# 🚀 Quick Start Guide

## 🐳 Docker команды

### Базовые команды
```bash
# Запустить все сервисы
./start.sh

# Остановить все сервисы
./start.sh stop

# Перезапустить все сервисы
./start.sh restart

# Показать статус
./start.sh status

# Показать логи
./start.sh logs
```

### Разработка
```bash
# Режим разработки (с hot reload)
./start.sh dev

# Пересобрать образы
./start.sh build
```

### Продакшен
```bash
# Режим продакшен
./start.sh prod

# Очистить все
./start.sh clean
```

## 🌐 Доступ к сервисам

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/
- **Admin Panel**: http://localhost/admin/
- **Database**: localhost:5432
- **Redis**: localhost:6379

## 🔑 Данные для входа

**Admin пользователь:**
- Логин: `admin`
- Пароль: `admin123`

## 📋 Полезные команды

### Docker
```bash
# Показать все контейнеры
docker-compose ps

# Войти в бэкенд контейнер
docker-compose exec backend bash

# Войти в базу данных
docker-compose exec db psql -U postgres -d volunteering_platform

# Показать логи конкретного сервиса
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx
```

### Разработка
```bash
# Установить зависимости frontend
cd frontend && npm install

# Установить зависимости backend
cd backend && pip install -r requirements.txt

# Запустить миграции
docker-compose exec backend python manage.py migrate

# Создать суперпользователя
docker-compose exec backend python manage.py createsuperuser
```

## 🐛 Troubleshooting

### Проблемы с портами
```bash
# Остановить системный PostgreSQL
sudo systemctl stop postgresql

# Очистить Docker
docker system prune -a
```

### Проблемы с nginx
```bash
# Перезапустить nginx
docker-compose restart nginx

# Проверить конфигурацию
docker-compose exec nginx nginx -t
```

### База данных
```bash
# Полная очистка базы данных
./start.sh clean
./start.sh
```

## 📚 Документация

- `DOCKER.md` - Полная Docker документация
- `PROJECT_ANALYSIS.md` - Анализ проекта
- `.env.example` - Пример переменных окружения
