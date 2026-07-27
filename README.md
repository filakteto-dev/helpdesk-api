# Helpdesk API

Backend API for a support ticket system.

## Overview

Helpdesk API is a backend project built with FastAPI and PostgreSQL. It provides user registration, JWT authentication, ticket creation, ticket listing, ticket detail view, and role-based ticket status updates for support/admin users.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- JWT authentication
- Docker / Docker Compose

## Features

- User registration
- User login with JWT access tokens
- Current user endpoint
- Ticket creation by authenticated users
- List current user's tickets
- Get ticket details with ownership check
- Update ticket status for support/admin roles
- PostgreSQL schema migrations with Alembic
- Docker-based PostgreSQL setup

## Architecture

The project uses a layered structure:

- endpoints handle HTTP requests and responses
- schemas define request and response validation
- services contain business logic
- repositories handle database operations
- models define SQLAlchemy ORM entities
- migrations track database schema changes

## Project Structure

```text
app/
├── api/
│   └── v1/
│       └── endpoints/
│           ├── auth.py
│           └── tickets.py
├── core/
│   ├── config.py
│   └── security.py
├── db/
│   ├── base.py
│   └── session.py
├── dependencies/
│   └── auth.py
├── models/
│   ├── user.py
│   └── ticket.py
├── repositories/
│   ├── user_repository.py
│   └── ticket_repository.py
├── schemas/
│   ├── auth.py
│   ├── user.py
│   └── ticket.py
├── services/
│   ├── auth_service.py
│   └── ticket_service.py
└── main.py

alembic/
└── versions/

docker-compose.yml
requirements.txt
.env.example
README.md
```

The application follows a layered architecture. Endpoints handle HTTP requests and delegate business logic to services. Services use repositories for database access. SQLAlchemy models describe database tables, while Pydantic schemas define request and response validation.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Filakteto-dev/helpdesk-api
cd helpdesk-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create environment file

```bash
cp .env.example .env
```

### 5. Start PostgreSQL

```bash
docker compose up -d
```

### 6. Apply database migrations

```bash
alembic upgrade head
```

### 7. Run the API

```bash
uvicorn app.main:app --reload
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Environment Variables

Create a `.env` file based on `.env.example`.

```env
APP_NAME=Helpdesk API
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/helpdesk
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Do not commit real secrets to Git.

## Database Migrations

Create a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback the last migration:

```bash
alembic downgrade -1
```

Check the current migration:

```bash
alembic current
```

## API Endpoints

### Auth

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Log in and receive a JWT access token |
| GET | `/auth/me` | Get the current authenticated user |

### Tickets

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| POST | `/tickets/` | Create a ticket |
| GET | `/tickets/` | List tickets created by the current user |
| GET | `/tickets/{ticket_id}` | Get a ticket by id |
| PATCH | `/tickets/{ticket_id}/status` | Update ticket status, available for support/admin users |

## Example Flow

1. Register a new user with `/auth/register`.
2. Click the **Authorize** button in Swagger.
3. Enter the user's email into the `username` field and the password into the `password` field.

> Note: Swagger uses the standard OAuth2 `username` field for login. In this project, the user's email is used as the login identifier, so the email should be entered into the `username` field.

4. Swagger sends a login request to `/auth/login` and stores the returned JWT token automatically.
5. Create a ticket with `/tickets/`.
6. Get the list of current user's tickets with `/tickets/`.
7. Get a single ticket by id with `/tickets/{ticket_id}`.
8. Log in as a support/admin user using the **Authorize** button.
9. Update ticket status with `/tickets/{ticket_id}/status`.

Example ticket status update request:

```json
{
  "status": "in_progress"
}
```

Available ticket statuses:

```text
open
in_progress
resolved
closed
```
Example ticket status update request:

```json
{
  "status": "in_progress"
}
```

Available ticket statuses:

```text
open
in_progress
resolved
closed
```

## What I Practiced

- Building REST API endpoints with FastAPI
- Working with request and response schemas using Pydantic v2
- Implementing JWT-based authentication
- Protecting endpoints with authenticated user dependencies
- Designing SQLAlchemy ORM models and relationships
- Managing PostgreSQL schema changes with Alembic migrations
- Separating code into endpoints, services, repositories, schemas, and models
- Implementing role-based access control for ticket status updates
- Using Docker Compose for local PostgreSQL setup
- Testing API behavior through Swagger documentation

## Status

The backend MVP is complete. Future improvements may include automated tests, a frontend demo client, ticket comments, and full API containerization.