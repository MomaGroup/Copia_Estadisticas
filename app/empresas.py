from pydantic import BaseModel
from uuid import UUID

class EmpresaBase(BaseModel):
    nombre: str
    nit: str
    tipo_empresa_id: UUID

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaRead(EmpresaBase):
    id: UUID

    class Config:
        orm_mode = True
