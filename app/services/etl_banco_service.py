import json
import unicodedata
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.movimientos_banco import MovimientoBANCO
from app.models.errores_etl import ErrorETL
from app.models.cargas_log import CargaLog


# ==========================
# Normalización avanzada
# ==========================
def normalizar(texto: str):
    if texto is None:
        return ""
    texto = str(texto).upper().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode()
    texto = "".join(ch for ch in texto if ch.isalnum() or ch == " ")
    return " ".join(texto.split())


# ==========================================================================================
# DICCIONARIO BANCARIO (rellenado por ti, aquí se usa tu definición de conceptos NBK)
# ==========================================================================================
diccionario_banco = [
    # Pega aquí literalmente todas las cadenas de tu captura
]

dicc_normalizado = [normalizar(x) for x in diccionario_banco]


# ==========================
# ETL para archivo JSON
# ==========================
def procesar_banco_json(db: Session, empresa_id: UUID, file):
    try:
        contenido = json.load(file.file)
    except Exception:
        raise HTTPException(400, "No se pudo leer el archivo JSON de bancos")

    registros = 0
    errores = []

    for idx, item in enumerate(contenido):

        try:
            descripcion_raw = item.get("descripcion") or item.get("Descripcion") or ""
            fecha_raw = item.get("fecha") or item.get("Fecha")
            valor_raw = item.get("valor") or item.get("Valor")

            descripcion = normalizar(descripcion_raw)
            valor = float(valor_raw)

            # ======================
            # CLASIFICACIÓN
            # ======================

            # 1. Si coincide con el diccionario → B-NBK
            categoria = None
            for concepto in dicc_normalizado:
                if concepto in descripcion:
                    categoria = "B-NBK"
                    break

            # 2. Si NO coincide → depende del signo
            if categoria is None:
                if valor > 0:
                    categoria = "B-RCJ"
                else:
                    categoria = "B-EGR"

            abreviatura = categoria
            tipo_reporte = "Indicadores"

            # ======================
            # Fecha
            # ======================
            fecha = datetime.strptime(str(fecha_raw), "%Y-%m-%d").date()

            # ======================
            # Crear registro
            # ======================
            mov = MovimientoBANCO(
                empresa_id=empresa_id,
                fecha=fecha,
                descripcion=descripcion_raw,
                valor=valor,

                codigo_movimiento=item.get("codigo_movimiento"),
                oficina=item.get("oficina"),
                saldo=item.get("saldo"),

                abreviatura_general=abreviatura,
                categoria_general=categoria,
                tipo_reporte=tipo_reporte,

                json_fuente=item
            )

            db.add(mov)
            registros += 1

        except Exception as e:
            errores.append({
                "fila": idx + 1,
                "error": str(e),
                "contenido": item
            })

    db.commit()

    # ======================
    # Registrar log
    # ======================
    log = CargaLog(
        empresa_id=empresa_id,
        tipo_archivo="BANCO",
        estado="procesado" if len(errores) == 0 else "error",
        archivo_nombre=file.filename,
        mensaje=f"{registros} procesados, {len(errores)} errores"
    )
    db.add(log)
    db.commit()

    # Registrar errores
    for err in errores:
        error = ErrorETL(
            empresa_id=empresa_id,
            tipo_archivo="BANCO",
            descripcion=err["error"],
            contenido=err["contenido"]
        )
        db.add(error)

    db.commit()

    return {"procesados": registros, "errores": errores}
