from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date
from app.core.periods import obtener_rango_periodo
from app.core.report_engine import ejecutar_sql

# Categorías oficiales del sistema
CATEGORIAS = [
    "E-DE", "E-DSS", "R-DE", "R-DNE", "O-EGR", "O-RCJ", "O-NBK"
]


# --------------------------------------------------------------
# UTILIDAD: estructura base con categorías vacías
# --------------------------------------------------------------
def inicializar_categorias():
    return {cat: [] for cat in CATEGORIAS}


# --------------------------------------------------------------
# PUBLICADOS – DIAN + BANCO
# --------------------------------------------------------------
def obtener_publicados(db: Session, empresa_id: str, inicio: date, fin: date):
    publicados = inicializar_categorias()

    # ---------------------- DIAN -------------------------
    sql_dian = """
        SELECT
            empresa_id,
            categoria_general,
            abreviatura_general,
            tipo_documento,
            cufe_cude,
            folio,
            prefijo,
            fecha_emision,
            fecha_recepcion,
            nit_emisor,
            nombre_emisor,
            nit_receptor,
            nombre_receptor,
            iva,
            total,
            estado
        FROM movimientos_dian
        WHERE empresa_id = :empresa_id
        AND fecha_emision BETWEEN :inicio AND :fin
        AND activo = TRUE;
    """

    filas_dian = ejecutar_sql(db, sql_dian, {
        "empresa_id": empresa_id,
        "inicio": inicio,
        "fin": fin
    })

    for f in filas_dian:
        categoria = f["categoria_general"]
        if categoria in publicados:
            publicados[categoria].append(f)

    # ---------------------- BANCO RCJ / EGR / NBK -------------------------
    sql_banco = """
        SELECT
            empresa_id,
            categoria_general,
            abreviatura_general,
            fecha,
            descripcion,
            valor,
            codigo_movimiento,
            oficina,
            saldo,
            json_fuente
        FROM movimientos_banco
        WHERE empresa_id = :empresa_id
        AND fecha BETWEEN :inicio AND :fin
        ORDER BY fecha ASC;
    """

    filas_banco = ejecutar_sql(db, sql_banco, {
        "empresa_id": empresa_id,
        "inicio": inicio,
        "fin": fin
    })

    for f in filas_banco:
        categoria = f["categoria_general"]
        if categoria in publicados:
            publicados[categoria].append(f)

    return publicados


# --------------------------------------------------------------
# CONTABILIZADOS – SIIGO
# --------------------------------------------------------------
def obtener_contabilizados(db: Session, empresa_id: str, inicio: date, fin: date):
    contabilizados = inicializar_categorias()

    sql_siigo = """
        SELECT
            empresa_id,
            categoria_general,
            abreviatura_general,
            codigo_contable,
            cuenta_contable,
            identificacion_tercero,
            nombre_tercero,
            comprobante,
            secuencia,
            fecha_elaboracion,
            descripcion_general,
            detalle,
            centro_costo,
            debito,
            credito,
            (debito - credito) AS valor
        FROM movimientos_siigo
        WHERE empresa_id = :empresa_id
        AND fecha_elaboracion BETWEEN :inicio AND :fin
        AND activo = TRUE;
    """

    filas = ejecutar_sql(db, sql_siigo, {
        "empresa_id": empresa_id,
        "inicio": inicio,
        "fin": fin
    })

    for f in filas:
        cat = f["categoria_general"]

        valor = f["valor"]

        # Reglas de naturaleza
        if cat == "O-RCJ" and valor <= 0:
            continue
        if cat == "O-EGR" and valor >= 0:
            continue
        # O-NBK siempre es válido
        # Resto de categorías pasan directo

        if cat in contabilizados:
            contabilizados[cat].append(f)

    return contabilizados


# --------------------------------------------------------------
# POR IDENTIFICAR – SIIGO códigos 1110 / 1120
# --------------------------------------------------------------
def obtener_pni(db: Session, empresa_id: str, inicio: date, fin: date):
    pni = inicializar_categorias()

    sql_pni = """
        SELECT
            empresa_id,
            categoria_general,
            abreviatura_general,
            codigo_contable,
            cuenta_contable,
            identificacion_tercero,
            nombre_tercero,
            comprobante,
            secuencia,
            fecha_elaboracion,
            descripcion_general,
            detalle,
            centro_costo,
            debito,
            credito,
            (debito - credito) AS valor
        FROM movimientos_siigo
        WHERE empresa_id = :empresa_id
        AND fecha_elaboracion BETWEEN :inicio AND :fin
        AND activo = TRUE
        AND (codigo_contable LIKE '1110%' OR codigo_contable LIKE '1120%');
    """

    filas = ejecutar_sql(db, sql_pni, {
        "empresa_id": empresa_id,
        "inicio": inicio,
        "fin": fin
    })

    for f in filas:
        cat = f["categoria_general"]
        valor = f["valor"]

        # Clasificación PNI:
        # NO RCJ válido
        if cat == "O-RCJ" and valor > 0:
            continue
        # NO EGR válido
        if cat == "O-EGR" and valor < 0:
            continue
        # NO NBK
        if cat == "O-NBK":
            continue

        # SIIGO no clasificado → PNI en su categoría
        if cat in pni:
            pni[cat].append(f)

    return pni


# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL DEL REPORTE DETALLADO
# --------------------------------------------------------------
def obtener_reporte_detallado(db: Session, empresa_id: str, periodo: str):
    if not empresa_id:
        raise HTTPException(status_code=400, detail="Debe enviar empresa_id")

    if not periodo:
        raise HTTPException(status_code=400, detail="Debe enviar periodo YYYY-MM")

    # Rango de fechas sincronizado con la matriz
    inicio, fin = obtener_rango_periodo(periodo)

    publicados = obtener_publicados(db, empresa_id, inicio, fin)
    contabilizados = obtener_contabilizados(db, empresa_id, inicio, fin)
    pni = obtener_pni(db, empresa_id, inicio, fin)

    return {
        "publicados": publicados,
        "contabilizados": contabilizados,
        "por_identificar": pni
    }
