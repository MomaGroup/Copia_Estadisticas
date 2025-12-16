from sqlalchemy import Column, String, Numeric, Date, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database.connection import Base

class MovimientoDIAN(Base):
    __tablename__ = "movimientos_dian"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)

    grupo = Column(String, nullable=False)
    tipo_documento = Column(String, nullable=False)

    fecha_emision = Column(Date)
    fecha_recepcion = Column(Date)

    cufe_cude = Column(String)
    folio = Column(String)
    divisa = Column(String)

    nit_emisor = Column(String)
    nombre_emisor = Column(String)
    nit_receptor = Column(String)
    nombre_receptor = Column(String)

    total = Column(Numeric, nullable=False)
    iva = Column(Numeric, nullable=False)
    total_bruto = Column(Numeric, nullable=False)

    abreviatura_general = Column(String, nullable=False)
    categoria_general = Column(String, nullable=False)
    tipo_reporte = Column(String, nullable=False)

    creado_en = Column(TIMESTAMP, server_default=func.now())
