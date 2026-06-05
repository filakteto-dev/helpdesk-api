from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenResponse
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

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    auth_service = AuthService(db)
    access_token = auth_service.login_user(
        email=form_data.username,
        password=form_data.password,
    )
    return TokenResponse(access_token=access_token)

@router.get("/me", response_model=UserResponse)
def get_me(current_user = Depends(get_current_user)) -> UserResponse:
    return current_user