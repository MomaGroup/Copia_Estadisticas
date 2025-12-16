# app/core/periods.py

from datetime import date, timedelta


# ===============================================================
# Convertir periodo "YYYY-MM" → fecha inicial y fecha final
# ===============================================================
def periodo_a_rango(periodo: str):
    """
    Devuelve (fecha_inicio, fecha_fin)
    Ejemplo: "2024-03" → (2024-03-01, 2024-04-01)
    fecha_fin es EXCLUSIVA para facilitar filtros SQL:
    fecha >= inicio AND fecha < fin
    """

    if not periodo:
        return None, None

    try:
        year, month = map(int, periodo.split("-"))
    except:
        raise ValueError(f"Periodo inválido: {periodo}")

    fecha_inicio = date(year, month, 1)

    # calcular mes siguiente
    if month == 12:
        fecha_fin = date(year + 1, 1, 1)
    else:
        fecha_fin = date(year, month + 1, 1)

    return fecha_inicio, fecha_fin


# ===============================================================
# Devuelve el último día de un mes
# ===============================================================
def ultimo_dia_del_mes(year: int, month: int):
    if month == 12:
        return date(year, 12, 31)
    siguiente = date(year, month + 1, 1)
    return siguiente - timedelta(days=1)


# ===============================================================
# Periodo anterior
# ===============================================================
def periodo_anterior(periodo: str):
    year, month = map(int, periodo.split("-"))

    if month == 1:
        return f"{year - 1}-12"
    return f"{year}-{(month - 1):02d}"


# ===============================================================
# Periodo siguiente
# ===============================================================
def periodo_siguiente(periodo: str):
    year, month = map(int, periodo.split("-"))

    if month == 12:
        return f"{year + 1}-01"
    return f"{year}-{(month + 1):02d}"


# ===============================================================
# Validar formato del periodo
# ===============================================================
def validar_periodo(periodo: str):
    try:
        year, month = map(int, periodo.split("-"))
        assert 1 <= month <= 12
    except:
        raise ValueError(f"Periodo inválido: {periodo}")
    return True


# ===============================================================
# Crear lista de periodos entre 2 fechas
# ===============================================================
def periodos_entre(periodo_inicio: str, periodo_fin: str):
    validar_periodo(periodo_inicio)
    validar_periodo(periodo_fin)

    year_i, month_i = map(int, periodo_inicio.split("-"))
    year_f, month_f = map(int, periodo_fin.split("-"))

    periodos = []
    y, m = year_i, month_i

    while (y < year_f) or (y == year_f and m <= month_f):
        periodos.append(f"{y}-{m:02d}")
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1

    return periodos
