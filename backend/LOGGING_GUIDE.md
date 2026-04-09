# 📝 Руководство по логированию волонтерской платформы

## 🎯 **Обзор**

Система логирования настроена для централизованного сбора всех событий в один файл с автоматической ротацией.

## 📁 **Структура логов**

```
backend/logs/
├── volunteering_platform.log  # Основной лог файл (все события)
├── errors.log                 # Только ошибки
└── .gitignore                 # Игнорировать лог файлы в Git
```

## 🔧 **Конфигурация**

### **Основные настройки:**
- **Файл:** `logs/volunteering_platform.log`
- **Макс. размер:** 10MB (автоматическая ротация)
- **Бэкапы:** 5 предыдущих файлов
- **Кодировка:** UTF-8
- **Формат:** `2024-02-18 15:30:45 [INFO] [apps.auth.views] Login attempt`

### **Уровни логирования:**
- **DEBUG:** Детальная отладочная информация
- **INFO:** Общая информация о работе системы
- **WARNING:** Предупреждения и проблемы
- **ERROR:** Ошибки и исключения

## 🛠 **Использование**

### **1. Просмотр логов в реальном времени:**

```bash
# Показать последние 50 строк
python view_logs.py

# Показать последние 100 строк
python view_logs.py --tail 100

# Показать только ошибки
python view_logs.py --type errors

# Показать статистику логов
python view_logs.py --stats
```

### **2. Поиск по логам:**

```bash
# Поиск по ключевому слову
python view_logs.py --search "LOGIN_SUCCESS"

# Поиск в конкретном типе логов
python view_logs.py --search "ERROR" --type errors

# Поиск с ограничением результатов
python view_logs.py --search "volunteer" --tail 20
```

### **3. Прямой доступ к файлам:**

```bash
# Просмотр основного лога
tail -f logs/volunteering_platform.log

# Просмотр ошибок
tail -f logs/errors.log

# Поиск с grep
grep "LOGIN_SUCCESS" logs/volunteering_platform.log
```

## 💻 **Использование в коде**

### **1. Базовое логирование:**

```python
from apps.core.logging import logger

# Информационное сообщение
logger.info("Пользователь успешно зарегистрирован")

# Отладочное сообщение
logger.debug("Обработка запроса к API")

# Предупреждение
logger.warning("Проблема с валидацией данных")

# Ошибка с исключением
logger.error("Ошибка базы данных", exception=e)
```

### **2. Специализированные методы:**

```python
from apps.core.logging import logger, security_logger

# Логирование API запросов
logger.api_request(
    method="POST",
    endpoint="/api/auth/login/",
    user_id=123,
    status_code=200,
    duration=0.123
)

# Логирование действий пользователя
logger.user_action(
    action="PROJECT_CREATED",
    user_id=123,
    details={"project_id": 456, "title": "Новый проект"}
)

# Логирование системных событий
logger.system_event(
    event="DATABASE_BACKUP_COMPLETED",
    details={"size": "1.2GB", "duration": "45s"}
)

# Логирование событий безопасности
security_logger.security_event(
    event="LOGIN_FAILED",
    user_id=None,
    ip_address="192.168.1.100",
    details={"username": "admin@test.com"}
)
```

### **3. Декоратор для API:**

```python
from apps.core.logging import log_api_request

@log_api_request
def my_api_view(request):
    # Ваш код
    pass
```

## 📊 **Типы логируемых событий**

### **🔐 Аутентификация:**
- `LOGIN_SUCCESS` - успешный вход
- `LOGIN_FAILED` - неудачная попытка входа
- `LOGOUT` - выход пользователя
- `VOLUNTEER_REGISTERED` - регистрация волонтера
- `ORGANIZATION_REGISTERED` - регистрация организации

### **👤 Действия пользователя:**
- `PROJECT_CREATED` - создание проекта
- `APPLICATION_SUBMITTED` - подача заявки
- `APPLICATION_APPROVED` - одобрение заявки
- `PROFILE_UPDATED` - обновление профиля

### **🛡️ Безопасность:**
- `PERMISSION_DENIED` - отказ в доступе
- `RATE_LIMIT_EXCEEDED` - превышение лимита запросов
- `SUSPICIOUS_ACTIVITY` - подозрительная активность

### **🔧 Системные события:**
- `DATABASE_BACKUP_COMPLETED` - бэкап завершен
- `CACHE_CLEARED` - кэш очищен
- `EMAIL_SENT` - email отправлен

## 🔍 **Примеры логов**

### **Успешный вход:**
```
2024-02-18 15:30:45 [INFO] [apps.auth.views] Login attempt for user@test.com from 192.168.1.100
2024-02-18 15:30:45 [INFO] [apps.auth.views] User Action: LOGIN_SUCCESS | User: 123 | Details: {'email': 'user@test.com', 'role': 'volunteer'}
```

### **Ошибка API:**
```
2024-02-18 15:31:20 [ERROR] [apps.projects.views] API request failed: POST /api/projects/projects/
Exception: IntegrityError at /api/projects/projects/
UNIQUE constraint failed: projects_project.title
Traceback: [полный traceback]
```

### **Событие безопасности:**
```
2024-02-18 15:32:10 [WARNING] [apps.security] SECURITY: LOGIN_FAILED | IP: 192.168.1.100 | Details: {'username': 'admin@test.com'}
```

## 🚀 **Советы по использованию**

### **1. Для разработки:**
- Используйте `DEBUG` уровень для детальной информации
- Следите за логами в реальном времени: `tail -f logs/volunteering_platform.log`

### **2. Для продакшена:**
- Мониторьте `ERROR` логи: `python view_logs.py --type errors`
- Настраивайте алерты на критические события
- Регулярно проверяйте логи безопасности

### **3. Для отладки:**
- Используйте поиск по ID пользователя: `python view_logs.py --search "user_id:123"`
- Фильтруйте по временным интервалам
- Анализируйте последовательность событий

## 📈 **Мониторинг**

### **Ключевые метрики:**
- Количество успешных входов
- Количество ошибок API
- Время ответа сервера
- Подозрительные активности

### **Автоматизация:**
```bash
# Скрипт для ежедневной проверки ошибок
#!/bin/bash
ERROR_COUNT=$(python view_logs.py --search "ERROR" --type errors | wc -l)
if [ $ERROR_COUNT -gt 10 ]; then
    echo "ВНИМАНИЕ: Обнаружено $ERROR_COUNT ошибок за сегодня"
fi
```

## 🔄 **Ротация логов**

Логи автоматически ротируются при достижении 10MB:
- `volunteering_platform.log` - текущий файл
- `volunteering_platform.log.1` - предыдущий
- `volunteering_platform.log.2` - и т.д. до 5 файлов

---

**🎯 Теперь все логи вашего друга будут сохраняться в одном файле с удобным доступом!**
