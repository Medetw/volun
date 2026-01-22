## Volunteering Platform

Backend: **Django + DRF**  
Frontend: will be added later (Vue/React).

### Quick start (backend)

- **Create env file**:
  - Copy `backend/env.example` to `backend/.env` (locally).

- **Run Postgres** (optional but recommended):

```bash
docker compose up -d
```

- **Install deps**:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
```

- **Run migrations + server**:

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

### API docs

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

