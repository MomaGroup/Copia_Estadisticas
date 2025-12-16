from sqlalchemy import Column, String, Numeric, Date, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database.connection import Base

class MovimientoBANCO(Base):
    __tablename__ = "movimientos_banco"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)

    fecha = Column(Date, nullable=False)
    descripcion = Column(String, nullable=False)
    valor = Column(Numeric, nullable=False)

    codigo_movimiento = Column(String)
    oficina = Column(String)
    saldo = Column(Numeric)

    abreviatura_general = Column(String, nullable=False)
    categoria_general = Column(String, nullable=False)
    tipo_reporte = Column(String, nullable=False)

    json_fuente = Column(JSON, nullable=False)

    creado_en = Column(TIMESTAMP, server_default=func.now())
