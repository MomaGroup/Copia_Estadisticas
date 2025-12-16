from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.models.empresas import Empresa
from app.models.usuarios import Usuario
from app.models.usuarios_empresas import UsuarioEmpresa
from app.schemas.empresas import EmpresaCreate


def crear_empresa(db: Session, datos: EmpresaCreate):
    existente = db.query(Empresa).filter(Empresa.nit == datos.nit).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El NIT ya está registrado."
        )

    empresa = Empresa(
        nombre=datos.nombre,
        nit=datos.nit,
        tipo_empresa_id=datos.tipo_empresa_id,
        activo=True
    )

    db.add(empresa)
    db.commit()
    db.refresh(empresa)

    return empresa


def asignar_usuario_a_empresa(db: Session, usuario_id: UUID, empresa_id: UUID):
    existente = db.query(UsuarioEmpresa).filter(
        UsuarioEmpresa.usuario_id == usuario_id,
        UsuarioEmpresa.empresa_id == empresa_id
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está asignado a esta empresa."
        )

    relacion = UsuarioEmpresa(
        usuario_id=usuario_id,
        empresa_id=empresa_id
    )

    db.add(relacion)
    db.commit()
    db.refresh(relacion)

    return relacion


def listar_empresas_usuario(db: Session, usuario_id: UUID):
    relaciones = db.query(UsuarioEmpresa).filter(
        UsuarioEmpresa.usuario_id == usuario_id
    ).all()

    empresas_ids = [r.empresa_id for r in relaciones]

    return db.query(Empresa).filter(Empresa.id.in_(empresas_ids)).all()


def obtener_empresa(db: Session, empresa_id: UUID, usuario_actual):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")

    # Si NO es admin, solo puede acceder si está asignado
    if usuario_actual.rol != "admin_general":
        asignada = db.query(UsuarioEmpresa).filter(
            UsuarioEmpresa.usuario_id == usuario_actual.id,
            UsuarioEmpresa.empresa_id == empresa_id
        ).first()

        if not asignada:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta empresa.")

    return empresa
