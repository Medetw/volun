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

#### Уведомления
```
GET    /api/notifications/            # Уведомления
POST   /api/notifications/mark_all_read/ # Прочитать все
GET    /api/notification-preferences/ # Волонтерская платформа

Современная платформа для соединения волонтеров с организациями, которые нуждаются в помощи.

## 🚀 Быстрый старт

### Требования
- Docker и Docker Compose
- Git

### Установка и запуск

```bash
# Клонировать репозиторий
git clone <repository-url>
cd volunteering-platform

# Запустить все сервисы
make dev

# Или вручную:
docker-compose up --build -d

# Проверить статус
make status
```

### Доступ к сервисам
- 🌐 **Фронтенд**: http://localhost/
- 🔧 **Backend API**: http://localhost/api/
- 🗄️ **База данных**: localhost:5432
- 📦 **Redis**: localhost:6379

## 📋 Команды управления

### Разработка
```bash
make dev      # Запустить с hot reload
make dev-up   # Запустить в фоне
make dev-down # Остановить
make dev-logs # Посмотреть логи
```

### Продакшен
```bash
make prod     # Собрать и запустить продакшен
make prod-up  # Запустить продакшен
make prod-down# Остановить продакшен
make prod-logs# Логи продакшена
```

### Утилиты
```bash
make build    # Собрать все образы
make clean    # Очистить Docker
make backup   # Бэкап БД
make deploy   # Деплой на продакшен
make status   # Статус сервисов
```

## 🏗️ Архитектура

### Технологический стек
- **Frontend**: Vue 3 + TypeScript + Tailwind CSS + Vite
- **Backend**: Django + Django REST Framework + Celery
- **База данных**: PostgreSQL 15
- **Кэш**: Redis 7
- **Прокси**: Nginx
- **Контейнеризация**: Docker + Docker Compose

### Структура проекта
```
volunteering-platform/
├── backend/                 # Django бэкенд
│   ├── apps/               # Django приложения
│   ├── config/             # Конфигурация Django
│   ├── Dockerfile.simple   # Dockerfile для бэкенда
│   └── requirements.txt    # Python зависимости
├── frontend/               # Vue.js фронтенд
│   ├── src/               # Исходный код Vue
│   ├── Dockerfile         # Dockerfile для фронтенда
│   └── nginx.conf         # Nginx конфигурация
├── nginx/                 # Nginx конфигурации
│   └── default.conf       # Reverse proxy конфиг
├── logs/                  # Логи приложений
├── backups/               # Бэкапы БД
├── docker-compose.yml     # Основная конфигурация
├── docker-compose.prod.yml # Продакшен конфигурация
├── Makefile              # Управляющие команды
├── .env.example          # Шаблон переменных окружения
└── README.md             # Этот файл
```

## 🔧 Конфигурация

### Переменные окружения
Скопируйте `.env.example` в `.env` и настройте:

```bash
cp .env.example .env
```

**Основные переменные:**
- `POSTGRES_PASSWORD` - пароль PostgreSQL
- `DJANGO_SECRET_KEY` - секретный ключ Django
- `DEBUG` - режим отладки (False для продакшена)
- `ALLOWED_HOSTS` - разрешенные хосты
- `CORS_ALLOWED_ORIGINS` - разрешенные origins для CORS

### Продакшен конфигурация
Для продакшена используется `docker-compose.prod.yml` с:
- 🔐 Улучшенной безопасностью
- 📊 Health checks для всех сервисов
- 💾 Отдельными volumes для продакшена
- 🚀 Оптимизированной конфигурацией

## 📝 API документация

### Endpoints
- `GET /api/` - Корень API
- `POST /api/auth/register/volunteer/` - Регистрация волонтера
- `POST /api/auth/register/organization/` - Регистрация организации
- `POST /api/auth/login/` - Вход
- `GET /api/projects/` - Список проектов
- `POST /api/projects/` - Создание проекта

### Аутентификация
Используется JWT токены. Заголовок:
```
Authorization: Bearer <token>
```

## 🚀 Деплой

### Автоматический деплой
```bash
make deploy
```

### Ручной деплой
```bash
# 1. Настроить .env для продакшена
cp .env.example .env
# редактировать .env с реальными значениями

# 2. Запустить продакшен
docker-compose -f docker-compose.prod.yml up -d --build

# 3. Выполнить миграции
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 4. Собрать статику
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

### SSL/HTTPS
Для настройки SSL:
```bash
# Установить certbot
sudo apt update && sudo apt install certbot python3-certbot-nginx

# Получить сертификаты
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🔍 Мониторинг

### Health checks
Все сервисы имеют health checks:
```bash
curl http://localhost/health
```

### Логи
```bash
# Все логи
docker-compose logs

# Конкретный сервис
docker-compose logs backend
docker-compose logs nginx
```

### Статус
```bash
docker-compose ps
```

## 🛠️ Разработка

### Локальная разработка бэкенда
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

### Локальная разработка фронтенда
```bash
cd frontend
npm install
npm run dev
```

### Миграции
```bash
# Создать миграцию
docker-compose exec backend python manage.py makemigrations

# Применить миграции
docker-compose exec backend python manage.py migrate
```

## 📦 Бэкапы

### Создать бэкап
```bash
make backup
```

### Восстановить бэкап
```bash
docker-compose exec db psql -U postgres -d volunteering < backup.sql
```

## 🐛 Траблшутинг

### Частые проблемы

1. **Порт занят**
   ```bash
   sudo systemctl stop postgresql  # Остановить системный PostgreSQL
   ```

2. **Permission denied**
   ```bash
   sudo chown -R $USER:$USER ./logs ./backups
   ```

3. **Контейнеры не стартуют**
   ```bash
   docker-compose down --volumes --remove-orphans
   docker system prune -a -f
   docker-compose up --build
   ```

4. **Vue Router 404 ошибки**
   - Убедитесь что `frontend/nginx.conf` содержит `try_files $uri $uri/ /index.html;`

## 📄 Лицензия

MIT License

## 🤝 Вклад

1. Fork проекта
2. Создать feature branch
3. Сделать коммиты
4. Push в branch
5. Создать Pull Request

---

**🎉 Спасибо за использование волонтерской платформы!**
