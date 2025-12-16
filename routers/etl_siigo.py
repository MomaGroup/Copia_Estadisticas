from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.connection import get_db
from app.core.security import get_current_user
from app.services.etl_siigo_service import procesar_siigo_excel

router = APIRouter()

@router.post("/{empresa_id}")
def cargar_siigo(
    empresa_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario = Depends(get_current_user)
):
    return procesar_siigo_excel(db, empresa_id, file)
