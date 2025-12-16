import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
import unicodedata

from app.models.movimientos_dian import MovimientoDIAN
from app.models.diccionarios import DiccionarioDIAN
from app.models.errores_etl import ErrorETL
from app.models.cargas_log import CargaLog


# Normalizador
def normalizar(txt):
    if txt is None:
        return None
    txt = str(txt).upper().strip()
    txt = unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode()
    return " ".join(txt.split())


def procesar_dian_excel(db: Session, empresa_id: UUID, file):
    try:
        df = pd.read_excel(file.file, dtype=str)  # 1 sola hoja
    except Exception:
        raise HTTPException(status_code=400, detail="No se pudo leer archivo DIAN")

    registros = 0
    errores = []

    # Cargar diccionario DIAN
    dicc = {
        f"{normalizar(d.grupo)}_{normalizar(d.tipo_documento)}": d
        for d in db.query(DiccionarioDIAN)
                  .filter(DiccionarioDIAN.activo == True)
    }

    for idx, row in df.iterrows():
        try:
            grupo = normalizar(row.get("Grupo"))
            tipo_doc = normalizar(row.get("Tipo de documento"))
            llave = f"{grupo}_{tipo_doc}"

            if llave not in dicc:
                raise ValueError(f"No existe en diccionario DIAN: {grupo} / {tipo_doc}")

            regla = dicc[llave]

            total = float(row.get("Total") or 0)
            iva = float(row.get("IVA") or 0)
            total_bruto = total - iva

            fecha_em = row.get("Fecha Emisión")
            fecha_rec = row.get("Fecha Recepción")

            mov = MovimientoDIAN(
                empresa_id=empresa_id,

                grupo=grupo,
                tipo_documento=tipo_doc,

                fecha_emision=datetime.strptime(str(fecha_em), "%Y-%m-%d").date() if fecha_em else None,
                fecha_recepcion=datetime.strptime(str(fecha_rec), "%Y-%m-%d").date() if fecha_rec else None,

                cufe_cude=row.get("CUFE/CUDE"),
                folio=row.get("Folio"),
                divisa=row.get("Divisa"),

                nit_emisor=row.get("NIT Emisor"),
                nombre_emisor=row.get("Nombre Emisor"),
                nit_receptor=row.get("NIT Receptor"),
                nombre_receptor=row.get("Nombre Receptor"),

                total=total,
                iva=iva,
                total_bruto=total_bruto,

                abreviatura_general=regla.abreviatura_general,
                categoria_general=regla.categoria_general,
                tipo_reporte=regla.tipo_reporte
            )

            db.add(mov)
            registros += 1

        except Exception as e:
            errores.append({
                "fila": idx + 2,
                "error": str(e),
                "contenido": row.to_dict()
            })

    db.commit()

    # Crear Log
    log = CargaLog(
        empresa_id=empresa_id,
        tipo_archivo="DIAN",
        estado="procesado" if len(errores) == 0 else "error",
        archivo_nombre=file.filename,
        mensaje=f"{registros} procesados, {len(errores)} errores"
    )

    db.add(log)
    db.commit()

    # Guardar errores
    for err in errores:
        error = ErrorETL(
            empresa_id=empresa_id,
            tipo_archivo="DIAN",
            descripcion=err["error"],
            contenido=err["contenido"]
        )
        db.add(error)

    db.commit()

    return {"procesados": registros, "errores": errores}
