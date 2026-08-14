from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    # Fuerza la zona horaria de sesion a UTC en cada conexion, sin
    # importar la configuracion "SYSTEM" del servidor MySQL subyacente
    # (que difiere entre entornos: instalacion nativa vs Docker). MySQL
    # interpreta columnas TIMESTAMP segun time_zone de sesion; sin esto,
    # auth/service.py::_utcnow() asumiria UTC incorrectamente en un
    # entorno cuya zona horaria del sistema no sea UTC.
    connect_args={"init_command": "SET time_zone='+00:00'"},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
