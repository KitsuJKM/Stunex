"""Utilidad reutilizable de rate limiting, construida sobre el Limiter de
slowapi con almacenamiento en memoria (sin Redis), conforme a
docs/03-Diseno/03_Arquitectura_Backend.md, seccion 4.4.

El decorador declarativo estandar de slowapi (@limiter.limit(...)) cuenta
TODA solicitud entrante, sin distinguir exitos de fallos. Cuando una regla
de negocio exige contar solo los intentos FALLIDOS (por ejemplo RN-010),
ese decorador no sirve. Esta utilidad expone en su lugar la API de bajo
nivel de slowapi/limits (Limiter().limiter, con .test()/.hit()) para que
el llamador decida explicitamente cuando contar un intento.
"""

from limits import RateLimitItemPerSecond
from slowapi import Limiter
from slowapi.util import get_remote_address

# Instancia unica del proceso: una sola MemoryStorage compartida por todas
# las reglas (RateLimitRule) que se creen a partir de este modulo. key_func
# no se usa realmente aqui -- es un parametro obligatorio del constructor de
# slowapi.Limiter, pensado para su decorador declarativo, que esta utilidad
# no utiliza.
_limiter = Limiter(key_func=get_remote_address)


class RateLimitRule:
    """Regla de rate limiting parametrizable en numero de intentos y
    duracion de la ventana (en segundos), reutilizable para distintas
    claves (IP, correo, etc.) sin duplicar la logica de conteo."""

    def __init__(self, max_attempts: int, window_seconds: int) -> None:
        self._item = RateLimitItemPerSecond(max_attempts, window_seconds)

    def is_blocked(self, key: str) -> bool:
        """Comprueba si `key` ya superó el límite, SIN incrementar el contador."""
        return not _limiter.limiter.test(self._item, key)

    def register_failed_attempt(self, key: str) -> None:
        """Registra explícitamente un intento fallido contra `key`
        (incrementa el contador). No debe llamarse ante un intento exitoso."""
        _limiter.limiter.hit(self._item, key)
