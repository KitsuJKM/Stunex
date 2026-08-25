from sqlalchemy.orm import Session

from auth.models import User
from profile.schemas import ProfileUpdateRequest

# Se mantiene en un service.py separado (en vez de hacerlo directo en
# router.py) aunque la logica sea minima: 03_Arquitectura_Backend.md
# (secciones 3.1/3.2) ya establece que router.py no debe acceder
# directamente a la sesion de SQLAlchemy en ningun dominio -- decision
# ya aprobada, no especifica de auth/, que se mantiene aqui para no
# romper el patron entre dominios.


def update_profile_name(db: Session, user: User, data: ProfileUpdateRequest) -> User:
    """RF-016. `user` ya viene resuelto desde get_current_user (RN-018:
    la identidad sale exclusivamente del token). `data.name` ya llega
    validado y sin espacios sobrantes (profile/schemas.py)."""
    user.name = data.name
    db.commit()
    db.refresh(user)
    return user
