import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from auth.models import User
from core.config import settings
from core.database import get_db

BCRYPT_ROUNDS = 12  # RNF-007

JWT_ALGORITHM = "HS256"  # RNF-005
JWT_EXPIRATION = timedelta(days=7)  # RNF-004

_UNAUTHORIZED_DETAIL = "No se pudo validar las credenciales"

_bearer_scheme = HTTPBearer(auto_error=False)


def _prehash(password: str) -> bytes:
    """bcrypt (>=5.0.0) lanza ValueError ante contraseñas de mas de 72 bytes,
    y RNF-006 permite hasta 128 caracteres UTF-8 (tildes/ñ ocupan 2 bytes
    cada uno, pudiendo superar los 72 bytes sin superar los 128 caracteres).
    Se hashea la contraseña con SHA-256 antes de bcrypt para normalizar la
    longitud de entrada (64 caracteres hex, siempre por debajo del limite).
    Esto NO reemplaza a bcrypt como mecanismo de seguridad, solo evita el
    ValueError. Ver docs/03-Diseno/10_Stack_y_Versiones.md, seccion 4.
    Debe aplicarse identico en hash_password y verify_password.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("ascii")


def hash_password(password: str) -> str:
    digest = _prehash(password)
    return bcrypt.hashpw(digest, bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    digest = _prehash(password)
    return bcrypt.checkpw(digest, password_hash.encode("ascii"))


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + JWT_EXPIRATION,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_ALGORITHM])


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=_UNAUTHORIZED_DETAIL
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=_UNAUTHORIZED_DETAIL
        )

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=_UNAUTHORIZED_DETAIL
        )

    return user
