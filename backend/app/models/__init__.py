"""
Modelos de base de datos para FinAnalytix.
Implementación multiempresa con soporte completo de análisis financiero.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Date,
    Numeric,
    ForeignKey,
    Boolean,
    Text,
    Enum,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class AccountType(str, enum.Enum):
    """Tipos de cuentas contables."""

    ASSET = "activo"
    LIABILITY = "pasivo"
    EQUITY = "patrimonio"
    INCOME = "ingreso"
    EXPENSE = "gasto"


class Company(Base):
    """Empresa cliente del sistema (multi-tenant)."""

    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    tax_id = Column(String(50), nullable=False, unique=True)
    legal_name = Column(String(255))
    address = Column(Text)
    country = Column(String(2), default="MX")
    currency = Column(String(3), default="MXN")
    fiscal_year_start = Column(Integer, default=1)  # Mes de inicio
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relaciones
    users = relationship("User", back_populates="company")
    accounts = relationship("Account", back_populates="company")
    journal_entries = relationship("JournalEntry", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")
    scenarios = relationship("Scenario", back_populates="company")

    __table_args__ = (Index("idx_company_tax_id", "tax_id"),)


class User(Base):
    """Usuarios del sistema por empresa."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default="analyst")  # admin, analyst, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Relaciones
    company = relationship("Company", back_populates="users")

    __table_args__ = (
        UniqueConstraint("company_id", "email", name="uq_user_company_email"),
    )


class Account(Base):
    """Catálogo de cuentas contables."""

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    level = Column(Integer, default=1)  # Nivel en el árbol
    is_leaf = Column(Boolean, default=True)  # Cuenta de último nivel
    balance_type = Column(String(10), default="debit")  # debit/credit
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    company = relationship("Company", back_populates="accounts")
    parent = relationship("Account", remote_side=[id], backref="children")
    entries = relationship("JournalEntryLine", back_populates="account")

    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_account_company_code"),
        Index("idx_account_company_type", "company_id", "account_type"),
    )


class JournalEntry(Base):
    """Pólizas contables (asientos diario)."""

    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    entry_number = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    concept = Column(Text, nullable=False)
    reference = Column(String(255))  # Referencia externa
    source = Column(String(50), default="manual")  # manual, import, system
    is_adjustment = Column(Boolean, default=False)
    is_closing = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    company = relationship("Company", back_populates="journal_entries")
    lines = relationship(
        "JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("company_id", "entry_number", name="uq_entry_company_number"),
        Index("idx_entry_company_date", "company_id", "date"),
    )


class JournalEntryLine(Base):
    """Líneas de póliza (movimientos)."""

    __tablename__ = "journal_entry_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id = Column(
        UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False
    )
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    description = Column(Text)
    debit = Column(Numeric(18, 2), default=0)
    credit = Column(Numeric(18, 2), default=0)

    # Relaciones
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account", back_populates="entries")

    __table_args__ = (Index("idx_line_account", "account_id"),)


class Invoice(Base):
    """Facturas de ingresos y gastos."""

    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    invoice_number = Column(String(50), nullable=False)
    invoice_type = Column(String(20), nullable=False)  # income, expense
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date)
    customer_supplier_name = Column(String(255))
    customer_supplier_tax_id = Column(String(50))
    subtotal = Column(Numeric(18, 2), nullable=False)
    tax_amount = Column(Numeric(18, 2), default=0)
    total = Column(Numeric(18, 2), nullable=False)
    amount_paid = Column(Numeric(18, 2), default=0)
    status = Column(String(20), default="pending")  # pending, paid, overdue, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    company = relationship("Company", back_populates="invoices")

    __table_args__ = (
        Index("idx_invoice_company_date", "company_id", "issue_date"),
        Index("idx_invoice_status", "company_id", "status"),
    )


