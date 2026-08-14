from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    Token,
    UserResponse,
)
from auth.service import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidResetTokenError,
    authenticate_user,
    forgot_password_rate_limit_by_email,
    forgot_password_rate_limit_key_for_email,
    login_rate_limit_by_email,
    login_rate_limit_by_ip,
    login_rate_limit_key_for_email,
    login_rate_limit_key_for_ip,
    register_user,
    request_password_reset,
    reset_password,
)
from core.database import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

_INVALID_CREDENTIALS_DETAIL = "Correo o contraseña incorrectos"
_RATE_LIMIT_DETAIL = "Demasiados intentos. Vuelve a intentarlo más tarde."
_INVALID_RESET_TOKEN_DETAIL = "El token no es válido"
_FORGOT_PASSWORD_MESSAGE = (
    "Si el correo está registrado, recibirás instrucciones para "
    "restablecer tu contraseña."
)
_RESET_PASSWORD_MESSAGE = "Contraseña actualizada correctamente."


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


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    data: ForgotPasswordRequest, db: Session = Depends(get_db)
) -> MessageResponse:
    # RNF-010, RN-017: 1 solicitud por correo cada 5 minutos. Solo por
    # cuenta, sin dimension de IP (a diferencia de login).
    key = forgot_password_rate_limit_key_for_email(data.email)
    if forgot_password_rate_limit_by_email.is_blocked(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=_RATE_LIMIT_DETAIL,
        )
    forgot_password_rate_limit_by_email.register_attempt(key)

    request_password_reset(db, data)
    # RN-014: siempre el mismo 200 con el mismo mensaje, exista o no la
    # cuenta -- request_password_reset no revela cual fue el caso.
    return MessageResponse(message=_FORGOT_PASSWORD_MESSAGE)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password_endpoint(
    data: ResetPasswordRequest, db: Session = Depends(get_db)
) -> MessageResponse:
    try:
        reset_password(db, data)
    except InvalidResetTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_RESET_TOKEN_DETAIL,
        )
    return MessageResponse(message=_RESET_PASSWORD_MESSAGE)
