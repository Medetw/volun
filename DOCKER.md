# 🐳 Docker Guide for Volunteering Platform

Простая и понятная инструкция по запуску проекта с помощью Docker.

## 🚀 Быстрый старт

### 1. Запуск всех сервисов
```bash
./start.sh
```
Эта команда запустит все сервисы:
- 🌐 Frontend (Vue.js) - http://localhost
- 🔧 Backend API (Django) - http://localhost/api/
- 🗄️ Database (PostgreSQL) - localhost:5432
- 📦 Cache (Redis) - localhost:6379

### 2. Проверка статуса
```bash
./start.sh status
```

### 3. Просмотр логов
```bash
./start.sh logs
```

### 4. Остановка всех сервисов
```bash
./start.sh stop
```

## 📋 Все команды

| Команда | Описание |
|---------|----------|
| `./start.sh` | Запустить все сервисы (по умолчанию) |
| `./start.sh start` | Запустить все сервисы |
| `./start.sh stop` | Остановить все сервисы |
| `./start.sh restart` | Перезапустить все сервисы |
| `./start.sh build` | Собрать Docker образы |
| `./start.sh logs` | Показать логи всех сервисов |
| `./start.sh status` | Показать статус контейнеров |
| `./start.sh clean` | Удалить все контейнеры и volumes |
| `./start.sh dev` | Запустить в режиме разработки |
| `./start.sh prod` | Запустить в режиме продакшена |
| `./start.sh help` | Показать справку |

## 🔧 Режимы работы

### Разработка (Development)
```bash
./start.sh dev
```
- Включен hot reload для бэкенда
- Открыты порты для прямого доступа к сервисам
- Django в режиме отладки
- Монтирование кода для мгновенных изменений

### Продакшен (Production)
```bash
./start.sh prod
```
- Оптимизированная конфигурация
- SSL поддержка
- Без режимов отладки
- Требуется файл `.env` с настройками

## 📁 Структура Docker файлов

- `docker-compose.yml` - Основная конфигурация
- `docker-compose.dev.yml` - Конфигурация для разработки
- `docker-compose.prod.yml` - Конфигурация для продакшена
- `start.sh` - Скрипт для управления проектом
- `.env.example` - Пример переменных окружения

## 🛠️ Устранение проблем

### Проблема: "Port already in use"
```bash
# Найти кто использует порт
sudo lsof -i :80
sudo lsof -i :8000

# Остановить сервисы
./start.sh stop
# Или очистить все
./start.sh clean
```

### Проблема: "Permission denied"
```bash
# Сделать скрипт исполняемым
chmod +x start.sh
```

### Проблема: "Out of memory"
```bash
# Очистить Docker
docker system prune -a
```

### Проблема: База данных не запускается
```bash
# Полная очистка и перезапуск
./start.sh clean
./start.sh
```

## 🔐 Настройка продакшена

1. Скопируйте файл окружения:
```bash
cp .env.example .env
```

2. Отредактируйте `.env` файл:
```bash
nano .env
```

3. Запустите в продакшен режиме:
```bash
./start.sh prod
```

## 📊 Мониторинг

### Просмотр логов конкретного сервиса
```bash
# Бэкенд
docker-compose logs -f backend

# Фронтенд
docker-compose logs -f frontend

# База данных
docker-compose logs -f db
```

### Статистика ресурсов
```bash
docker stats
```

### Вход в контейнер
```bash
# Бэкенд
docker-compose exec backend bash

# База данных
docker-compose exec db psql -U postgres -d volunteering_platform
```

## 🔄 Обновление проекта

При изменении кода:
```bash
# Пересобрать и запустить
./start.sh restart

# Или только пересобрать образы
./start.sh build
```

## 💡 Советы

1. **Первый запуск**: Всегда используйте `./start.sh clean` перед первым запуском на новой машине
2. **Разработка**: Используйте `./start.sh dev` для удобной разработки
3. **Продакшен**: Всегда настраивайте `.env` файл для продакшена
4. **Логи**: Используйте `./start.sh logs` для отладки проблем
5. **Чистка**: Регулярно используйте `docker system prune -a` для освобождения места

## 🆘 Помощь

Если что-то не работает:
1. Проверьте статус: `./start.sh status`
2. Посмотрите логи: `./start.sh logs`
3. Попробуйте полную очистку: `./start.sh clean`
4. Перезапустите: `./start.sh`

Для дополнительной информации:
```bash
./start.sh help
```
