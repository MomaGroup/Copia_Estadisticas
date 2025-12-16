from pydantic import BaseModel
from uuid import UUID

# ======= DIAN ===========

class DIANBase(BaseModel):
    grupo: str
    tipo_documento: str
    nombre_generico: str
    abreviatura_general: str
    categoria_general: str
    tipo_reporte: str

class DIANCreate(DIANBase):
    pass

class DIANRead(DIANBase):
    id: UUID

    class Config:
        orm_mode = True


# ======= SIIGO ==========

class SIIGOBase(BaseModel):
    empresa_id: UUID
    comprobante: str
    abreviatura_general: str
    categoria_general: str
    tipo_reporte: str

class SIIGOCREATE(SIIGOBase):
    pass

class SIIGORead(SIIGOBase):
    id: UUID

    class Config:
        orm_mode = True
