# app/core/report_engine.py

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.movimientos_siigo import MovimientoSIIGO
from app.models.movimientos_dian import MovimientoDIAN
from app.models.movimientos_banco import MovimientoBANCO

from app.core.filters import (
    filtrar_por_empresa,
    filtrar_por_periodo,
    filtrar_por_rango,
    filtrar_por_tipo_reporte,
    filtrar_por_categoria,
    filtrar_por_abreviatura,
    filtrar_por_documento
)

from app.core.periods import periodo_a_rango


# ===============================================================
# CONSULTA BASE — SIIGO
# ===============================================================
def consulta_base_siigo(db: Session):
    return db.query(
        MovimientoSIIGO.fecha_elaboracion.label("fecha"),
        MovimientoSIIGO.descripcion.label("descripcion"),
        MovimientoSIIGO.valor.label("valor"),
        MovimientoSIIGO.categoria_general.label("categoria"),
        MovimientoSIIGO.abreviatura_general.label("abreviatura"),
        MovimientoSIIGO.tipo_reporte.label("tipo_reporte"),
        func.cast(func.null(), func.text).label("fuente")
    )


# ===============================================================
# CONSULTA BASE — DIAN
# ===============================================================
def consulta_base_dian(db: Session):
    return db.query(
        MovimientoDIAN.fecha_emision.label("fecha"),
        MovimientoDIAN.nombre_emisor.label("descripcion"),
        MovimientoDIAN.total_bruto.label("valor"),
        MovimientoDIAN.categoria_general.label("categoria"),
        MovimientoDIAN.abreviatura_general.label("abreviatura"),
        MovimientoDIAN.tipo_reporte.label("tipo_reporte"),
        func.cast("DIAN", func.text).label("fuente")
    )


# ===============================================================
# CONSULTA BASE — BANCO
# ===============================================================
def consulta_base_banco(db: Session):
    return db.query(
        MovimientoBANCO.fecha.label("fecha"),
        MovimientoBANCO.descripcion.label("descripcion"),
        MovimientoBANCO.valor.label("valor"),
        MovimientoBANCO.categoria_general.label("categoria"),
        MovimientoBANCO.abreviatura_general.label("abreviatura"),
        MovimientoBANCO.tipo_reporte.label("tipo_reporte"),
        func.cast("BANCO", func.text).label("fuente")
    )


# ===============================================================
# APLICAR TODOS LOS FILTROS A LA CONSULTA
# ===============================================================
def aplicar_filtros(
    query,
    empresa_id=None,
    periodo=None,
    fecha_inicio=None,
    fecha_fin=None,
    tipo_reporte=None,
    categoria=None,
    abreviatura=None,
    documento=None,
    fecha_col=None
):
    # A — Empresa
    query = filtrar_por_empresa(query, empresa_id)

    # B — Periodo
    if periodo and fecha_col:
        fecha_ini, fecha_fin_p = periodo_a_rango(periodo)
        query = query.filter(fecha_col >= fecha_ini, fecha_col < fecha_fin_p)

    # C — Rango manual
    if fecha_col:
        query = filtrar_por_rango(query, fecha_col, fecha_inicio, fecha_fin)

    # D — Tipo de reporte
    query = filtrar_por_tipo_reporte(query, tipo_reporte)

    # E — Categoría
    query = filtrar_por_categoria(query, categoria)

    # F — Abreviatura
    query = filtrar_por_abreviatura(query, abreviatura)

    # G — Documento / comprobante
    query = filtrar_por_documento(query, documento)

    return query


# ===============================================================
# FUNCIÓN GENERAL PARA OBTENER MOVIMIENTOS POR FUENTE
# ===============================================================
def obtener_movimientos(
        db: Session,
        fuente: str,
        empresa_id: str,
        periodo=None,
        fecha_inicio=None,
        fecha_fin=None,
        tipo_reporte=None,
        categoria=None,
        abreviatura=None,
        documento=None
):
    """
    fuente = 'SIIGO' | 'DIAN' | 'BANCO'
    """

    if fuente == "SIIGO":
        base = consulta_base_siigo(db)
        fecha_col = MovimientoSIIGO.fecha_elaboracion

    elif fuente == "DIAN":
        base = consulta_base_dian(db)
        fecha_col = MovimientoDIAN.fecha_emision

    elif fuente == "BANCO":
        base = consulta_base_banco(db)
        fecha_col = MovimientoBANCO.fecha

    else:
        raise ValueError("Fuente inválida")

    # Aplicar filtros A–G
    q = aplicar_filtros(
        base,
        empresa_id=empresa_id,
        periodo=periodo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tipo_reporte=tipo_reporte,
        categoria=categoria,
        abreviatura=abreviatura,
        documento=documento,
        fecha_col=fecha_col
    )

    return q.order_by(fecha_col.asc()).all()


# ===============================================================
# FUNCIÓN MAESTRA — COMBINAR FUENTES
# ===============================================================
def obtener_movimientos_unificados(
        db: Session,
        empresa_id: str,
        incluir_siigo=True,
        incluir_dian=True,
        incluir_banco=True,
        **filtros
):
    resultados = []

    if incluir_siigo:
        resultados += obtener_movimientos(db, "SIIGO", empresa_id, **filtros)

    if incluir_dian:
        resultados += obtener_movimientos(db, "DIAN", empresa_id, **filtros)

    if incluir_banco:
        resultados += obtener_movimientos(db, "BANCO", empresa_id, **filtros)

    # Ordenar por fecha
    resultados.sort(key=lambda x: x.fecha)

    return resultados