class Scenario(Base):
    """Escenarios de simulación estratégica."""

    __tablename__ = "scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    scenario_type = Column(
        String(50), nullable=False
    )  # growth, pricing, expansion, financing
    base_period_start = Column(Date, nullable=False)
    base_period_end = Column(Date, nullable=False)
    projection_months = Column(Integer, default=12)

    # Parámetros de simulación (almacenados como JSON en implementación real)
    growth_rate = Column(Numeric(8, 4), default=0)  # Tasa de crecimiento
    price_change = Column(Numeric(8, 4), default=0)  # Cambio en precios
    cost_change = Column(Numeric(8, 4), default=0)  # Cambio en costos
    new_financing = Column(Numeric(18, 2), default=0)  # Nuevo financiamiento
    interest_rate = Column(Numeric(8, 4), default=0)  # Tasa de interés

    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    company = relationship("Company", back_populates="scenarios")
    results = relationship(
        "ScenarioResult", back_populates="scenario", cascade="all, delete-orphan"
    )


class ScenarioResult(Base):
    """Resultados de proyección por escenario."""

    __tablename__ = "scenario_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id"), nullable=False)
    period_month = Column(Integer, nullable=False)  # 1-12
    projected_revenue = Column(Numeric(18, 2), default=0)
    projected_expenses = Column(Numeric(18, 2), default=0)
    projected_ebitda = Column(Numeric(18, 2), default=0)
    projected_tax = Column(Numeric(18, 2), default=0)
    projected_net_income = Column(Numeric(18, 2), default=0)
    projected_cash = Column(Numeric(18, 2), default=0)

    # Relaciones
    scenario = relationship("Scenario", back_populates="results")

    __table_args__ = (
        UniqueConstraint("scenario_id", "period_month", name="uq_scenario_period"),
    )


class TaxConfiguration(Base):
    """Configuración fiscal por país/empresa."""

    __tablename__ = "tax_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True
    )
    country_code = Column(String(2), default="MX")
    vat_rate = Column(Numeric(5, 4), default=0.16)
    income_tax_rate = Column(Numeric(5, 4), default=0.30)
    payroll_tax_rate = Column(Numeric(5, 4), default=0)  # ISN, etc.
    other_taxes = Column(Numeric(5, 4), default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FinancialMetricHistory(Base):
    """Histórico de métricas calculadas para análisis de tendencias."""

    __tablename__ = "financial_metric_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Numeric(18, 4))
    calculated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "company_id", "period_start", "metric_name", name="uq_metric_period"
        ),
        Index("idx_metric_company", "company_id", "metric_name"),
    )


# ============== MODELOS ESPECÍFICOS PARA MÉXICO (SAT/CFDI) ==============


class EmpresaMX(Base):
    """Datos fiscales específicos de empresa mexicana (SAT)."""

    __tablename__ = "empresas_mx"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True
    )

    # Datos del SAT
    rfc = Column(String(13), nullable=False, unique=True)
    razon_social = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255))
    regimen_fiscal = Column(String(3), nullable=False)  # Catálogo SAT
    codigo_postal = Column(String(5), nullable=False)
    calle = Column(String(100))
    numero_exterior = Column(String(20))
    numero_interior = Column(String(20))
    colonia = Column(String(100))
    municipio = Column(String(100))
    estado = Column(String(100))
    pais = Column(String(3), default="MEX")

    # Configuración CFDI
    csd_certificado = Column(Text)  # Certificado de Sello Digital
    csd_llave_privada = Column(Text)  # Llave privada (encriptada)
    csd_password = Column(String(255))  # Contraseña de llave (hash)
    csd_vigencia_desde = Column(Date)
    csd_vigencia_hasta = Column(Date)

    # FIEL (Firma Electrónica Avanzada)
    fiel_certificado = Column(Text)
    fiel_llave_privada = Column(Text)
    fiel_vigencia_desde = Column(Date)
    fiel_vigencia_hasta = Column(Date)

    # PAC (Proveedor Autorizado de Certificación)
    pac_nombre = Column(String(100))
    pac_api_key = Column(String(255))  # Encriptado
    pac_api_secret = Column(String(255))  # Encriptado

    # Flags
    es_zona_fronteriza = Column(Boolean, default=False)
    activa_en_sat = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    company = relationship("Company", backref="datos_mx")
    cfdis_emitidos = relationship(
        "CFDI", foreign_keys="CFDI.empresa_id", back_populates="empresa"
    )

    __table_args__ = (
        Index("idx_empresa_mx_rfc", "rfc"),
        Index("idx_empresa_mx_regimen", "regimen_fiscal"),
    )


