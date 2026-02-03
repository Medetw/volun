# 📚 Volunteering Platform API Documentation

## 🚀 Quick Start

### Base URL
```
Development: http://localhost:8001/api/
Production: https://your-domain.com/api/
```

### Authentication
All protected endpoints require JWT Bearer token:
```bash
Authorization: Bearer <your_access_token>
```

---

## 🔐 Authentication Endpoints

### Register Volunteer
```bash
curl -X POST http://localhost:8001/api/auth/register/volunteer/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "volunteer1",
    "email": "volunteer1@test.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Иван",
    "last_name": "Петров",
    "birth_date": "1990-05-15",
    "gender": "male",
    "city": "Алматы",
    "region": "Алматы",
    "skills": ["программирование", "дизайн"],
    "interests": ["образование", "экология"]
  }'
```

### Register Organization
```bash
curl -X POST http://localhost:8001/api/auth/register/organization/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "org1",
    "email": "org1@test.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "organization_name": "Благотворительный фонд 'Помощь'",
    "organization_type": "ngo",
    "description": "Помогаем нуждающимся",
    "city": "Алматы",
    "region": "Алматы",
    "contact_phone": "+7 777 123 4567",
    "contact_email": "contact@help-fund.kz"
  }'
```

### Login
```bash
curl -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "volunteer1@test.com",
    "password": "testpass123"
  }'
```

### Logout
```bash
curl -X POST http://localhost:8001/api/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

---

## 📋 Projects Endpoints

### Get All Projects
```bash
curl -X GET http://localhost:8001/api/projects/ \
  -H "Authorization: Bearer <token>"
```

### Create Project (Organization only)
```bash
curl -X POST http://localhost:8001/api/projects/ \
  -H "Authorization: Bearer <org_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Помощь животным",
    "description": "Помощь бездомным животным в приюте",
    "category_id": 1,
    "region_id": 1,
    "format": "offline",
    "start_date": "2024-03-01",
    "end_date": "2024-03-31",
    "volunteers_needed": 15,
    "requirements": "Любовь к животным",
    "contact_info": {
      "phone": "+7 777 123 4567",
      "email": "contact@shelter.kz"
    }
  }'
```

### Update Project Status
```bash
curl -X PATCH http://localhost:8001/api/projects/1/ \
  -H "Authorization: Bearer <org_token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

---

## 📝 Applications Endpoints

### Submit Application (Volunteer only)
```bash
curl -X POST http://localhost:8001/api/applications/ \
  -H "Authorization: Bearer <volunteer_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project": 1,
    "cover_letter": "Хочу помочь животным, имею опыт работы с ними",
    "hours_committed": 20
  }'
```

### Get My Applications
```bash
curl -X GET http://localhost:8001/api/applications/ \
  -H "Authorization: Bearer <volunteer_token>"
```

### Approve Application (Organization only)
```bash
curl -X POST http://localhost:8001/api/applications/1/approve/ \
  -H "Authorization: Bearer <org_token>"
```

### Reject Application (Organization only)
```bash
curl -X POST http://localhost:8001/api/applications/1/reject/ \
  -H "Authorization: Bearer <org_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "review_comment": "К сожалению, проект уже завершен"
  }'
```

---

## 📊 Statistics Endpoints

### Get Statistics
```bash
curl -X GET http://localhost:8001/api/statistics/ \
  -H "Authorization: Bearer <token>"
```

---

## 📰 News Endpoints

### Get All News
```bash
curl -X GET http://localhost:8001/api/news/ \
  -H "Authorization: Bearer <token>"
```

### Create News (Admin only)
```bash
curl -X POST http://localhost:8001/api/news/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Новый проект запущен!",
    "content": "Мы рады анонсировать запуск нового проекта...",
    "category": "announcement",
    "is_featured": true
  }'
```

---

## 🔔 Notifications Endpoints

### Get My Notifications
```bash
curl -X GET http://localhost:8001/api/notifications/ \
  -H "Authorization: Bearer <token>"
```

