from sqlalchemy import Column, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.models.empresas import Base

class DiccionarioDIAN(Base):
    __tablename__ = "diccionario_dian"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grupo = Column(String, nullable=False)
    tipo_documento = Column(String, nullable=False)
    nombre_generico = Column(String, nullable=False)
    abreviatura_general = Column(String, nullable=False)
    categoria_general = Column(String, nullable=False)
    tipo_reporte = Column(String, nullable=False)
    activo = Column(Boolean, default=True)


class DiccionarioSIIGO(Base):
    __tablename__ = "diccionario_siigo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    comprobante = Column(String, nullable=False)
    abreviatura_general = Column(String, nullable=False)
    categoria_general = Column(String, nullable=False)
    tipo_reporte = Column(String, nullable=False)
    activo = Column(Boolean, default=True)
