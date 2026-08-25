from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.models import User
from auth.schemas import UserResponse
from core.database import get_db
from core.security import get_current_user
from profile.schemas import ProfileUpdateRequest
from profile.service import update_profile_name

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


@router.get("/me", response_model=UserResponse)
def get_profile(user: User = Depends(get_current_user)) -> User:
    # RN-018: la identidad sale EXCLUSIVAMENTE del token via
    # get_current_user; ninguna ruta/query param determina que usuario
    # se consulta. El usuario ya viene completamente resuelto, no hace
    # falta pasar por profile/service.py para simplemente devolverlo.
    return user


@router.patch("/me", response_model=UserResponse)
def update_profile(
    data: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    # RN-018: mismo criterio que GET /me -- ningun parametro de
    # ruta/query/body determina que usuario se edita, solo el token.
    return update_profile_name(db, user, data)
