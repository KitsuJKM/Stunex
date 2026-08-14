from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class LoginRequest(BaseModel):
    # email es str, no EmailStr: un formato invalido debe fallar como
    # credenciales invalidas (401) por el flujo normal de login, no como
    # 422, para no filtrar informacion adicional (RN-014).
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    # email es str, no EmailStr (mismo criterio que LoginRequest): un
    # formato invalido no debe distinguirse con un 422 de un correo bien
    # formado pero inexistente -- ambos casos terminan en el mismo 200
    # generico de RN-014.
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)  # RF-004, RNF-006


class MessageResponse(BaseModel):
    message: str
