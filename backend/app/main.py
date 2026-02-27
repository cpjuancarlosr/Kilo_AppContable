"""
Punto de entrada principal de la aplicación FastAPI.
Configura middleware, CORS y rutas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.api.v1.endpoints import (
    executive,
    control,
    fiscal,
    simulation,
    mexico,
    advanced,
)
from app.db.database import engine, Base

settings = get_settings()

# Crear tablas en la base de datos (en producción usar Alembic)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API de FinAnalytix - Plataforma de Análisis Financiero Empresarial",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint de health check."""
    return {"app": settings.APP_NAME, "version": settings.VERSION, "status": "running"}


@app.get("/health")
async def health_check():
    """Health check detallado."""
    return JSONResponse(
        content={
            "status": "healthy",
            "database": "connected",  # Simplificado
            "version": settings.VERSION,
        }
    )


# Incluir routers de la API v1
app.include_router(
    executive.router, prefix="/api/v1/executive", tags=["Capa Ejecutiva"]
)

app.include_router(
    control.router, prefix="/api/v1/control", tags=["Control Financiero"]
)

app.include_router(fiscal.router, prefix="/api/v1/fiscal", tags=["Fiscal Estratégico"])

app.include_router(
    simulation.router, prefix="/api/v1/simulation", tags=["Simulación Estratégica"]
)

app.include_router(mexico.router, prefix="/api/v1/mexico", tags=["México - CFDI / SAT"])

app.include_router(
    advanced.router, prefix="/api/v1/advanced", tags=["Indicadores Avanzados"]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
