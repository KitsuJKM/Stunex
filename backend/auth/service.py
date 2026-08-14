import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.models import PasswordResetToken, User
from auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from core.email import send_email
from core.rate_limit import RateLimitRule
from core.security import create_access_token, hash_password, verify_password


def _utcnow() -> datetime:
    """Datetime naive en UTC, consistente con lo que PyMySQL/SQLAlchemy
    devuelve para columnas TIMESTAMP (verificado: sin tzinfo). Se usa para
    calcular y comparar expires_at/used_at sin mezclar naive/aware."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

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


# RNF-010, RN-017: 1 solicitud por correo cada 5 minutos. Solo por cuenta,
# sin dimension de IP (a diferencia de login) -- asi lo definen RNF-010 y
# RN-017 explicitamente ("por correo").
FORGOT_PASSWORD_RATE_LIMIT_MAX_ATTEMPTS = 1
FORGOT_PASSWORD_RATE_LIMIT_WINDOW_SECONDS = 5 * 60

forgot_password_rate_limit_by_email = RateLimitRule(
    FORGOT_PASSWORD_RATE_LIMIT_MAX_ATTEMPTS, FORGOT_PASSWORD_RATE_LIMIT_WINDOW_SECONDS
)


def forgot_password_rate_limit_key_for_email(email: str) -> str:
    return f"forgot_password:email:{email.lower()}"


# RNF-009, RN-016: el token de restablecimiento es valido por 15 minutos.
RESET_TOKEN_LIFETIME = timedelta(minutes=15)


def generate_reset_token() -> tuple[str, str]:
    """Genera un token de restablecimiento de alta entropia (32 bytes via
    secrets.token_urlsafe, modulo estandar) y su hash SHA-256 en hex (64
    caracteres, calza con CHAR(64) de password_reset_tokens.token_hash).
    Se persiste solo el hash (ver reset_password mas abajo); el valor en
    texto plano se entrega por correo y nunca se guarda ni se loguea.

    No se ubica en core/security.py: a diferencia de get_current_user
    (reutilizado deliberadamente por futuros dominios sin depender de
    auth/, ver 03_Arquitectura_Backend.md seccion 4.3), la generacion de
    tokens de restablecimiento es una responsabilidad especifica del
    ciclo de vida de la cuenta -- mismo criterio ya aplicado a la propia
    tabla password_reset_tokens en 03_Arquitectura_Backend.md seccion
    7.7 -- y ningun otro dominio la necesita hoy.
    """
    token = secrets.token_urlsafe(32)
    return token, hash_reset_token(token)


def hash_reset_token(token: str) -> str:
    """Calcula el hash SHA-256 (hex) de un token en texto plano. Debe ser
    EXACTAMENTE el mismo mecanismo usado en generate_reset_token, o el
    token nunca se encontrara al validarlo en reset_password.

    No es bcrypt: bcrypt esta pensado para contraseñas de baja entropia
    elegidas por humanos (por eso hash_password lo usa); este token ya es
    aleatorio y de alta entropia, SHA-256 directo es suficiente y
    apropiado (mismo razonamiento ya documentado en
    docs/03-Diseno/04_Modelo_Base_de_Datos.md, seccion 3.1)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class EmailAlreadyRegisteredError(Exception):
    """El correo ya esta asociado a una cuenta existente (RF-002, RN-001).
    auth/router.py la traduce a HTTPException 409."""


class InvalidCredentialsError(Exception):
    """Credenciales invalidas en login (RF-008, RN-014). Se lanza tanto si
    el correo no existe como si la contraseña no coincide, siempre con el
    mismo tipo, para que auth/router.py responda el mismo 401 genérico en
    ambos casos sin distinguir cual de los dos fallo."""


class InvalidResetTokenError(Exception):
    """Token de restablecimiento ausente, invalido, expirado o ya usado
    (RF-014, RN-015, RN-016). Se lanza con el mismo tipo en los tres
    casos para que auth/router.py responda un unico 401 generico, sin
    distinguir la causa -- mismo criterio defensivo ya aplicado en
    InvalidCredentialsError y en get_current_user."""


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
        # (branch de abajo) nunca llama a register_attempt.
        login_rate_limit_by_ip.register_attempt(
            login_rate_limit_key_for_ip(client_ip)
        )
        login_rate_limit_by_email.register_attempt(
            login_rate_limit_key_for_email(data.email)
        )
        raise InvalidCredentialsError()

    return create_access_token(user.id)


def request_password_reset(db: Session, data: ForgotPasswordRequest) -> None:
    """RF-012, RF-013. No retorna nada que distinga si el usuario existia:
    auth/router.py responde siempre el mismo mensaje generico (RN-014)
    sin importar el resultado interno de esta funcion."""
    user = db.execute(
        select(User).where(User.email == data.email)
    ).scalar_one_or_none()
    if user is None:
        return  # RN-014: no se genera token ni fila alguna para este caso

    token, token_hash = generate_reset_token()
    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=_utcnow() + RESET_TOKEN_LIFETIME,
    )
    db.add(reset_token)
    db.commit()

    # El envio de correo nunca debe romper el contrato del endpoint: la
    # generacion/persistencia del token (lo que importa) ya ocurrio antes
    # de este intento. send_email no lanza excepcion si falla.
    send_email(
        to=user.email,
        subject="Recupera tu contraseña en Stunex",
        html=(
            "<p>Ingresa el siguiente código en la aplicación para "
            "restablecer tu contraseña. Es válido por 15 minutos:</p>"
            f"<p><strong>{token}</strong></p>"
        ),
    )


def reset_password(db: Session, data: ResetPasswordRequest) -> None:
    """RF-013, RF-014. Un unico InvalidResetTokenError cubre token
    ausente/invalido/expirado/ya usado (RN-015, RN-016), sin distinguir
    la causa en lo que ve el cliente."""
    token_hash = hash_reset_token(data.token)
    reset_token = db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    ).scalar_one_or_none()

    if (
        reset_token is None
        or reset_token.used_at is not None
        or reset_token.expires_at < _utcnow()
    ):
        raise InvalidResetTokenError()

    user = db.get(User, reset_token.user_id)
    user.password_hash = hash_password(data.new_password)
    reset_token.used_at = _utcnow()  # RN-015: invalidacion permanente tras el uso
    db.commit()
