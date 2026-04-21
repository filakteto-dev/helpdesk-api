from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import db
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    auth_service = AuthService(db)
    user = auth_service.register_user(user_data)
    return user