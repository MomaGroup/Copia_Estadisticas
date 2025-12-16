from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.connection import get_db
from app.schemas.usuarios import UsuarioCreate, UsuarioRead
from app.services.usuario_service import (
    crear_usuario,
    listar_usuarios,
    obtener_usuario,
    actualizar_usuario,
    desactivar_usuario
)
from app.core.security import get_current_user

router = APIRouter()


# Solo admin_general puede administrar usuarios
def validar_admin(usuario_actual):
    if usuario_actual.rol != "admin_general":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción."
        )


@router.post("/", response_model=UsuarioRead)
def crear(
    datos: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    validar_admin(usuario_actual)
    return crear_usuario(db, datos)


@router.get("/", response_model=list[UsuarioRead])
def listar(
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    validar_admin(usuario_actual)
    return listar_usuarios(db)


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener(
    usuario_id: UUID,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    # Usuario común solo puede ver su perfil
    if str(usuario_id) != str(usuario_actual.id) and usuario_actual.rol != "admin_general":
        raise HTTPException(status_code=403, detail="Acceso denegado.")

    return obtener_usuario(db, usuario_id)


@router.put("/{usuario_id}", response_model=UsuarioRead)
def actualizar(
    usuario_id: UUID,
    cambios: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    validar_admin(usuario_actual)
    return actualizar_usuario(db, usuario_id, cambios.dict())


@router.delete("/{usuario_id}")
def desactivar(
    usuario_id: UUID,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    validar_admin(usuario_actual)
    return desactivar_usuario(db, usuario_id)
