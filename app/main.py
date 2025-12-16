from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth, usuarios, empresas, diccionarios, etl

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(empresas.router, prefix="/empresas", tags=["Empresas"])
app.include_router(diccionarios.router, prefix="/diccionarios", tags=["Diccionarios"])
app.include_router(etl.router, prefix="/etl", tags=["ETL"])

@app.get("/")
def root():
    return {"status": "ok", "msg": "Backend funcionando"}

from app.routers import etl_siigo

app.include_router(etl_siigo.router, prefix="/etl/siigo", tags=["ETL SIIGO"])

from app.routers import etl_dian

app.include_router(etl_dian.router, prefix="/etl/dian", tags=["ETL DIAN"])

from app.routers import etl_banco

app.include_router(etl_banco.router, prefix="/etl/banco", tags=["ETL BANCO"])
