# Projects API

API для управления проектами волонтёрской платформы.

## Endpoints

### Категории и регионы

#### GET `/api/categories/`
Получить список всех категорий проектов.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Образование",
    "description": "Проекты в сфере образования",
    "created_at": "2026-01-22T10:00:00Z"
  }
]
```

#### GET `/api/regions/`
Получить список всех регионов.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Московская область",
    "code": "MO",
    "created_at": "2026-01-22T10:00:00Z"
  }
]
```

### Проекты

#### GET `/api/projects/`
Получить список проектов с фильтрацией и поиском.

**Query Parameters:**
- `status` - фильтр по статусу (draft, active, completed, cancelled)
- `category` - фильтр по категории (ID)
- `region` - фильтр по региону (ID)
- `format` - фильтр по формату (online, offline, hybrid)
- `search` - поиск по названию и описанию
- `ordering` - сортировка (created_at, start_date, volunteers_needed)
- `page` - номер страницы (пагинация)

**Пример:**
```
GET /api/projects/?status=active&category=1&format=offline&search=образование
```

**Response (200):**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/projects/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Обучение детей программированию",
      "description": "Краткое описание...",
      "category": {"id": 1, "name": "Образование"},
      "format": "offline",
      "region": {"id": 1, "name": "Москва"},
      "start_date": "2026-02-01",
      "end_date": "2026-02-28",
      "volunteers_needed": 5,
      "status": "active",
      "organization_name": "НКО Образование",
      "volunteers_count": 2,
      "volunteers_remaining": 3,
      "created_at": "2026-01-22T10:00:00Z"
    }
  ]
}
```

#### GET `/api/projects/{id}/`
Получить детальную информацию о проекте.

**Response (200):**
```json
{
  "id": 1,
  "title": "Обучение детей программированию",
  "description": "Полное описание проекта...",
  "category": {...},
  "format": "offline",
  "region": {...},
  "start_date": "2026-02-01",
  "end_date": "2026-02-28",
  "volunteers_needed": 5,
  "status": "active",
  "organization": {
    "id": 2,
    "name": "НКО Образование",
    "organization_type": "ngo",
    "is_verified": true
  },
  "volunteers_count": 2,
  "volunteers_remaining": 3,
  "created_at": "2026-01-22T10:00:00Z",
  "updated_at": "2026-01-22T10:00:00Z",
  "image": "http://localhost:8000/media/projects/image.jpg",
  "requirements": "Требования к волонтёрам...",
  "contact_info": {"phone": "+1234567890"}
}
```

#### POST `/api/projects/`
Создать новый проект (только для организаций).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Название проекта",
  "description": "Описание проекта",
  "category_id": 1,
  "format": "offline",
  "region_id": 1,
  "start_date": "2026-02-01",
  "end_date": "2026-02-28",
  "volunteers_needed": 5,
  "status": "draft",
  "requirements": "Требования к волонтёрам",
  "contact_info": {"phone": "+1234567890"}
}
```

**Response (201):** Детальная информация о созданном проекте.

#### PUT/PATCH `/api/projects/{id}/`
Обновить проект (только владелец).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:** Аналогично созданию (все поля опциональны для PATCH).

**Response (200):** Обновлённая информация о проекте.

#### DELETE `/api/projects/{id}/`
Удалить проект (только владелец).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204):** No content.

#### GET `/api/projects/my/`
Получить список проектов текущей организации.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):** Список проектов организации.

## Permissions

- **Просмотр проектов**: Доступно всем (включая неавторизованных)
- **Создание проектов**: Только для организаций
- **Редактирование/Удаление**: Только владелец проекта

## Статусы проектов

- `draft` - Черновик (виден только организации)
- `active` - Активный (виден всем)
- `completed` - Завершён
- `cancelled` - Отменён

## Форматы проектов

- `online` - Онлайн
- `offline` - Офлайн
- `hybrid` - Гибридный

## Фильтрация

По умолчанию:
- Неавторизованные пользователи видят только активные проекты
- Авторизованные волонтёры видят активные и черновики
- Организации видят все проекты (свои + активные других)
