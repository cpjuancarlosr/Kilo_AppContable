"""Modelos contables/fiscales centrados en CFDI para México."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class TipoContacto(str, enum.Enum):
    CLIENTE = "cliente"
    PROVEEDOR = "proveedor"
    AMBOS = "ambos"


class TipoCuenta(str, enum.Enum):
    ACTIVO = "activo"
    PASIVO = "pasivo"
    CAPITAL = "capital"
    INGRESO = "ingreso"
    GASTO = "gasto"


class NaturalezaCuenta(str, enum.Enum):
    DEUDORA = "deudora"
    ACREEDORA = "acreedora"


class TipoPoliza(str, enum.Enum):
    INGRESO = "ingreso"
    EGRESO = "egreso"
    DIARIO = "diario"


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfc = Column(String(13), nullable=False, unique=True, index=True)
    nombre = Column(String(255), nullable=False)
    regimen_fiscal = Column(String(10), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Contacto(Base):
    __tablename__ = "contactos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    rfc = Column(String(13), nullable=False)
    nombre = Column(String(255), nullable=False)
    tipo_contacto = Column(Enum(TipoContacto), nullable=False)
    cuenta_contable_predeterminada_id = Column(
        UUID(as_uuid=True), ForeignKey("cuentas_contables.id"), nullable=True
    )
    categoria = Column(String(100), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    empresa = relationship("Empresa")
    cuenta_contable_predeterminada = relationship("CuentaContable")

    __table_args__ = (UniqueConstraint("empresa_id", "rfc", name="uq_contacto_empresa_rfc"),)


class CFDI(Base):
    __tablename__ = "cfdi"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    contacto_id = Column(UUID(as_uuid=True), ForeignKey("contactos.id"), nullable=True)
    uuid_fiscal = Column(String(36), nullable=False, unique=True, index=True)
    version = Column(String(4), nullable=False)
    fecha_emision = Column(DateTime, nullable=False)
    tipo_comprobante = Column(String(1), nullable=False)
    rfc_emisor = Column(String(13), nullable=False)
    nombre_emisor = Column(String(255), nullable=False)
    rfc_receptor = Column(String(13), nullable=False)
    nombre_receptor = Column(String(255), nullable=False)
    subtotal = Column(Numeric(14, 2), nullable=False)
    iva_trasladado = Column(Numeric(14, 2), default=0)
    iva_retenido = Column(Numeric(14, 2), default=0)
    total = Column(Numeric(14, 2), nullable=False)
    moneda = Column(String(5), nullable=False)
    metodo_pago = Column(String(3), nullable=True)
    forma_pago = Column(String(3), nullable=True)
    uso_cfdi = Column(String(4), nullable=True)
    tiene_complemento_pago = Column(Boolean, default=False)
    tiene_nomina = Column(Boolean, default=False)
    xml_origen = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    empresa = relationship("Empresa")
    contacto = relationship("Contacto")
    conceptos = relationship("ConceptoCFDI", back_populates="cfdi", cascade="all, delete-orphan")
    impuestos = relationship("ImpuestoCFDI", back_populates="cfdi", cascade="all, delete-orphan")


class ConceptoCFDI(Base):
    __tablename__ = "conceptos_cfdi"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("cfdi.id"), nullable=False)
    clave_prod_serv = Column(String(20), nullable=True)
    descripcion = Column(Text, nullable=False)
    cantidad = Column(Numeric(14, 4), nullable=False)
    valor_unitario = Column(Numeric(14, 4), nullable=False)
    importe = Column(Numeric(14, 2), nullable=False)

    cfdi = relationship("CFDI", back_populates="conceptos")


class ImpuestoCFDI(Base):
    __tablename__ = "impuestos_cfdi"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("cfdi.id"), nullable=False)
    tipo = Column(String(20), nullable=False)
    impuesto = Column(String(5), nullable=False)
    tipo_factor = Column(String(10), nullable=True)
    tasa_o_cuota = Column(Numeric(10, 6), nullable=True)
    base = Column(Numeric(14, 2), nullable=False)
    importe = Column(Numeric(14, 2), nullable=False)

    cfdi = relationship("CFDI", back_populates="impuestos")


class CuentaContable(Base):
    __tablename__ = "cuentas_contables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    codigo = Column(String(30), nullable=False)
    nombre = Column(String(255), nullable=False)
    tipo = Column(Enum(TipoCuenta), nullable=False)
    naturaleza = Column(Enum(NaturalezaCuenta), nullable=False)
    nivel = Column(Integer, default=1)
    cuenta_padre_id = Column(UUID(as_uuid=True), ForeignKey("cuentas_contables.id"), nullable=True)

    empresa = relationship("Empresa")
    cuenta_padre = relationship("CuentaContable", remote_side=[id])

    __table_args__ = (UniqueConstraint("empresa_id", "codigo", name="uq_cuenta_empresa_codigo"),)


class Poliza(Base):
    __tablename__ = "polizas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("cfdi.id"), nullable=False)
    folio = Column(String(50), nullable=False)
    fecha = Column(Date, nullable=False)
    tipo = Column(Enum(TipoPoliza), nullable=False)
    concepto = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    movimientos = relationship("MovimientoPoliza", back_populates="poliza", cascade="all, delete-orphan")


class MovimientoPoliza(Base):
    __tablename__ = "movimientos_poliza"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    poliza_id = Column(UUID(as_uuid=True), ForeignKey("polizas.id"), nullable=False)
    cuenta_contable_id = Column(UUID(as_uuid=True), ForeignKey("cuentas_contables.id"), nullable=False)
    concepto = Column(Text, nullable=False)
    debe = Column(Numeric(14, 2), default=0)
    haber = Column(Numeric(14, 2), default=0)

    poliza = relationship("Poliza", back_populates="movimientos")
    cuenta_contable = relationship("CuentaContable")


class CuentaPorCobrar(Base):
    __tablename__ = "cuentas_por_cobrar"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("cfdi.id"), nullable=False)
    contacto_id = Column(UUID(as_uuid=True), ForeignKey("contactos.id"), nullable=False)
    saldo_original = Column(Numeric(14, 2), nullable=False)
    saldo_actual = Column(Numeric(14, 2), nullable=False)
    fecha_vencimiento = Column(Date, nullable=True)
    estatus = Column(String(20), default="pendiente")


class CuentaPorPagar(Base):
    __tablename__ = "cuentas_por_pagar"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    cfdi_id = Column(UUID(as_uuid=True), ForeignKey("cfdi.id"), nullable=False)
    contacto_id = Column(UUID(as_uuid=True), ForeignKey("contactos.id"), nullable=False)
    saldo_original = Column(Numeric(14, 2), nullable=False)
    saldo_actual = Column(Numeric(14, 2), nullable=False)
    fecha_vencimiento = Column(Date, nullable=True)
    estatus = Column(String(20), default="pendiente")


class PagoRecibido(Base):
    __tablename__ = "pagos_recibidos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cuenta_por_cobrar_id = Column(UUID(as_uuid=True), ForeignKey("cuentas_por_cobrar.id"), nullable=False)
    fecha_pago = Column(Date, nullable=False)
    monto = Column(Numeric(14, 2), nullable=False)
    referencia = Column(String(255), nullable=True)


class PagoEmitido(Base):
    __tablename__ = "pagos_emitidos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cuenta_por_pagar_id = Column(UUID(as_uuid=True), ForeignKey("cuentas_por_pagar.id"), nullable=False)
    fecha_pago = Column(Date, nullable=False)
    monto = Column(Numeric(14, 2), nullable=False)
    referencia = Column(String(255), nullable=True)
