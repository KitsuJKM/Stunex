"""Infraestructura generica de envio de correo, sobre el SDK de Resend
(resend==2.35.0). No conoce nada de dominios especificos (auth, perfil,
etc.), igual que core/database.py es infraestructura generica de base de
datos: cualquier modulo que necesite enviar un correo reutiliza esta
funcion sin acoplarse a Resend directamente.
"""

import logging

import resend

from core.config import settings

logger = logging.getLogger("stunex.email")

_FROM_ADDRESS = "Stunex <onboarding@resend.dev>"


def send_email(to: str, subject: str, html: str) -> bool:
    """Intenta enviar un correo. Nunca lanza excepcion: si no hay API key
    configurada o el envio falla por cualquier razon, retorna False y
    registra un aviso (sin exponer el destinatario completo ni el
    contenido). El llamador decide si un fallo de envio debe afectar su
    propio flujo (en el caso de recuperacion de contraseña, no debe:
    ver auth/service.py, request_password_reset)."""
    if not settings.resend_api_key:
        logger.warning("send_email: RESEND_API_KEY no configurada, correo no enviado")
        return False

    resend.api_key = settings.resend_api_key
    try:
        resend.Emails.send(
            {
                "from": _FROM_ADDRESS,
                "to": to,
                "subject": subject,
                "html": html,
            }
        )
        return True
    except Exception:
        logger.warning("send_email: fallo el envio a %s***", to[:3], exc_info=True)
        return False
