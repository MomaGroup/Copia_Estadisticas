# app/routers/reportes.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from app.database.connection import get_db
from app.core.security import get_current_user
from app.core.report_engine import (
    obtener_movimientos,
    obtener_movimientos_unificados
)


router = APIRouter()


# ===============================================================
# Endpoint genérico para movimientos por fuente
# ===============================================================
@router.get("/movimientos/{fuente}")
def listar_por_fuente(
    fuente: str,
    empresa_id: str,
    periodo: str | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    tipo_reporte: str | None = None,
    categoria: str | None = None,
    abreviatura: str | None = None,
    documento: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    """
    fuente = SIIGO | DIAN | BANCO
    """

    return obtener_movimientos(
        db=db,
        fuente=fuente.upper(),
        empresa_id=empresa_id,
        periodo=periodo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tipo_reporte=tipo_reporte,
        categoria=categoria,
        abreviatura=abreviatura,
        documento=documento
    )


# ===============================================================
# Movimientos unificados (SIIGO + DIAN + BANCO)
# ===============================================================
@router.get("/movimientos-unificados")
def movimientos_unificados(
    empresa_id: str,
    periodo: str | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    tipo_reporte: str | None = None,
    categoria: str | None = None,
    abreviatura: str | None = None,
    documento: str | None = None,
    incluir_siigo: bool = True,
    incluir_dian: bool = True,
    incluir_banco: bool = True,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return obtener_movimientos_unificados(
        db=db,
        empresa_id=empresa_id,
        incluir_siigo=incluir_siigo,
        incluir_dian=incluir_dian,
        incluir_banco=incluir_banco,
        periodo=periodo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tipo_reporte=tipo_reporte,
        categoria=categoria,
        abreviatura=abreviatura,
        documento=documento
    )


# ===============================================================
# Ingresos basados en categoría o tipo_reporte
# ===============================================================
@router.get("/ingresos")
def reporte_ingresos(
    empresa_id: str,
    periodo: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return obtener_movimientos_unificados(
        db=db,
        empresa_id=empresa_id,
        periodo=periodo,
        tipo_reporte="INGRESOS"
    )


# ===============================================================
# Egresos basados en categoría o tipo_reporte
# ===============================================================
@router.get("/egresos")
def reporte_egresos(
    empresa_id: str,
    periodo: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    return obtener_movimientos_unificados(
        db=db,
        empresa_id=empresa_id,
        periodo=periodo,
        tipo_reporte="EGRESOS"
    )


# ===============================================================
# Resumen general: suma de ingresos y egresos
# ===============================================================
@router.get("/resumen-general")
def resumen_general(
    empresa_id: str,
    periodo: str,
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user)
):
    datos = obtener_movimientos_unificados(
        db=db,
        empresa_id=empresa_id,
        periodo=periodo
    )

    ingresos = sum(d.valor for d in datos if d.tipo_reporte.upper() == "INGRESOS")
    egresos = sum(d.valor for d in datos if d.tipo_reporte.upper() == "EGRESOS")

    return {
        "periodo": periodo,
        "ingresos": ingresos,
        "egresos": egresos,
        "resultado": ingresos - egresos
    }

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.report_service import obtener_reporte_matriz

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.get("/matriz")
def matriz_conciliacion(db: Session = Depends(get_db)):
    return obtener_reporte_matriz(db)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.report_service import obtener_reporte_detallado

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/detallado")
def reporte_detallado(empresa_id: str, periodo: str, db: Session = Depends(get_db)):
    return obtener_reporte_detallado(db, empresa_id, periodo)

@router.get("/global")
def reporte_global_api(periodo: str, db: Session = Depends(get_db)):
    """
    Reporte Global Multiempresa:
    PUB, CON, PNC, PNI, avance, rezago, calidad, totales.
    """
    from app.services.report_global_service import reporte_global
    return reporte_global(periodo, db)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.report_filtered_service import generar_reporte_filtrado

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/matriz-filtrada")
def reporte_matriz_filtrada(
    empresa_id: str = Query(None),
    fecha_inicio: str = Query(None),
    fecha_fin: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Devuelve PUB / CON / PNI por categoría,
    filtrado por empresa y fechas.
    """
    data = generar_reporte_filtrado(
        db=db,
        empresa_id=empresa_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

    return {
        "success": True,
        "empresa_id": empresa_id,
        "filtros": {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        },
        "data": data
    }
