"""
Configuración central de la aplicación FinAnalytix.
Maneja variables de entorno y configuración del sistema.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno."""

    # Aplicación
    APP_NAME: str = "FinAnalytix"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # Seguridad
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/finanalytix"

    # Configuración fiscal específica para México
    COUNTRY_CODE: str = "MX"
    COUNTRY_NAME: str = "México"
    CURRENCY: str = "MXN"

    # Tasas de impuestos México 2024
    VAT_RATE: float = 0.16  # IVA tasa general
    VAT_RATE_BORDER: float = 0.08  # IVA fronterizo
    INCOME_TAX_RATE: float = 0.30  # ISR persona moral
    INCOME_TAX_RATE_INDIVIDUAL: float = 0.35  # ISR persona física (top)
    FLAT_TAX_RATE: float = 0.075  # IEPS (tasa base, varía por producto)
    PAYROLL_TAX_RATE: float = 0.03  # ISN aproximado (varía por estado)

    # Retenciones ISR México
    ISR_WITHHOLDING_DIVIDENDS: float = 0.10  # Dividendos
    ISR_WITHHOLDING_INTEREST: float = 0.20  # Intereses
    ISR_WITHHOLDING_RENT: float = 0.10  # Arrendamiento
    ISR_WITHHOLDING_FEES: float = 0.10  # Honorarios

    # Configuraciones CFDI
    CFDI_VERSION: str = "4.0"
    CFDI_PAC: str = "sw_sapien"  # Proveedor autorizado de certificación

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instancia cacheada de configuración."""
    return Settings()
