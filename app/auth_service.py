from sqlalchemy.orm import Session
from app.models.usuarios import Usuario
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_password(password_plano: str, password_hash: str):
    return pwd_context.verify(password_plano, password_hash)

def hash_password(password: str):
    return pwd_context.hash(password)

def autenticar_usuario(db: Session, email: str, password: str):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        return None

    if not verificar_password(password, usuario.password):
        return None

    return usuario