class CFDI(Base):
    """Comprobante Fiscal Digital por Internet (Factura electrónica México)."""

    __tablename__ = "cfdis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    empresa_id = Column(
        UUID(as_uuid=True), ForeignKey("empresas_mx.id"), nullable=False
    )

    # Datos del CFDI
    uuid = Column(String(36), unique=True, index=True)  # Folio fiscal
    serie = Column(String(25))
    folio = Column(String(40))
    version = Column(String(5), default="4.0")

    # Tipo y estado
    tipo_comprobante = Column(String(1), nullable=False)  # I, E, T, N, P
    estado = Column(String(20), default="vigente")  # vigente, cancelado, en_proceso
    estado_sat = Column(String(20))  # Vigente, Cancelado, No Encontrado

    # Fechas
    fecha_emision = Column(DateTime, nullable=False)
    fecha_timbrado = Column(DateTime)
    fecha_cancelacion = Column(DateTime)

    # Emisor (ya está en empresa_id, pero guardamos datos al momento de emitir)
    emisor_rfc = Column(String(13), nullable=False)
    emisor_nombre = Column(String(255))
    emisor_regimen_fiscal = Column(String(3))

    # Receptor
    receptor_rfc = Column(String(13), nullable=False)
    receptor_nombre = Column(String(255))
    receptor_regimen_fiscal = Column(String(3))
    receptor_domicilio_fiscal = Column(String(5))  # CP
    receptor_uso_cfdi = Column(String(3), default="G03")

    # Totales
    subtotal = Column(Numeric(18, 2), default=0)
    descuento = Column(Numeric(18, 2), default=0)
    impuestos_trasladados = Column(Numeric(18, 2), default=0)
    impuestos_retenidos = Column(Numeric(18, 2), default=0)
    total = Column(Numeric(18, 2), default=0)

    # Moneda
    moneda = Column(String(3), default="MXN")
    tipo_cambio = Column(Numeric(18, 6), default=1)

    # Forma y método de pago
    forma_pago = Column(String(2))  # 01, 02, 03, etc.
    metodo_pago = Column(String(3), default="PUE")  # PUE, PPD
    condiciones_pago = Column(String(100))

    # Relación con otros CFDI (notas de crédito, etc.)
    cfdi_relacionado_uuid = Column(String(36))
    tipo_relacion = Column(String(2))  # 01, 02, 03, etc.

    # XML y sellos
    xml_timbrado = Column(Text)  # XML timbrado por PAC
    cadena_original = Column(Text)
    sello_digital_emisor = Column(Text)
    sello_digital_sat = Column(Text)

    # QR y representación impresa
    url_verificacion = Column(String(500))

    # Campos de control
    exportacion = Column(
        String(2), default="01"
    )  # 01=No aplica, 02=Definitiva, 03=Temporal
    periodicidad = Column(String(2))  # Para recibos de nómina
    meses = Column(String(2))  # Para recibos de nómina
    ano = Column(String(4))  # Para recibos de nómina

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    empresa = relationship(
        "EmpresaMX", foreign_keys=[empresa_id], back_populates="cfdis_emitidos"
    )
    conceptos = relationship(
        "CFDIConcepto", back_populates="cfdi", cascade="all, delete-orphan"
    )
    impuestos = relationship(
        "CFDIImpuesto", back_populates="cfdi", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_cfdi_uuid", "uuid"),
        Index("idx_cfdi_empresa", "company_id", "fecha_emision"),
        Index("idx_cfdi_receptor", "receptor_rfc", "fecha_emision"),
        Index("idx_cfdi_estado", "company_id", "estado"),
    )


