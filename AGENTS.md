# Volun Project — Agent Context

> Этот файл загружается автоматически при каждой сессии работы с Antigravity.
> Содержит ключевую архитектурную информацию и историю важных фиксов.

---

## 📦 Платформа: Volunteering Platform (Казахстан)

**Стек:** Django 4.x + DRF · Vue 3 (Vite) · PostgreSQL · Redis · Gunicorn

**Деплой:** [blitz.cloud](https://blitz.cloud) — **Docker-based, европейские датацентры**

---

## ☁️ Как работает blitz.cloud (важно знать)

- Подключается к **GitHub**, при каждом push в `main` — автоматически пересобирает и деплоит.
- Читает **Dockerfile** из корня репозитория (не `docker-compose.yml`!).
- **`docker-compose.yml` blitz.cloud НЕ использует** — он нужен только для локальной разработки.
- Запускает **один контейнер** (single service) — Celery и Celery-beat как отдельные сервисы невозможны.
- Переменную **`DATABASE_URL`** платформа подставляет сама при подключении managed database.
- Контейнеры запускаются **без root** (non-root, gVisor sandbox).
- Приложения **"засыпают"** после 30 мин без трафика (free tier).

### Free tier лимиты:
| Параметр | Лимит |
|---|---|
| Приложений | 5 |
| RAM | 512 MB |
| Storage | 10 GB |
| Managed Databases | 1 |
| Sleep timeout | 30 мин без трафика |

### Базы данных:
- PostgreSQL 17 / MariaDB / Redis (Valkey 8) — в один клик
- `DATABASE_URL` задаётся платформой автоматически
- Бэкап каждую ночь, хранится 7 дней

---

## 🐳 Текущая Docker-архитектура

**`Dockerfile`** — multi-stage:
```
Stage 1: node:20-slim       → npm ci && npm run build (Vue → /frontend/dist)
Stage 2: python:3.12-slim   → pip install, копирует backend + frontend_dist
```

**`backend/entrypoint.sh`** — выполняется при каждом старте контейнера:
```
1. Ждёт PostgreSQL (socket check)
2. python manage.py migrate
3. python manage.py collectstatic
4. python manage.py createsuperuser --noinput || true  ← если заданы DJANGO_SUPERUSER_*
5. python manage.py create_test_accounts  ← если DJANGO_CREATE_TEST_ACCOUNTS=1 (по умолч.)
6. exec gunicorn (1 worker, 4 threads, timeout 120)
```

> Чтобы отключить авто-создание тестовых аккаунтов на проде:
> задать переменную окружения `DJANGO_CREATE_TEST_ACCOUNTS=0` в blitz.cloud.

**`docker-compose.yml`** — используется **только** blitz.cloud как референс конфига,
но сам платформа его не исполняет — он нужен для документирования переменных окружения.

**`docker-compose.dev.yml`** — локальная разработка (Postgres + Redis + Celery).

---

## 🔑 Роли пользователей (RBAC)

| Роль | `UserRole` | Описание |
|---|---|---|
| `admin` | `UserRole.ADMIN` | Полный доступ, `is_staff=True`, `is_superuser=True` |
| `moderator` | `UserRole.MODERATOR` | RBAC через `ModeratorProfile` (can_view_volunteers, can_manage_hours, can_manage_certificates) |
| `organization` | `UserRole.ORGANIZATION` | Создаёт проекты, управляет заявками |
| `volunteer` | `UserRole.VOLUNTEER` | Подаёт заявки на проекты |

**Тестовые аккаунты** (создаются автоматически через `entrypoint.sh` при старте):

| Роль | Email (логин) | Password |
|---|---|---|
| admin | `test_admin@volun.test` | `Admin@12345` |
| moderator (full) | `test_moderator@volun.test` | `Mod@12345` |
| moderator (limited) | `test_mod_limited@volun.test` | `Mod@12345` |
| organization | `test_org@volun.test` | `Org@12345` |
| volunteer | `test_volunteer@volun.test` | `Vol@12345` |
| volunteer | `test_volunteer2@volun.test` | `Vol@12345` |

> ⚠️ Логин на сайте — **по email** (не username). Username = email (так работает LoginSerializer).
> Команда: `python manage.py create_test_accounts` — идемпотентна.
> `--reset` — удалить и пересоздать.
> Управление через env var: `DJANGO_CREATE_TEST_ACCOUNTS=0` отключает авто-создание.

---

## 🔧 История важных фиксов (хронология, Oct 2026)

### ✅ [Oct 20] Celery / Celery-beat — убраны, blitz.cloud = 1 контейнер

**Проблема:** Пытались добавить отдельные сервисы `celery` и `celery-beat`.
Blitz.cloud запускает **один контейнер** — остальные сервисы игнорируются.

**Решение:** Celery/Celery-beat убраны. Уведомления переключены на синхронное
выполнение / `CELERY_TASK_ALWAYS_EAGER=True`.

**Если нужен Celery в будущем** → апгрейд на платный blitz.cloud tier
или переезд на Render / Railway / Fly.io (там multi-service поддерживается).

---

### ✅ [Oct 20] Redis — fallback на LocMemCache

**Проблема:** При отсутствии `REDIS_URL` Django падал с 500.

**Решение:** В `settings.py`:
```python
if REDIS_URL:
    CACHES = { "default": { "BACKEND": "django_redis.cache.RedisCache", ... } }
else:
    CACHES = { "default": { "BACKEND": "django.core.cache.backends.locmem.LocMemCache" } }
```

---

### ✅ [Oct 20] Статика / Vue assets — раздача через Django + WhiteNoise

**Проблема:** Vue assets (`/assets/`) не находились после `collectstatic` без Nginx.

**Решение:** WhiteNoise + Django URL route для `/assets/`.
`VITE_API_BASE_URL=/api` прописан в Dockerfile на этапе сборки фронтенда.

---

### ✅ [Oct 21] Тестовые аккаунты — авто-создание через entrypoint.sh

**Проблема:** На blitz.cloud нет SSH-доступа для ручного запуска management commands.

**Решение:** `create_test_accounts` добавлен в `entrypoint.sh` — выполняется
при каждом старте контейнера. Команда идемпотентна. Управляется через
`DJANGO_CREATE_TEST_ACCOUNTS` env var (default=1).

---

## 📁 Ключевые файлы проекта

| Файл | Назначение |
|---|---|
| `Dockerfile` | **Multi-stage build: Vue → Django** — читается blitz.cloud |
| `docker-compose.yml` | Документация env vars для blitz.cloud (не исполняется платформой) |
| `docker-compose.dev.yml` | Локальная разработка (Celery, Redis, Postgres) |
| `backend/entrypoint.sh` | Startup: wait-pg → migrate → collectstatic → test_accounts → gunicorn |
| `backend/config/settings.py` | Django settings (DATABASE_URL, Redis fallback) |
| `backend/apps/users/management/commands/create_test_accounts.py` | Seed test accounts |
| `backend/apps/tests/factories.py` | Factory Boy factories для тестов |
| `backend/conftest.py` | Pytest fixtures (все роли покрыты, включая moderator) |

---

## 🚀 Локальный запуск (dev)

```bash
cd backend
test_env/bin/python3 manage.py migrate
test_env/bin/python3 manage.py create_test_accounts
test_env/bin/python3 manage.py runserver
```

> Python-окружение: `backend/test_env/` (не `venv/` — она под Windows)
