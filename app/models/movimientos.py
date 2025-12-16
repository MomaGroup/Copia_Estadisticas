from sqlalchemy import Column, String, Boolean, TIMESTAMP, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.models.empresas import Base

class Movimiento(Base):
    __tablename__ = "movimientos_unificados"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    estado = Column(String, nullable=False)
    abreviatura_general = Column(String, nullable=False)
    categoria_general = Column(String, nullable=False)
    tipo_reporte = Column(String, nullable=False)
    modulo_origen = Column(String, nullable=False)
    descripcion_general = Column(String)
    valor = Column(Numeric, nullable=False)
