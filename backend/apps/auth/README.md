# Authentication API

Система аутентификации для волонтёрской платформы.

## Endpoints

### Регистрация

#### POST `/api/auth/register/volunteer/`
Регистрация волонтёра.

**Request Body:**
```json
{
  "email": "volunteer@example.com",
  "password": "secure_password123",
  "password_confirm": "secure_password123",
  "phone": "+1234567890",
  "first_name": "Иван",
  "last_name": "Иванов",
  "birth_date": "1990-01-01",
  "gender": "male",
  "city": "Москва",
  "region": "Московская область",
  "skills": ["IT", "Обучение"],
  "interests": ["Образование", "Экология"]
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "email": "volunteer@example.com",
    "role": "volunteer",
    "volunteer_profile": { ... }
  },
  "tokens": {
    "refresh": "...",
    "access": "..."
  }
}
```

#### POST `/api/auth/register/organization/`
Регистрация организации.

**Request Body:**
```json
{
  "email": "org@example.com",
  "password": "secure_password123",
  "password_confirm": "secure_password123",
  "phone": "+1234567890",
  "name": "Название организации",
  "organization_type": "ngo",
  "description": "Описание организации",
  "region": "Московская область",
  "contacts": {
    "website": "https://example.com",
    "social": "@example"
  }
}
```

**Response (201):** Аналогично регистрации волонтёра.

### Авторизация

#### POST `/api/auth/login/`
Вход в систему.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "user": { ... },
  "tokens": {
    "refresh": "...",
    "access": "..."
  }
}
```

#### POST `/api/auth/token/refresh/`
Обновление access токена.

**Request Body:**
```json
{
  "refresh": "refresh_token_here"
}
```

**Response (200):**
```json
{
  "access": "new_access_token"
}
```

### Профиль пользователя

#### GET `/api/auth/me/`
Получить текущий профиль пользователя.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "volunteer",
  "volunteer_profile": { ... }
}
```

#### PUT/PATCH `/api/auth/me/update/`
Обновить профиль пользователя.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (для волонтёра):**
```json
{
  "phone": "+1234567890",
  "first_name": "Новое имя",
  "city": "Санкт-Петербург",
  "skills": ["Новый навык"]
}
```

**Response (200):** Обновлённый профиль пользователя.

## Использование токенов

Все защищённые endpoints требуют заголовок:
```
Authorization: Bearer <access_token>
```

Access токен действителен 1 час, refresh токен - 7 дней.

## Ошибки

- `400` - Ошибка валидации данных
- `401` - Не авторизован (отсутствует или неверный токен)
