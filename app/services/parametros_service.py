from sqlalchemy.orm import Session
from app.models.parametros import ParametroSistema
from fastapi import HTTPException

def obtener_parametros(db: Session):
    params = db.query(ParametroSistema).all()
    return {p.clave: p.valor_texto or p.valor_numero for p in params}


def obtener_parametro(db: Session, clave: str):
    param = db.query(ParametroSistema).filter(ParametroSistema.clave == clave).first()
    if not param:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return param


def actualizar_parametro(db: Session, clave: str, valor_texto=None, valor_numero=None, usuario_id=None):
    param = obtener_parametro(db, clave)

    if valor_texto is not None:
        param.valor_texto = valor_texto

    if valor_numero is not None:
        param.valor_numero = valor_numero

    param.actualizado_por = usuario_id

    db.commit()
    db.refresh(param)
    return param
