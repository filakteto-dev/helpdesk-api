from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db
from app.main import app


class BrokenSession:
    def execute(self, *args, **kwargs):
        raise SQLAlchemyError("database is down")


def broken_get_db():
    yield BrokenSession()


def test_healthcheck_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_healthcheck_db_ready_returns_ok(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_healthcheck_db_ready_returns_503_when_db_down(client):
    app.dependency_overrides[get_db] = broken_get_db
    
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}