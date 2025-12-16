from sqlalchemy import Column, String, Numeric, Date, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database.connection import Base

class MovimientoSIIGO(Base):
    __tablename__ = "movimientos_siigo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)

    fecha_elaboracion = Column(Date, nullable=False)
    comprobante = Column(String, nullable=False)
    secuencia = Column(String)
    descripcion = Column(String)
    detalle = Column(String)

    codigo_contable = Column(String)
    cuenta_contable = Column(String)
    identificacion = Column(String)
    nombre_tercero = Column(String)
    centro_costo = Column(String)

    debito = Column(Numeric)
    credito = Column(Numeric)
    valor = Column(Numeric, nullable=False)

    abreviatura_general = Column(String, nullable=False)
    categoria_general = Column(String, nullable=False)
    tipo_reporte = Column(String, nullable=False)

    creado_en = Column(TIMESTAMP, server_default=func.now())
