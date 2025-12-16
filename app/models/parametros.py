from sqlalchemy import Column, String, Boolean, TIMESTAMP, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.models.usuarios import Base

class ParametroSistema(Base):
    __tablename__ = "parametros_sistema"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clave = Column(String, unique=True, nullable=False)
    valor_numero = Column(Numeric)
    valor_texto = Column(String)
    descripcion = Column(String)
    creado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_en = Column(TIMESTAMP, server_default=func.now())
    actualizado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
