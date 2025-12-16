from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.parametros_service import (
    obtener_parametros,
    obtener_parametro,
    actualizar_parametro
)

router = APIRouter(prefix="/parametros", tags=["Parámetros"])


@router.get("/")
def listar_parametros(db: Session = Depends(get_db)):
    return obtener_parametros(db)


@router.get("/{clave}")
def get_parametro(clave: str, db: Session = Depends(get_db)):
    return obtener_parametro(db, clave)


@router.put("/{clave}")
def update_parametro(
    clave: str,
    valor_texto: str = None,
    valor_numero: float = None,
    usuario_id: str = None,
    db: Session = Depends(get_db)
):
    return actualizar_parametro(
        db=db,
        clave=clave,
        valor_texto=valor_texto,
        valor_numero=valor_numero,
        usuario_id=usuario_id
    )
