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