class CFDIConcepto(Base):
    """Conceptos/Partidas de un CFDI."""

    __tablename__ = "cfdi_conceptos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("cfdis.id"), nullable=False)

    # Producto/Servicio
    clave_prod_serv = Column(String(8), nullable=False)  # Catálogo SAT
    clave_unidad = Column(String(3), nullable=False)  # Catálogo SAT
    unidad = Column(String(20))  # Descripción de unidad
    no_identificacion = Column(String(100))  # SKU/Código interno
    descripcion = Column(Text, nullable=False)

    # Cantidad y valores
    cantidad = Column(Numeric(18, 6), default=0)
    valor_unitario = Column(Numeric(18, 6), default=0)
    importe = Column(Numeric(18, 2), default=0)
    descuento = Column(Numeric(18, 2), default=0)

    # Impuestos del concepto
    iva_tasa = Column(Numeric(5, 4), default=0.16)
    iva_importe = Column(Numeric(18, 2), default=0)
    ieps_tasa = Column(Numeric(5, 4), default=0)
    ieps_importe = Column(Numeric(18, 2), default=0)
    isr_retenido_tasa = Column(Numeric(5, 4), default=0)
    isr_retenido_importe = Column(Numeric(18, 2), default=0)
    iva_retenido_tasa = Column(Numeric(5, 4), default=0)
    iva_retenido_importe = Column(Numeric(18, 2), default=0)

    # Información adicional
    objeto_imp = Column(
        String(2), default="02"
    )  # 01=No objeto, 02=Sí objeto, 03=Sí objeto y no obligado
    cuenta_predial = Column(String(150))  # Para bienes inmuebles

    # Complementos específicos por concepto
    complemento_nota = Column(Text)

    # Relaciones
    cfdi = relationship("CFDI", back_populates="conceptos")

    __table_args__ = (Index("idx_concepto_cfdi", "cfdi_id"),)


class CFDIImpuesto(Base):
    """Desglose de impuestos a nivel CFDI."""

    __tablename__ = "cfdi_impuestos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("cfdis.id"), nullable=False)

    # Tipo de impuesto
    tipo = Column(String(10), nullable=False)  # Traslado, Retencion
    impuesto = Column(String(3), nullable=False)  # 001=ISR, 002=IVA, 003=IEPS
    tipo_factor = Column(String(10), nullable=False)  # Tasa, Cuota, Exento
    tasa_cuota = Column(Numeric(5, 4), default=0)
    importe = Column(Numeric(18, 2), default=0)

    # Relaciones
    cfdi = relationship("CFDI", back_populates="impuestos")


class RetencionISR(Base):
    """Registro de retenciones de ISR (para acreditamiento)."""

    __tablename__ = "retenciones_isr"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Datos del retenedor
    retencion_rfc = Column(String(13), nullable=False)  # Quien retuvo
    retencion_nombre = Column(String(255))

    # Datos del contribuyente (la empresa)
    contribuyente_rfc = Column(String(13), nullable=False)

    # Datos de la retención
    ejercicio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)  # 1-12
    monto_operacion = Column(Numeric(18, 2), default=0)
    monto_retencion = Column(Numeric(18, 2), default=0)
    tipo_retencion = Column(
        String(20), nullable=False
    )  # arrendamiento, honorarios, dividendos, etc.

    # CFDI asociado (si aplica)
    cfdi_uuid = Column(String(36))

    # Constancia de retención
    folio_constancia = Column(String(20))
    fecha_constancia = Column(Date)

    # Estado
    acreditada = Column(Boolean, default=False)
    fecha_acreditamiento = Column(Date)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_retencion_company", "company_id", "ejercicio", "mes"),
        Index("idx_retencion_cfdi", "cfdi_uuid"),
    )


