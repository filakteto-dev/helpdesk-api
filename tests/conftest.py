import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User, UserRole


TEST_DATABASE_URL = "sqlite://"
TEST_SECRET_KEY = "test_secret-key-that-is-longer-than-32-bytes"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _create_auth_headers_for_role(
    client,
    user_data,
    role,
):
    register_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    with TestingSessionLocal() as db:
        user = db.execute(
            select(User).where(
                User.email == user_data["email"]
            )
        ).scalar_one()

        user.role = role
        db.commit()

    login_response = client.post(
        "/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(settings, "SECRET_KEY", TEST_SECRET_KEY)

    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def registered_user(client):
    user_data = {
        "email": "alice@example.com",
        "username": "alice",
        "password": "very-strong-password",
    }

    response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert response.status_code == 201

    return user_data


@pytest.fixture
def auth_headers(client, registered_user):
    login_response = client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest.fixture
def second_registered_user(client):
    user_data = {
        "email": "bob@example.com",
        "username": "bob",
        "password": "very-strong-password",
    }

    response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert response.status_code == 201

    return user_data


@pytest.fixture
def second_auth_headers(client, second_registered_user):
    login_response = client.post(
        "/auth/login",
        data={
            "username": second_registered_user["email"],
            "password": second_registered_user["password"],
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest.fixture
def support_auth_headers(client):
    return _create_auth_headers_for_role(
        client=client,
        user_data={
            "email": "support@example.com",
            "username": "support",
            "password": "very-strong-password",
        },
        role=UserRole.SUPPORT,
    )


@pytest.fixture
def admin_auth_headers(client):
    return _create_auth_headers_for_role(
        client=client,
        user_data={
            "email": "admin@example.com",
            "username": "admin",
            "password": "very-strong-password",
        },
        role=UserRole.ADMIN,
    )
