from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.models import User
from auth.schemas import LoginRequest, RegisterRequest
from core.rate_limit import RateLimitRule
from core.security import create_access_token, hash_password, verify_password

# RF-017, RNF-008, RN-010: 5 intentos fallidos / 15 minutos, evaluados de
# forma independiente por IP y por cuenta (correo). Instancias unicas del
# modulo: auth/router.py las reutiliza (mismo objeto) para el chequeo
# previo sin incrementar (is_blocked), de modo que ambos lean/escriban el
# mismo estado.
LOGIN_RATE_LIMIT_MAX_ATTEMPTS = 5
LOGIN_RATE_LIMIT_WINDOW_SECONDS = 15 * 60

login_rate_limit_by_ip = RateLimitRule(
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS, LOGIN_RATE_LIMIT_WINDOW_SECONDS
)
login_rate_limit_by_email = RateLimitRule(
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS, LOGIN_RATE_LIMIT_WINDOW_SECONDS
)


def login_rate_limit_key_for_ip(ip: str) -> str:
    return f"login:ip:{ip}"


def login_rate_limit_key_for_email(email: str) -> str:
    return f"login:email:{email.lower()}"


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


def authenticate_user(db: Session, data: LoginRequest, client_ip: str) -> str:
    user = db.execute(
        select(User).where(User.email == data.email)
    ).scalar_one_or_none()
    if user is None or not verify_password(data.password, user.password_hash):
        # RN-010: solo los intentos FALLIDOS cuentan contra el limite.
        # Se registra contra ambas claves (IP y cuenta); un login exitoso
        # (branch de abajo) nunca llama a register_failed_attempt.
        login_rate_limit_by_ip.register_failed_attempt(
            login_rate_limit_key_for_ip(client_ip)
        )
        login_rate_limit_by_email.register_failed_attempt(
            login_rate_limit_key_for_email(data.email)
        )
        raise InvalidCredentialsError()

    return create_access_token(user.id)
