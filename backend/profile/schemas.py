from pydantic import BaseModel, Field, field_validator


class ProfileUpdateRequest(BaseModel):
    # RN-019: unico campo editable del perfil. min_length/max_length
    # coinciden con users.name VARCHAR(100) (mismo limite que
    # RegisterRequest.name en auth/schemas.py).
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def _strip_and_reject_blank(cls, value: str) -> str:
        # El length check de Pydantic por si solo deja pasar " " (1
        # caracter, min_length=1 cumplido). CU-007 E1 exige rechazar un
        # nombre vacio o invalido -- " " no es un nombre valido.
        stripped = value.strip()
        if not stripped:
            raise ValueError("El nombre no puede estar vacío")
        return stripped
