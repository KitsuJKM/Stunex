from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.models import User
from auth.schemas import LoginRequest, RegisterRequest
from core.security import create_access_token, hash_password, verify_password


class EmailAlreadyRegisteredError(Exception):
    """El correo ya esta asociado a una cuenta existente (RF-002, RN-001).
    auth/router.py la traduce a HTTPException 409."""


class InvalidCredentialsError(Exception):
    """Credenciales invalidas en login (RF-008, RN-014). Se lanza tanto si
    el correo no existe como si la contraseña no coincide, siempre con el
    mismo tipo, para que auth/router.py responda el mismo 401 genérico en
    ambos casos sin distinguir cual de los dos fallo."""


def register_user(db: Session, data: RegisterRequest) -> User:
    existing = db.execute(
        select(User).where(User.email == data.email)
    ).scalar_one_or_none()
    if existing is not None:
        raise EmailAlreadyRegisteredError()

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: LoginRequest) -> str:
    user = db.execute(
        select(User).where(User.email == data.email)
    ).scalar_one_or_none()
    if user is None or not verify_password(data.password, user.password_hash):
        raise InvalidCredentialsError()

    return create_access_token(user.id)
