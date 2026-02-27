"""
Schemas Pydantic para validación y serialización de datos.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============== COMPANY SCHEMAS ==============


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    tax_id: str = Field(..., min_length=1, max_length=50)
    legal_name: Optional[str] = None
    country: str = "MX"
    currency: str = "MXN"


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    is_active: bool


# ============== USER SCHEMAS ==============


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    company_id: UUID


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    role: str
    is_active: bool
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ============== ACCOUNT SCHEMAS ==============


class AccountBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    account_type: str  # asset, liability, equity, income, expense
    parent_id: Optional[UUID] = None


class AccountCreate(AccountBase):
    pass


class AccountResponse(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    level: int
    is_leaf: bool
    balance_type: str


# ============== JOURNAL ENTRY SCHEMAS ==============


class JournalEntryLineBase(BaseModel):
    account_id: UUID
    description: Optional[str] = None
    debit: Decimal = Field(default=Decimal("0"), ge=0)
    credit: Decimal = Field(default=Decimal("0"), ge=0)


class JournalEntryLineCreate(JournalEntryLineBase):
    pass


class JournalEntryLineResponse(JournalEntryLineBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_code: Optional[str] = None
    account_name: Optional[str] = None


class JournalEntryBase(BaseModel):
    entry_number: str = Field(..., min_length=1, max_length=50)
    date: date
    concept: str
    reference: Optional[str] = None


class JournalEntryCreate(JournalEntryBase):
    lines: List[JournalEntryLineCreate] = Field(..., min_length=2)


class JournalEntryResponse(JournalEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    source: str
    is_adjustment: bool
    created_at: datetime
    total_debit: Decimal
    total_credit: Decimal
    lines: List[JournalEntryLineResponse]


# ============== FINANCIAL DASHBOARD SCHEMAS ==============


class ExecutiveMetrics(BaseModel):
    """Métricas ejecutivas para dashboard."""

    revenue_current: Decimal
    revenue_previous: Decimal
    revenue_change_pct: float

    net_income_current: Decimal
    net_income_previous: Decimal
    net_income_change_pct: float

    ebitda_current: Decimal
    ebitda_margin_pct: float

    cash_balance: Decimal
    cash_runway_months: Optional[float]

    accounts_receivable: Decimal
    accounts_payable: Decimal
    working_capital: Decimal

    alerts: List[Dict[str, Any]]


class FinancialRatios(BaseModel):
    """Ratios financieros clave."""

    current_ratio: Optional[float]
    quick_ratio: Optional[float]
    debt_to_equity: Optional[float]
    roa: Optional[float]
    roe: Optional[float]
    gross_margin: Optional[float]
    operating_margin: Optional[float]
    net_margin: Optional[float]
    asset_turnover: Optional[float]
    inventory_turnover: Optional[float]


class CashConversionCycle(BaseModel):
    """Ciclo de conversión de efectivo."""

    dso: float  # Días de ventas pendientes
    dio: float  # Días de inventario
    dpo: float  # Días de cuentas por pagar
    ccc: float  # Ciclo total


# ============== SCENARIO SCHEMAS ==============


class ScenarioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scenario_type: str  # growth, pricing, expansion, financing
    projection_months: int = Field(default=12, ge=1, le=60)


class ScenarioParameters(BaseModel):
    """Parámetros de simulación."""

    growth_rate: float = Field(default=0, ge=-1, le=5)  # -100% a 500%
    price_change: float = Field(default=0, ge=-0.5, le=1)  # -50% a 100%
    cost_change: float = Field(default=0, ge=-0.5, le=1)
    new_financing: Decimal = Field(default=Decimal("0"), ge=0)
    interest_rate: float = Field(default=0, ge=0, le=1)


class ScenarioCreate(ScenarioBase):
    base_period_start: date
    base_period_end: date
    parameters: ScenarioParameters


class ScenarioResultData(BaseModel):
    period_month: int
    projected_revenue: Decimal
    projected_expenses: Decimal
    projected_ebitda: Decimal
    projected_net_income: Decimal
    projected_cash: Decimal


class ScenarioResponse(ScenarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    base_period_start: date
    base_period_end: date
    parameters: ScenarioParameters
    results: List[ScenarioResultData]
    created_at: datetime


# ============== TAX ANALYSIS SCHEMAS ==============


class TaxSummary(BaseModel):
    """Resumen de carga fiscal."""

    period_start: date
    period_end: date
    revenue: Decimal
    taxable_income: Decimal
    income_tax: Decimal
    vat_collected: Decimal
    vat_paid: Decimal
    vat_net: Decimal
    other_taxes: Decimal
    total_tax: Decimal
    effective_tax_rate: float


class TaxProjection(BaseModel):
    """Proyección fiscal a 12 meses."""

    month: int
    projected_revenue: Decimal
    projected_taxable_income: Decimal
    projected_income_tax: Decimal
    projected_vat: Decimal
    projected_total_tax: Decimal
    cumulative_tax: Decimal


# ============== ANALYSIS SCHEMAS ==============


class VerticalAnalysisItem(BaseModel):
    account_code: str
    account_name: str
    amount: Decimal
    percentage: float


class VerticalAnalysis(BaseModel):
    """Análisis vertical del estado de resultados."""

    period_start: date
    period_end: date
    revenue: Decimal
    items: List[VerticalAnalysisItem]


class HorizontalAnalysisItem(BaseModel):
    account_code: str
    account_name: str
    current_amount: Decimal
    previous_amount: Decimal
    absolute_change: Decimal
    percentage_change: float


class HorizontalAnalysis(BaseModel):
    """Análisis horizontal comparativo."""

    current_period_start: date
    current_period_end: date
    previous_period_start: date
    previous_period_end: date
    items: List[HorizontalAnalysisItem]


class BreakEvenAnalysis(BaseModel):
    """Análisis de punto de equilibrio."""

    period_start: date
    period_end: date
    fixed_costs: Decimal
    variable_costs: Decimal
    contribution_margin: Decimal
    contribution_margin_pct: float
    break_even_revenue: Decimal
    break_even_units: Optional[float]
    safety_margin_pct: float
    current_revenue: Decimal


class MarginAnalysis(BaseModel):
    """Análisis de márgenes detallado."""

    period_start: date
    period_end: date
    revenue: Decimal
    cost_of_goods_sold: Decimal
    gross_profit: Decimal
    gross_margin_pct: float
    operating_expenses: Decimal
    operating_income: Decimal
    operating_margin_pct: float
    ebitda: Decimal
    ebitda_margin_pct: float
    net_income: Decimal
    net_margin_pct: float


# ============== SCHEMAS ESPECÍFICOS PARA MÉXICO ==============


class EmpresaMXBase(BaseModel):
    """Datos base de empresa mexicana."""

    rfc: str = Field(..., min_length=12, max_length=13)
    razon_social: str = Field(..., min_length=1, max_length=255)
    nombre_comercial: Optional[str] = None
    regimen_fiscal: str = Field(..., min_length=3, max_length=3)
    codigo_postal: str = Field(..., min_length=5, max_length=5)
    calle: Optional[str] = None
    numero_exterior: Optional[str] = None
    numero_interior: Optional[str] = None
    colonia: Optional[str] = None
    municipio: Optional[str] = None
    estado: Optional[str] = None


class EmpresaMXCreate(EmpresaMXBase):
    company_id: UUID


class EmpresaMXResponse(EmpresaMXBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    es_zona_fronteriza: bool
    activa_en_sat: bool
    created_at: datetime


class CFDIConceptoBase(BaseModel):
    """Concepto de CFDI."""

    clave_prod_serv: str = Field(..., min_length=8, max_length=8)
    clave_unidad: str = Field(..., min_length=1, max_length=3)
    descripcion: str
    cantidad: Decimal = Field(..., gt=0)
    valor_unitario: Decimal = Field(..., ge=0)
    descuento: Decimal = Field(default=Decimal("0"), ge=0)


class CFDIConceptoCreate(CFDIConceptoBase):
    pass


class CFDIConceptoResponse(CFDIConceptoBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    importe: Decimal
    iva_tasa: Decimal
    iva_importe: Decimal
    ieps_tasa: Decimal
    ieps_importe: Decimal


class CFDIBase(BaseModel):
    """Datos base de CFDI."""

    tipo_comprobante: str = Field(..., pattern="^[IETNP]$")
    receptor_rfc: str = Field(..., min_length=12, max_length=13)
    receptor_nombre: str
    receptor_regimen_fiscal: str = Field(..., min_length=3, max_length=3)
    receptor_domicilio_fiscal: str = Field(..., min_length=5, max_length=5)
    receptor_uso_cfdi: str = Field(default="G03", min_length=3, max_length=3)
    forma_pago: Optional[str] = None
    metodo_pago: str = Field(default="PUE")


class CFDICreate(CFDIBase):
    conceptos: List[CFDIConceptoCreate] = Field(..., min_length=1)


class CFDIResponse(CFDIBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    uuid: Optional[str]
    serie: Optional[str]
    folio: Optional[str]
    estado: str
    fecha_emision: datetime
    subtotal: Decimal
    impuestos_trasladados: Decimal
    impuestos_retenidos: Decimal
    total: Decimal
    conceptos: List[CFDIConceptoResponse]
    xml_timbrado: Optional[str]


class RetencionISRBase(BaseModel):
    """Retención de ISR."""

    ejercicio: int = Field(..., ge=2020, le=2030)
    mes: int = Field(..., ge=1, le=12)
    monto_operacion: Decimal = Field(..., ge=0)
    monto_retencion: Decimal = Field(..., ge=0)
    tipo_retencion: str  # arrendamiento, honorarios, dividendos
    cfdi_uuid: Optional[str] = None
    folio_constancia: Optional[str] = None
    fecha_constancia: Optional[date] = None


class RetencionISRCreate(RetencionISRBase):
    company_id: UUID
    retencion_rfc: str
    retencion_nombre: str


class RetencionISRResponse(RetencionISRBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    retencion_rfc: str
    retencion_nombre: str
    acreditada: bool
    created_at: datetime


class DIOTOperacionBase(BaseModel):
    """Operación DIOT."""

    ejercicio: int
    mes: int
    proveedor_rfc: str
    proveedor_nombre: str
    valor_neto: Decimal
    iva_acreditable: Decimal
    iva_no_acreditable: Decimal = Decimal("0")


class DIOTOperacionCreate(DIOTOperacionBase):
    company_id: UUID


class DIOTOperacionResponse(DIOTOperacionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    monto_total: Decimal
    es_exceso: bool
    cfdi_uuid: Optional[str]
    created_at: datetime


class DIOTResumen(BaseModel):
    """Resumen mensual de DIOT."""

    ejercicio: int
    mes: int
    total_proveedores: int
    total_operaciones: Decimal
    total_iva_acreditable: Decimal
    total_iva_no_acreditable: Decimal


class CalculoFiscalMX(BaseModel):
    """Resultado de cálculo fiscal mexicano."""

    periodo: str
    ingresos_gravados: Decimal
    ingresos_exentos: Decimal
    deducciones_autorizadas: Decimal
    base_gravable_isr: Decimal
    isr_causado: Decimal
    isr_retenido: Decimal
    isr_a_cargo: Decimal
    iva_trasladado: Decimal
    iva_acreditable: Decimal
    iva_a_cargo: Decimal
    ieps_causado: Decimal


class EstadoCuentaSAT(BaseModel):
    """Estado de cuenta de contribuyente (proyección)."""

    rfc: str
    razon_social: str
    situacion_del_contribuyente: str  # Activo, Suspendido, etc.
    supuestos: List[str]  # Supuestos de inscripción al padrón
    actividades_economicas: List[str]
    obligaciones: List[str]
    regimenes: List[str]
