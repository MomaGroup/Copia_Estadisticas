from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuarios import Usuario
from app.schemas.usuarios import UsuarioCreate
from app.services.auth_service import hash_password


def crear_usuario(db: Session, datos: UsuarioCreate):
    existente = db.query(Usuario).filter(Usuario.email == datos.email).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado."
        )

    usuario = Usuario(
        email=datos.email,
        nombre=datos.nombre,
        rol=datos.rol,
        password=hash_password(datos.password),
        activo=True
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def listar_usuarios(db: Session):
    return db.query(Usuario).all()


def obtener_usuario(db: Session, usuario_id: str):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return usuario


def actualizar_usuario(db: Session, usuario_id: str, cambios: dict):
    usuario = obtener_usuario(db, usuario_id)

    for campo, valor in cambios.items():
        if valor is not None:
            setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario


def desactivar_usuario(db: Session, usuario_id: str):
    usuario = obtener_usuario(db, usuario_id)
    usuario.activo = False

    db.commit()
    db.refresh(usuario)
    return usuario
