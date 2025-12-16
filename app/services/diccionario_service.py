from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.models.diccionarios import DiccionarioDIAN, DiccionarioSIIGO
from app.schemas.diccionarios import (
    DIANCreate,
    SIIGOCREATE
)

# ========== DIAN ================

def crear_dian(db: Session, datos: DIANCreate):
    registro = DiccionarioDIAN(**datos.dict())
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


def listar_dian(db: Session):
    return db.query(DiccionarioDIAN).filter(DiccionarioDIAN.activo == True).all()


def actualizar_dian(db: Session, id: UUID, datos: DIANCreate):
    registro = db.query(DiccionarioDIAN).filter(DiccionarioDIAN.id == id).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Entrada no encontrada.")

    for campo, valor in datos.dict().items():
        setattr(registro, campo, valor)

    db.commit()
    db.refresh(registro)
    return registro


def eliminar_dian(db: Session, id: UUID):
    registro = db.query(DiccionarioDIAN).filter(DiccionarioDIAN.id == id).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Entrada no encontrada.")

    registro.activo = False
    db.commit()
    return {"msg": "Registro desactivado correctamente."}


# ========== SIIGO =================

def crear_siigo(db: Session, datos: SIIGOCREATE):
    registro = DiccionarioSIIGO(**datos.dict())
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


def listar_siigo(db: Session, empresa_id: UUID):
    return db.query(DiccionarioSIIGO).filter(
        DiccionarioSIIGO.empresa_id == empresa_id,
        DiccionarioSIIGO.activo == True
    ).all()


def actualizar_siigo(db: Session, id: UUID, datos: SIIGOCREATE):
    registro = db.query(DiccionarioSIIGO).filter(DiccionarioSIIGO.id == id).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Entrada no encontrada.")

    for campo, valor in datos.dict().items():
        setattr(registro, campo, valor)

    db.commit()
    db.refresh(registro)
    return registro


def eliminar_siigo(db: Session, id: UUID):
    registro = db.query(DiccionarioSIIGO).filter(DiccionarioSIIGO.id == id).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Entrada no encontrada.")

    registro.activo = False
    db.commit()
    return {"msg": "Registro desactivado correctamente."}