### Mark as Read
```bash
curl -X POST http://localhost:8001/api/notifications/1/mark-read/ \
  -H "Authorization: Bearer <token>"
```

---

## 📋 Reports Endpoints

### Create Project Report (Organization only)
```bash
curl -X POST http://localhost:8001/api/reports/ \
  -H "Authorization: Bearer <org_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project": 1,
    "title": "Отчет о проекте 'Помощь животным'",
    "description": "Проект успешно завершен...",
    "goals_achieved": "Все цели достигнуты, помогли 50 животным",
    "total_volunteers_participated": 12,
    "total_volunteer_hours": 240,
    "beneficiaries_count": 50
  }'
```

### Submit Report for Review
```bash
curl -X POST http://localhost:8001/api/reports/1/submit/ \
  -H "Authorization: Bearer <org_token>"
```

### Approve Report (Admin only)
```bash
curl -X POST http://localhost:8001/api/reports/1/approve/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "review_comment": "Отличная работа!"
  }'
```

---

## 👑 Admin Endpoints

### Get All Users
```bash
curl -X GET http://localhost:8001/api/admin/users/ \
  -H "Authorization: Bearer <admin_token>"
```

### Block User
```bash
curl -X POST http://localhost:8001/api/admin/users/5/block/ \
  -H "Authorization: Bearer <admin_token>"
```

### Unblock User
```bash
curl -X POST http://localhost:8001/api/admin/users/5/unblock/ \
  -H "Authorization: Bearer <admin_token>"
```

### Verify Organization
```bash
curl -X POST http://localhost:8001/api/admin/users/3/verify-organization/ \
  -H "Authorization: Bearer <admin_token>"
```

### Get User Statistics
```bash
curl -X GET http://localhost:8001/api/admin/users/stats/ \
  -H "Authorization: Bearer <admin_token>"
```

---

## 🧪 Test Data Setup

### Create Test Admin
```bash
curl -X POST http://localhost:8001/api/auth/register/organization/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@test.com",
    "password": "adminpass123",
    "password_confirm": "adminpass123",
    "organization_name": "Platform Administration",
    "organization_type": "government",
    "description": "Platform administrators",
    "city": "Астана",
    "region": "Астана"
  }'
# Then manually update role to 'admin' in database
```

### Test Categories & Regions
```bash
# Categories are created automatically via migrations
# Regions are created automatically via migrations
```

---

## 📝 Response Formats

### Success Response
```json
{
  "id": 1,
  "title": "Project Title",
  "description": "Project description",
  "status": "active",
  "created_at": "2024-02-03T14:30:00Z"
}
```

### Error Response
```json
{
  "error": "Error message description",
  "details": {
    "field_name": ["Error details"]
  }
}
```

### Rate Limit Error
```json
{
  "error": "Too many authentication attempts. Please try again later."
}
```

---

## 🔒 Rate Limiting

| Endpoint | Limit | Key |
|----------|-------|-----|
| Login/Register | 5/min | IP |
| Other Auth | 20/min | IP |
| Applications | 10/hour | User |
| Projects | 5/hour | User |
| General API | 100/min | IP |

---

## 🚨 Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid data |
| 401 | Unauthorized - No token or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

---

## 📚 Additional Resources

- **Swagger UI**: http://localhost:8001/api/docs/
- **OpenAPI Schema**: http://localhost:8001/api/schema/
- **Admin Panel**: http://localhost:8001/admin/

---

## 🛠️ Development Notes

1. **Environment Setup**: Make sure Redis is running for rate limiting
2. **Database**: PostgreSQL recommended for production
3. **Media Files**: Configure S3 or local storage for file uploads
4. **Email**: Configure SMTP settings for production email sending
5. **CORS**: Update allowed origins for frontend domain

---

## 📞 Support

For API issues and questions:
- Check the error messages carefully
- Verify authentication tokens
- Check rate limiting headers
- Review the documentation at `/api/docs/`

**Happy coding! 🚀**
