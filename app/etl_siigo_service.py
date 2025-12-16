import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
import unicodedata

from app.models.movimientos_siigo import MovimientoSIIGO
from app.models.diccionarios import DiccionarioSIIGO
from app.models.errores_etl import ErrorETL
from app.models.cargas_log import CargaLog


# ==========================
# Normalizador de texto
# ==========================
def normalizar(texto):
    if texto is None:
        return None
    texto = str(texto).upper().strip()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode()
    return " ".join(texto.split())


# ==========================
# ETL SIIGO
# ==========================
def procesar_siigo_excel(db: Session, empresa_id: UUID, file):
    try:
        df = pd.read_excel(file.file, dtype=str)  # lectura exacta del Excel
    except Exception:
        raise HTTPException(400, "No se pudo leer el archivo Excel SIIGO.")

    registros = 0
    errores = []

    # Cargar diccionario SIIGO de la empresa
    dicc = {
        normalizar(item.comprobante): item
        for item in db.query(DiccionarioSIIGO)
                      .filter(DiccionarioSIIGO.empresa_id == empresa_id,
                              DiccionarioSIIGO.activo == True)
    }

    for idx, row in df.iterrows():
        try:
            comprobante = normalizar(row.get("Comprobante"))
            fecha_elab = row.get("Fecha elaboración")
            debito = row.get("Débito")
            credito = row.get("Crédito")

            if comprobante not in dicc:
                raise ValueError(f"Comprobante no existe en diccionario SIIGO: {comprobante}")

            regla = dicc[comprobante]

            fecha = datetime.strptime(str(fecha_elab), "%Y-%m-%d").date()

            deb = float(debito) if debito else 0
            cre = float(credito) if credito else 0
            valor = deb - cre  # regla confirmada

            mov = MovimientoSIIGO(
                empresa_id=empresa_id,
                fecha_elaboracion=fecha,
                comprobante=comprobante,
                secuencia=row.get("Secuencia"),
                descripcion=row.get("Descripción"),
                detalle=row.get("Detalle"),

                codigo_contable=row.get("Código contable"),
                cuenta_contable=row.get("Cuenta contable"),
                identificacion=row.get("Identificación"),
                nombre_tercero=row.get("Nombre tercero"),
                centro_costo=row.get("Centro de costo"),

                debito=deb,
                credito=cre,
                valor=valor,

                abreviatura_general=regla.abreviatura_general,
                categoria_general=regla.categoria_general,
                tipo_reporte=regla.tipo_reporte
            )

            db.add(mov)
            registros += 1

        except Exception as e:
            errores.append({"fila": idx + 2, "error": str(e), "contenido": row.to_dict()})

    db.commit()

    # Registrar log
    log = CargaLog(
        empresa_id=empresa_id,
        tipo_archivo="SIIGO",
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
            tipo_archivo="SIIGO",
            descripcion=err["error"],
            contenido=err["contenido"]
        )
        db.add(error)

    db.commit()

    return {"procesados": registros, "errores": errores}