class DIOTOperacion(Base):
    """Declaración Informativa de Operaciones con Terceros (SAT)."""

    __tablename__ = "diot_operaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Período
    ejercicio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)

    # Proveedor
    proveedor_rfc = Column(String(13), nullable=False)
    proveedor_nombre = Column(String(255))
    tipo_tercero = Column(String(2), default="04")  # 04=Proveedor nacional
    tipo_operacion = Column(String(2), default="03")  # 03=Prestación de servicios

    # Montos
    valor_neto = Column(Numeric(18, 2), default=0)  # Base gravable
    iva_acreditable = Column(Numeric(18, 2), default=0)
    iva_no_acreditable = Column(Numeric(18, 2), default=0)
    monto_total = Column(Numeric(18, 2), default=0)

    # Flags
    es_exceso = Column(Boolean, default=False)  # Exceso de IVA acreditable
    es_devolucion = Column(Boolean, default=False)

    # CFDI relacionado
    cfdi_uuid = Column(String(36))

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_diot_company_periodo", "company_id", "ejercicio", "mes"),
        Index("idx_diot_proveedor", "proveedor_rfc"),
        UniqueConstraint(
            "company_id",
            "ejercicio",
            "mes",
            "proveedor_rfc",
            "cfdi_uuid",
            name="uq_diot_operacion",
        ),
    )


class ComplementoPago(Base):
    """Complemento de pago (para facturas con método PPD)."""

    __tablename__ = "complementos_pago"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    empresa_id = Column(
        UUID(as_uuid=True), ForeignKey("empresas_mx.id"), nullable=False
    )

    # CFDI de pago
    cfdi_uuid = Column(String(36), unique=True)
    fecha_pago = Column(DateTime, nullable=False)

    # Forma de pago
    forma_pago = Column(String(2), nullable=False)
    moneda = Column(String(3), default="MXN")
    tipo_cambio = Column(Numeric(18, 6), default=1)
    monto = Column(Numeric(18, 2), default=0)

    # Cuentas bancarias (últimos 4 dígitos)
    num_operacion = Column(String(100))
    rfc_emisor_cta_ord = Column(String(13))
    nom_banco_ord_ext = Column(String(300))
    cta_ordenante = Column(String(50))
    rfc_emisor_cta_ben = Column(String(13))
    cta_beneficiario = Column(String(50))

    # Relación con facturas pagadas
    documentos = relationship(
        "PagoDocumentoRelacionado",
        back_populates="complemento_pago",
        cascade="all, delete-orphan",
    )

    created_at = Column(DateTime, default=datetime.utcnow)


class PagoDocumentoRelacionado(Base):
    """Documentos (facturas) pagados con un complemento de pago."""

    __tablename__ = "pago_documentos_relacionados"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complemento_pago_id = Column(
        UUID(as_uuid=True), ForeignKey("complementos_pago.id"), nullable=False
    )

    # Documento pagado
    id_documento = Column(String(36), nullable=False)  # UUID de la factura original
    serie = Column(String(25))
    folio = Column(String(40))
    moneda_dr = Column(String(3), default="MXN")
    num_parcialidad = Column(Integer, default=1)
    imp_saldo_ant = Column(Numeric(18, 2), default=0)  # Saldo anterior
    imp_pagado = Column(Numeric(18, 2), default=0)  # Monto pagado
    imp_saldo_insoluto = Column(Numeric(18, 2), default=0)  # Saldo restante
    metodo_pago_dr = Column(String(3), default="PPD")

    # Relaciones
    complemento_pago = relationship("ComplementoPago", back_populates="documentos")
