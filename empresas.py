from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.connection import get_db
from app.schemas.empresas import EmpresaCreate
from app.schemas.empresas import EmpresaRead
from app.services.empresa_service import (
    crear_empresa,
    asignar_usuario_a_empresa,
    listar_empresas_usuario,
    obtener_empresa
)
from app.core.security import get_current_user

router = APIRouter()


def validar_admin(usuario_actual):
    if usuario_actual.rol != "admin_general":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción."
        )


@router.post("/", response_model=EmpresaRead)
def crear(
    datos: EmpresaCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    validar_admin(usuario_actual)
    return crear_empresa(db, datos)


@router.post("/asignar/{empresa_id}/{usuario_id}")
def asignar(
    empresa_id: UUID,
    usuario_id: UUID,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    validar_admin(usuario_actual)
    return asignar_usuario_a_empresa(db, usuario_id, empresa_id)


@router.get("/", response_model=list[EmpresaRead])
def mis_empresas(
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    return listar_empresas_usuario(db, usuario_actual.id)


@router.get("/{empresa_id}", response_model=EmpresaRead)
def obtener(
    empresa_id: UUID,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    return obtener_empresa(db, empresa_id, usuario_actual)
