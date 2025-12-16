from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.connection import get_db
from app.schemas.diccionarios import (
    DIANCreate, DIANRead,
    SIIGOCREATE, SIIGORead
)
from app.services.diccionario_service import (
    crear_dian, listar_dian, actualizar_dian, eliminar_dian,
    crear_siigo, listar_siigo, actualizar_siigo, eliminar_siigo
)
from app.core.security import get_current_user


router = APIRouter()


def validar_admin(usuario_actual):
    if usuario_actual.rol != "admin_general":
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para esta acción."
        )


# ========== DIAN ===================

@router.post("/dian/", response_model=DIANRead)
def crear_d(dic: DIANCreate, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    validar_admin(usuario)
    return crear_dian(db, dic)


@router.get("/dian/", response_model=list[DIANRead])
def listar_d(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return listar_dian(db)


@router.put("/dian/{id}", response_model=DIANRead)
def modificar_d(id: UUID, dic: DIANCreate, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    validar_admin(usuario)
    return actualizar_dian(db, id, dic)


@router.delete("/dian/{id}")
def eliminar_d(id: UUID, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    validar_admin(usuario)
    return eliminar_dian(db, id)


# ========== SIIGO ====================

@router.post("/siigo/", response_model=SIIGORead)
def crear_s(dic: SIIGOCREATE, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    validar_admin(usuario)
    return crear_siigo(db, dic)


@router.get("/siigo/{empresa_id}", response_model=list[SIIGORead])
def listar_s(empresa_id: UUID, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    return listar_siigo(db, empresa_id)


@router.put("/siigo/{id}", response_model=SIIGORead)
def modificar_s(id: UUID, dic: SIIGOCREATE, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    validar_admin(usuario)
    return actualizar_siigo(db, id, dic)


@router.delete("/siigo/{id}")
def eliminar_s(id: UUID, db: Session = Depends(get_db), usuario=Depends(get_current_user)):
    validar_admin(usuario)
    return eliminar_siigo(db, id)
