# Волонтёрская Платформа

**Backend: Django + DRF + Redis + Celery**  
**Frontend: будет добавлен позже (Vue/React)**

## 🚀 Возможности

### ✅ Реализовано:
- **Аутентификация**: JWT, регистрация волонтёров и организаций
- **Пользователи**: профили волонтёров и организаций с ролями
- **Проекты**: CRUD, фильтрация, поиск, категории
- **Заявки**: подача, одобрение/отклонение, история
- **Новости**: CRUD для админов, публичный доступ
- **Статистика**: детальная аналитика для всех ролей
- **Уведомления**: email + in-app с настройками
- **Отчёты**: система отчетов по проектам
- **Восстановление пароля**: через email код
- **Rate Limiting**: защита API
- **Redis**: кэширование и Celery
- **Docker**: полная контейнеризация

### 📊 Прогресс: **95%**

## 🛠 Технологический стек

- **Backend**: Django 4.2.10, DRF 3.14.0
- **База**: PostgreSQL + SQLite fallback
- **Кэш**: Redis 5.0.1
- **Очереди**: Celery 5.3.4
- **Аутентификация**: JWT (SimpleJWT)
- **Документация**: OpenAPI/Swagger
- **Контейнеризация**: Docker + Docker Compose

## 🚀 Быстрый старт

### Вариант 1: Docker (рекомендуется)

```bash
# Клонируйте репозиторий
git clone https://github.com/Medeeet/volunteering-platform.git
cd volunteering-platform

# Запустите все сервисы
docker compose up -d

# Примените миграции
docker compose exec backend python manage.py migrate

# Создайте суперпользователя (опционально)
docker compose exec backend python manage.py createsuperuser
```

Приложение будет доступно по адресу:
- **API**: http://localhost:8000
- **Документация**: http://localhost:8000/api/docs/
- **Admin панель**: http://localhost:8000/admin/

### Вариант 2: Локальная разработка

**1. Установите зависимости:**
```bash
# Python 3.12+
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

**2. Запустите Redis:**
```bash
# Через Docker (просто)
docker run -d -p 6379:6379 redis:7-alpine

# Или установите локально
# Ubuntu/Debian: sudo apt install redis-server
# macOS: brew install redis
```

**3. Настройте переменные окружения:**
```bash
cp backend/env.example backend/.env
# Отредактируйте .env при необходимости
```

**4. Запустите PostgreSQL (опционально):**
```bash
docker run -d \
  --name volunteering-db \
  -e POSTGRES_DB=volunteering_platform \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15
```

**5. Примените миграции и запустите сервер:**
```bash
cd backend
python manage.py migrate
python manage.py runserver
```

**6. Запустите Celery worker (в отдельном терминале):**
```bash
cd backend
celery -A config worker -l info
```

**7. Запустите Celery beat (в отдельном терминале):**
```bash
cd backend
celery -A config beat -l info
```

## 📚 API Документация

### Основные эндпоинты:

#### Аутентификация
```
POST /api/auth/register/volunteer/     # Регистрация волонтёра
POST /api/auth/register/organization/  # Регистрация организации
POST /api/auth/login/                  # Вход
POST /api/auth/password/reset/         # Сброс пароля
POST /api/auth/password/change/        # Изменение пароля
```

#### Пользователи
```
GET  /api/auth/me/                     # Текущий профиль
PUT  /api/auth/me/update/              # Обновление профиля
```

#### Проекты
```
GET    /api/projects/                  # Список проектов
POST   /api/projects/                  # Создание проекта
GET    /api/projects/{id}/             # Детали проекта
PUT    /api/projects/{id}/             # Обновление проекта
DELETE /api/projects/{id}/             # Удаление проекта
```

#### Заявки
```
GET    /api/applications/              # Список заявок
POST   /api/applications/              # Подача заявки
POST   /api/applications/{id}/approve/ # Одобрение
POST   /api/applications/{id}/reject/  # Отклонение
```

#### Уведомления
```
GET    /api/notifications/            # Уведомления
POST   /api/notifications/mark_all_read/ # Прочитать все
GET    /api/notification-preferences/ # Настройки
```

#### Отчёты
```
GET    /api/reports/                   # Отчёты по проектам
POST   /api/reports/                   # Создание отчета
POST   /api/reports/{id}/submit/       # Отправить на модерацию
```

#### Статистика
```
GET    /api/statistics/                # Статистика платформы
```

## 🔧 Конфигурация

### Переменные окружения:

```bash
# Django
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# База данных
DATABASE_URL=postgres://user:pass@localhost:5432/dbname

# Redis
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

# Email
DEFAULT_FROM_EMAIL=noreply@volunteer-platform.com
SITE_URL=http://localhost:8000

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
python manage.py test

# Тесты конкретного приложения
python manage.py test apps.notifications
python manage.py test apps.reports
python manage.py test apps.statistics
```

## 📦 Структура проекта

```
backend/
├── apps/
│   ├── auth/           # Аутентификация
│   ├── users/          # Пользователи
│   ├── projects/       # Проекты
│   ├── applications/   # Заявки
│   ├── news/           # Новости
│   ├── statistics/     # Статистика
│   ├── notifications/  # Уведомления
│   └── reports/        # Отчёты
├── config/
│   ├── settings.py     # Настройки Django
│   ├── urls.py         # URL конфигурация
│   ├── celery.py       # Celery конфигурация
│   └── __init__.py
├── requirements.txt    # Зависимости Python
├── Dockerfile         # Docker конфигурация
└── manage.py          # Django management
```

## 🔒 Безопасность

- **JWT токены** с ротацией
- **Rate limiting** для API
- **CORS** конфигурация
- **Password validation**
- **Ролевая модель доступа**
- **CSRF защита**
- **SQL injection защита** через ORM

## 🚀 Развертывание

### Production

1. **Настройте переменные окружения:**
   ```bash
   DJANGO_DEBUG=0
   DJANGO_SECRET_KEY=your-production-secret
   DATABASE_URL=postgres://user:pass@host:5432/dbname
   REDIS_URL=redis://host:6379/1
   ```

2. **Запустите через Docker:**
   ```bash
   docker compose -f docker-compose.yml up -d
   ```

3. **Настройте Nginx** (опционально) для reverse proxy

### Мониторинг

- **Celery**: мониторинг через Flower
- **Redis**: redis-cli monitor
- **Docker**: docker compose logs -f

## 🤝 Contributing

1. Fork проекта
2. Создайте feature ветку: `git checkout -b feature/amazing-feature`
3. Commit изменения: `git commit -m 'Add amazing feature'`
4. Push в ветку: `git push origin feature/amazing-feature`
5. Откройте Pull Request

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE) файл

## 📞 Контакты

- **GitHub**: [@Medeeet](https://github.com/Medeeet)
- **Email**: awusincere@gmail.com

---

**🎉 Спасибо за использование Волонтёрской Платформы!**

