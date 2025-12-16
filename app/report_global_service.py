# app/services/report_global_service.py
from sqlalchemy.orm import Session
from app.database.connection import get_db
from fastapi import Depends

from app.core.periods import get_period_range
from app.core.filters import apply_filters_global
from sqlalchemy import text


CATEGORIAS = ["E-DE", "E-DSS", "R-DE", "R-DNE", "O-EGR", "O-RCJ", "O-NBK"]


def calcular_indicadores_empresa(data_empresa):
    """
    Calcula avance_general, rezago (IRZ) y calidad (ICP) según totales.
    """
    pub_total = data_empresa["resumen"]["pub_total"]
    con_total = data_empresa["resumen"]["con_total"]
    pnc_total = data_empresa["resumen"]["pnc_total"]
    pni_total = data_empresa["resumen"]["pni_total"]

    avance = con_total / pub_total if pub_total > 0 else 1
    rezago = pnc_total / pub_total if pub_total > 0 else 0
    calidad = 1 - (pni_total / pub_total) if pub_total > 0 else 1

    return avance, rezago, calidad


def obtener_pni_por_categoria(db: Session, empresa_id: str, fecha_ini, fecha_fin):
    """
    Obtiene los PNI (movimientos SIIGO con código 1110/1120 y sin categoría válida)
    agrupados por categoría contable.
    """
    sql = text("""
        SELECT 
            empresa_id,
            categoria_general,
            COUNT(*) AS pni
        FROM movimientos_siigo
        WHERE empresa_id = :empresa
          AND fecha BETWEEN :f_ini AND :f_fin
          AND (codigo_contable LIKE '1110%' OR codigo_contable LIKE '1120%')
          AND categoria_general IS NULL
        GROUP BY empresa_id, categoria_general;
    """)

    rows = db.execute(sql, {"empresa": empresa_id, "f_ini": fecha_ini, "f_fin": fecha_fin}).fetchall()

    result = {cat: 0 for cat in CATEGORIAS}
    for r in rows:
        result[r.categoria_general] = r.pni if r.categoria_general else 0

    return result


def obtener_matriz_sql(db: Session, fecha_ini, fecha_fin):
    """
    Obtiene los valores PUB/CON/PNC desde la vista oficial.
    """
    sql = text("""
        SELECT *
        FROM vista_reporte_matriz
        WHERE fecha BETWEEN :f_ini AND :f_fin;
    """)
    return db.execute(sql, {"f_ini": fecha_ini, "f_fin": fecha_fin}).fetchall()


def build_empresa_json(row, pni_dict):
    """
    Construye la estructura JSON final por empresa.
    """

    categorias = {}
    resumen = {"pub_total": 0, "con_total": 0, "pnc_total": 0, "pni_total": 0}

    for cat in CATEGORIAS:
        pub = getattr(row, f"pub_{cat.lower().replace('-', '_')}", 0)
        con = getattr(row, f"con_{cat.lower().replace('-', '_')}", 0)
        pnc = getattr(row, f"pnc_{cat.lower().replace('-', '_')}", 0)
        pni = pni_dict.get(cat, 0)

        avance_cat = con / pub if pub > 0 else 1

        categorias[cat] = {
            "pub": pub,
            "con": con,
            "pnc": pnc,
            "pni": pni,
            "avance": avance_cat
        }

        resumen["pub_total"] += pub
        resumen["con_total"] += con
        resumen["pnc_total"] += pnc
        resumen["pni_total"] += pni

    avance_general, rezago, calidad = calcular_indicadores_empresa({"resumen": resumen})

    empresa_json = {
        "empresa_id": row.empresa_id,
        "empresa": row.empresa,
        "categorias": categorias,
        "avance_general": avance_general,
        "rezago": rezago,
        "calidad": calidad,
        "resumen": resumen
    }

    return empresa_json


def reporte_global(periodo: str, db: Session):
    """
    Servicio principal del Reporte Global Multiempresa.
    """

    fecha_ini, fecha_fin = get_period_range(periodo)

    matriz_rows = obtener_matriz_sql(db, fecha_ini, fecha_fin)

    empresas_json = []
    totales = {"pub_total": 0, "con_total": 0, "pnc_total": 0, "pni_total": 0}

    for row in matriz_rows:

        pni_dict = obtener_pni_por_categoria(db, row.empresa_id, fecha_ini, fecha_fin)

        empresa_json = build_empresa_json(row, pni_dict)

        for key in totales:
            totales[key] += empresa_json["resumen"][key]

        empresas_json.append(empresa_json)

    # Indicadores consolidados
    if totales["pub_total"] > 0:
        avance_general = totales["con_total"] / totales["pub_total"]
        rezago = totales["pnc_total"] / totales["pub_total"]
        calidad = 1 - (totales["pni_total"] / totales["pub_total"])
    else:
        avance_general = 1
        rezago = 0
        calidad = 1

    totales["avance_general"] = avance_general
    totales["rezago"] = rezago
    totales["calidad"] = calidad

    return {
        "empresas": empresas_json,
        "totales": totales
    }
