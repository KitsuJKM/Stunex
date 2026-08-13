from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from auth.schemas import LoginRequest, RegisterRequest, Token, UserResponse
from auth.service import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    authenticate_user,
    login_rate_limit_by_email,
    login_rate_limit_by_ip,
    login_rate_limit_key_for_email,
    login_rate_limit_key_for_ip,
    register_user,
)
from core.database import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

_INVALID_CREDENTIALS_DETAIL = "Correo o contraseña incorrectos"
_RATE_LIMIT_DETAIL = "Demasiados intentos. Vuelve a intentarlo más tarde."


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(data: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    try:
        user = register_user(db, data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado",
        )
    return user


@router.post("/login", response_model=Token)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)) -> Token:
    ip = _client_ip(request)

    # RF-017, RNF-008, RN-010: se verifica SIN incrementar. Si cualquiera
    # de las dos claves (IP o cuenta) ya superó el límite, se rechaza sin
    # revelar cuál de las dos fue.
    blocked = login_rate_limit_by_ip.is_blocked(
        login_rate_limit_key_for_ip(ip)
    ) or login_rate_limit_by_email.is_blocked(
        login_rate_limit_key_for_email(data.email)
    )
    if blocked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=_RATE_LIMIT_DETAIL,
        )

    try:
        access_token = authenticate_user(db, data, ip)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS_DETAIL,
        )
    return Token(access_token=access_token, token_type="bearer")
