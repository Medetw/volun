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
- **Тестирование**: полная тестовая архитектура (pytest)

### 📊 Прогресс: **95%**

## 🛠 Технологический стек

- **Backend**: Django 4.2.10, DRF 3.14.0
- **База**: PostgreSQL + SQLite fallback
- **Кэш**: Redis 5.0.1
- **Очереди**: Celery 5.3.4
- **Аутентификация**: JWT (SimpleJWT)
- **Документация**: OpenAPI/Swagger
- **Тестирование**: pytest + factory_boy + coverage

## 🚀 Быстрый старт

### Вариант 1: Локальная разработка (рекомендуется)

```bash
# Клонируйте репозиторий
git clone https://github.com/Medetw/volun.git
cd volun

# Настройте backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Создайте .env файл (скопируйте с .env.example)
cp .env.example .env

# Примените миграции
python manage.py migrate

# Создайте суперпользователя (опционально)
python manage.py createsuperuser

# Запустите сервер
python manage.py runserver
```

### Вариант 2: С помощью тестового скрипта

```bash
cd backend
./run_all_tests.sh  # Запустит тесты и покажет статус
```

## 📦 Требования

### Системные:
- Python 3.12+
- PostgreSQL 15+ (для продакшена)
- Redis 7+ (для Celery и кэша)

### Python зависимости:
Смотрите `requirements.txt` для полного списка.

## 🧪 Тестирование

```bash
cd backend

# Запуск всех тестов
pytest apps/users/tests/test_user_models.py \
       apps/projects/tests/test_project_models.py \
       apps/applications/tests/test_application_models.py \
       apps/reports/tests/test_report_models.py

# С покрытием кода
pytest --cov=apps --cov-report=html

# Использование скриптов
./run_all_tests.sh          # Все тесты
./run_all_tests.sh --cov      # С покрытием
```

### 📊 Статистика тестирования:
- **Всего тестов**: 63
- **Покрытие кода**: ~90%
- **Приложения**: users, projects, applications, reports
- **Фреймворк**: pytest + pytest-django

## 📡 Документация API

После запуска сервера доступна по адресу:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Admin панель**: http://localhost:8000/admin/

## 🔧 Конфигурация

### Переменные окружения (.env):
```bash
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3  # или postgresql://...
REDIS_URL=redis://localhost:6379/0
```

## 🏗️ Структура проекта

```
volunteering-platform/
├── backend/                    # Django backend
│   ├── apps/                  # Приложения
│   │   ├── users/            # Пользователи и профили
│   │   ├── projects/         # Проекты и категории
│   │   ├── applications/     # Заявки на участие
│   │   ├── reports/          # Отчёты по проектам
│   │   ├── notifications/    # Уведомления
│   │   ├── statistics/       # Статистика
│   │   └── news/           # Новости
│   ├── config/               # Настройки Django
│   ├── requirements.txt       # Python зависимости
│   ├── manage.py            # Django management
│   └── pytest.ini           # pytest конфигурация
├── frontend/                  # Frontend (будет добавлен)
├── .github/workflows/         # GitHub Actions CI/CD
└── README.md                 # Этот файл
```

## 🔄 CI/CD

Проект настроен на GitHub Actions с автоматическим:
- Тестированием кода
- Проверкой качества кода
- Измерением покрытия
- Security проверками

## 🤝 Вклад в разработку

1. Fork проекта
2. Создайте feature ветку: `git checkout -b feature/amazing-feature`
3. Внесите изменения
4. Закоммитьте: `git commit -m 'Add amazing feature'`
5. Отправьте в репозиторий: `git push origin feature/amazing-feature`
6. Создайте Pull Request

## 📝 Лицензия

MIT License - можете свободно использовать в своих проектах.

---

**🎉 Готов к разработке и тестированию!**
