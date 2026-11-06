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
- Dockerized FastAPI and PostgreSQL services
- Automatic database migrations on container startup
- Healthchecks for the API and database

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

Dockerfile
.dockerignore
docker-compose.yml
requirements.txt
.env.example
README.md
```

The application follows a layered architecture. Endpoints handle HTTP requests and delegate business logic to services. Services use repositories for database access. SQLAlchemy models describe database tables, while Pydantic schemas define request and response validation.

## Getting Started with Docker

### Prerequisites

- Git
- Docker with Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/Filakteto-dev/helpdesk-api
cd helpdesk-api
```

### 2. Create the environment file

```bash
cp .env.example .env
```

Replace the example `SECRET_KEY` before using the application outside local development.

### 3. Build and start the stack

```bash
docker compose up -d --build
```

Docker Compose starts the services in the following order:

1. `db` starts PostgreSQL and waits for it to accept connections.
2. `migrate` applies all pending Alembic migrations and exits successfully.
3. `api` starts Uvicorn after the migrations complete.

### 4. Check service status

```bash
docker compose ps -a
```

The expected state is:

- `db` is running and healthy;
- `migrate` has exited with code `0`;
- `api` is running and healthy.

### 5. Open the API

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health endpoint: [http://localhost:8000/health](http://localhost:8000/health)

### 6. View logs

```bash
docker compose logs -f
```

Logs for a specific service can be viewed separately:

```bash
docker compose logs -f api
docker compose logs -f db
docker compose logs migrate
```

### 7. Stop the stack

```bash
docker compose down
```

This removes the containers and Compose network but preserves PostgreSQL data in the named volume.

> **Warning:** `docker compose down -v` also deletes the PostgreSQL volume and all local database data.

## Local Development without Dockerized API

Docker can run only PostgreSQL while the FastAPI application runs directly in the local Python environment.

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the environment file

```bash
cp .env.example .env
```

### 4. Start PostgreSQL

```bash
docker compose up -d db
```

### 5. Apply migrations

```bash
alembic upgrade head
```

### 6. Run the API with reload

```bash
uvicorn app.main:app --reload
```

The API is available at:

```text
http://localhost:8000
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

When the application runs through Docker Compose, `DATABASE_URL` is overridden so that the API connects to PostgreSQL through the internal service hostname `db`. The `localhost` value in `.env.example` is used when the API runs directly on the host machine.

## Docker Services

| Service | Purpose | Lifecycle |
| ------- | ------- | --------- |
| `db` | Runs PostgreSQL 16 and stores data in the `postgres_data` volume | Long-running |
| `migrate` | Runs `alembic upgrade head` after PostgreSQL becomes healthy | Exits after completion |
| `api` | Runs the FastAPI application with Uvicorn on port 8000 | Long-running |

The API connects to PostgreSQL using the Compose service hostname `db`. Inside a container, `localhost` refers to that same container, not to other services or the host machine.

## Database Migrations

Docker Compose applies existing migrations automatically through the one-time `migrate` service. The commands below are used when creating, inspecting, or rolling back migrations during local development.

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

## Tests

Run the test suite with application coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

The current suite covers authentication, authorization, ticket workflows, validation errors, and the health endpoint.

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

## What I Practiced

- Building REST API endpoints with FastAPI
- Working with request and response schemas using Pydantic v2
- Implementing JWT-based authentication
- Protecting endpoints with authenticated user dependencies
- Designing SQLAlchemy ORM models and relationships
- Managing PostgreSQL schema changes with Alembic migrations
- Separating code into endpoints, services, repositories, schemas, and models
- Implementing role-based access control for ticket status updates
- Containerizing FastAPI with Docker
- Orchestrating the API, migrations, and PostgreSQL with Docker Compose
- Adding API and database healthchecks
- Testing API behavior and authorization with pytest
- Testing API behavior through Swagger documentation

## Status

The backend MVP and local containerized environment are complete. Future improvements may include continuous integration, a frontend demo client, ticket comments, production deployment configuration, and observability.
