from sqlalchemy import Column, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UsuarioEmpresa(Base):
    __tablename__ = "usuarios_empresas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    creado_en = Column(TIMESTAMP, server_default=func.now())
