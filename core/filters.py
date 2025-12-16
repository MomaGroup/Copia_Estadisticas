# app/core/filters.py

from datetime import date
from sqlalchemy.orm import Query


# ==============================================
# FILTRO A — Filtrar por empresa
# ==============================================
def filtrar_por_empresa(query: Query, empresa_id):
    return query.filter(query.column_descriptions[0]["entity"].empresa_id == empresa_id)



# ==============================================
# FILTRO B — Filtrar por periodo contable (YYYY-MM)
# Esto se combina con core/periods.py
# ==============================================
def filtrar_por_periodo(query: Query, fecha_col, periodo: str):
    """
    periodo = '2024-03'
    Se filtra por todas las fechas del mes.
    """
    if not periodo:
        return query

    year, month = map(int, periodo.split("-"))
    fecha_ini = date(year, month, 1)
    
    # calcular último día del mes
    if month == 12:
        fecha_fin = date(year + 1, 1, 1)
    else:
        fecha_fin = date(year, month + 1, 1)

    return query.filter(fecha_col >= fecha_ini, fecha_col < fecha_fin)



# ==============================================
# FILTRO C — Filtrar por rango de fechas
# ==============================================
def filtrar_por_rango(query: Query, fecha_col, fecha_inicio: date, fecha_fin: date):
    if fecha_inicio:
        query = query.filter(fecha_col >= fecha_inicio)
    if fecha_fin:
        query = query.filter(fecha_col <= fecha_fin)
    return query



# ==============================================
# FILTRO D — Filtrar por tipo de reporte
# (ingresos, egresos, indicadores, etc.)
# ==============================================
def filtrar_por_tipo_reporte(query: Query, tipo_reporte: str):
    if tipo_reporte:
        return query.filter(query.column_descriptions[0]["entity"].tipo_reporte == tipo_reporte)
    return query



# ==============================================
# FILTRO E — Filtrar por categoría general
# (Ej: B-EGR, B-RCJ, B-NBK, VENTA, COMPRA, etc.)
# ==============================================
def filtrar_por_categoria(query: Query, categoria: str):
    if categoria:
        return query.filter(query.column_descriptions[0]["entity"].categoria_general == categoria)
    return query



# ==============================================
# FILTRO F — Filtrar por abreviatura general
# (Ej: FAC, REC, AJU, NC, ND, etc.)
# ==============================================
def filtrar_por_abreviatura(query: Query, abreviatura: str):
    if abreviatura:
        return query.filter(query.column_descriptions[0]["entity"].abreviatura_general == abreviatura)
    return query



# ==============================================
# FILTRO G — Filtrar por comprobante o documento
# Esto aplica principalmente para SIIGO y DIAN
# ==============================================
def filtrar_por_documento(query: Query, documento: str, field_name="comprobante"):
    """
    field_name puede ser:
    - 'comprobante' para SIIGO
    - 'tipo_documento' para DIAN
    """

    if documento:
        entity = query.column_descriptions[0]["entity"]
        field = getattr(entity, field_name)
        return query.filter(field == documento)

    return query
