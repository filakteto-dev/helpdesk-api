# Helpdesk API

Backend API for a support ticket system.

## Tech stack
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- Pytest

## Local run
1. Start database:
   docker compose up -d

2. Install dependencies:
   pip install -r requirements.txt

3. Run app:
   uvicorn app.main:app --reload