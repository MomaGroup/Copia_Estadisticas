from pydantic import BaseModel, EmailStr
from uuid import UUID

class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str
    rol: str

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioRead(UsuarioBase):
    id: UUID

    class Config:
        orm_mode = True
