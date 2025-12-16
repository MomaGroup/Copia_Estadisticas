from sqlalchemy.orm import Session
from app.models.movimientos_dian import MovDian
from app.models.movimientos_banco import MovBanco
from app.models.movimientos_siigo import MovSiigo
from app.core.periods import apply_period_filter


# ------------------------------------------------------------
#  CLASIFICADOR DE ESTADOS: PUB / CON / PNI
# ------------------------------------------------------------

def clasificar_estado_siigo(mov):
    """
    Clasifica los movimientos de SIIGO según la naturaleza válida.
    - CON → si la naturaleza es correcta según categoría
    - PNI → categoría válida pero naturaleza inválida
    - PUB → NO aplica para SIIGO (solo se publica DIAN y Banco)
    """

    valor = (mov.debito or 0) - (mov.credito or 0)
    categoria = mov.categoria_general

    # --- RCJ (debe ser valor positivo)
    if categoria == "O-RCJ":
        if valor > 0:
            return "CON"
        else:
            return "PNI"

    # --- EGR (debe ser valor negativo)
    if categoria == "O-EGR":
        if valor < 0:
            return "CON"
        else:
            return "PNI"

    # --- NBK (siempre CON por reglas de negocio)
    if categoria == "O-NBK":
        return "CON"

    # Categoría no contemplada
    return "PNI"


def clasificar_estado_dian(_mov):
    """DIAN siempre es PUBLICADO"""
    return "PUB"


def clasificar_estado_banco(mov):
    """
    Banco:
    - RCJ (valor > 0) → PUB
    - EGR (valor < 0) → PUB
    - NBK → 1 PUB por JSON (ya viene consolidado desde SQL)
    """
    if mov.categoria_general in ("B-RCJ", "B-EGR", "B-NBK"):
        return "PUB"

    return "PNI"


# ------------------------------------------------------------
#  SERVICIO PRINCIPAL DE REPORTE CON FILTROS
# ------------------------------------------------------------

def generar_reporte_filtrado(db: Session, empresa_id=None, fecha_inicio=None, fecha_fin=None):
    """
    Devuelve el estado consolidado PUB / CON / PNI para cada categoría.
    Incluye:
    - DIAN
    - BANCO
    - SIIGO
    """

    # Aplicar filtros de fechas o periodos
    filtros_siigo = apply_period_filter(MovSiigo.fecha, fecha_inicio, fecha_fin)
    filtros_dian = apply_period_filter(MovDian.fecha_emision, fecha_inicio, fecha_fin)
    filtros_banco = apply_period_filter(MovBanco.fecha, fecha_inicio, fecha_fin)

    if empresa_id:
        filtros_siigo.append(MovSiigo.empresa_id == empresa_id)
        filtros_dian.append(MovDian.empresa_id == empresa_id)
        filtros_banco.append(MovBanco.empresa_id == empresa_id)

    # ------------------------------------------------------------
    # 1. Obtener movimientos
    # ------------------------------------------------------------
    movs_siigo = db.query(MovSiigo).filter(*filtros_siigo).all()
    movs_dian = db.query(MovDian).filter(*filtros_dian).all()
    movs_banco = db.query(MovBanco).filter(*filtros_banco).all()

    # ------------------------------------------------------------
    # 2. Estructura base del reporte (todas las categorías posibles)
    # ------------------------------------------------------------

    categorias = [
        "E-DE", "E-DSS",
        "R-DE", "R-DNE",
        "O-EGR", "O-RCJ", "O-NBK"
    ]

    resultado = {cat: {"PUB": 0, "CON": 0, "PNI": 0} for cat in categorias}

    # ------------------------------------------------------------
    # 3. Procesar DIAN
    # ------------------------------------------------------------
    for mov in movs_dian:
        cat = mov.categoria_general
        if cat in resultado:
            estado = clasificar_estado_dian(mov)
            resultado[cat][estado] += 1

    # ------------------------------------------------------------
    # 4. Procesar BANCO
    # ------------------------------------------------------------
    for mov in movs_banco:
        cat = mov.categoria_general
        if cat in resultado:
            estado = clasificar_estado_banco(mov)
            resultado[cat][estado] += 1

    # ------------------------------------------------------------
    # 5. Procesar SIIGO
    # ------------------------------------------------------------
    comprobantes_vistos = set()

    for mov in movs_siigo:
        cat = mov.categoria_general
        if cat not in resultado:
            continue

        # Agrupación por comprobante
        comp_key = f"{mov.comprobante}-{mov.secuencia}"

        if comp_key in comprobantes_vistos:
            continue

        comprobantes_vistos.add(comp_key)

        estado = clasificar_estado_siigo(mov)
        resultado[cat][estado] += 1

    return resultado
