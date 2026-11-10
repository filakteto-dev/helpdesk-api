from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import get_db
from sqlalchemy import text
from fastapi import HTTPException, status
import logging

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.tickets import router as tickets_router

app = FastAPI(title="Helpdesk API")

app.include_router(auth_router)
app.include_router(tickets_router)

logger = logging.getLogger(__name__)

@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/health/ready")
def healthcheck_ready(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Database readiness check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",)
    return {"status": "ok", "database": "ok"}