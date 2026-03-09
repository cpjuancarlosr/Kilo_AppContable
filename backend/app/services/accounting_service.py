"""Servicio principal para procesar CFDI y persistencia contable."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.accounting_engine.classification_engine import CFDIClassifier
from app.models.accounting_models import (
    CFDI,
    ConceptoCFDI,
    Contacto,
    CuentaPorCobrar,
    CuentaPorPagar,
    ImpuestoCFDI,
    TipoContacto,
)
from app.parsers.cfdi_parser import CFDIParser
from app.tax_engine.fiscal_engine import FiscalEngine


class AccountingService:
    def __init__(self, db: Session):
        self.db = db
        self.parser = CFDIParser()
        self.classifier = CFDIClassifier()
        self.fiscal = FiscalEngine()

    def process_cfdi(self, empresa_id: UUID, empresa_rfc: str, xml_content: str) -> CFDI:
        parsed = self.parser.parse_xml_content(xml_content)
        contacto = self._get_or_create_contacto(empresa_id, empresa_rfc, parsed)

        cfdi = CFDI(
            empresa_id=empresa_id,
            contacto_id=contacto.id if contacto else None,
            uuid_fiscal=parsed.uuid,
            version=parsed.version,
            fecha_emision=datetime.fromisoformat(parsed.fecha_emision),
            tipo_comprobante=parsed.tipo_comprobante,
            rfc_emisor=parsed.rfc_emisor,
            nombre_emisor=parsed.nombre_emisor,
            rfc_receptor=parsed.rfc_receptor,
            nombre_receptor=parsed.nombre_receptor,
            subtotal=parsed.subtotal,
            iva_trasladado=parsed.iva_trasladado,
            iva_retenido=parsed.iva_retenido,
            total=parsed.total,
            moneda=parsed.moneda,
            metodo_pago=parsed.metodo_pago,
            forma_pago=parsed.forma_pago,
            uso_cfdi=parsed.uso_cfdi,
            tiene_complemento_pago=parsed.tiene_complemento_pago,
            tiene_nomina=parsed.tiene_nomina,
            xml_origen=xml_content,
        )
        self.db.add(cfdi)
        self.db.flush()

        for concepto in parsed.conceptos:
            self.db.add(ConceptoCFDI(cfdi_id=cfdi.id, **concepto))

        for impuesto in parsed.impuestos:
            self.db.add(ImpuestoCFDI(cfdi_id=cfdi.id, **impuesto))

        if parsed.tipo_comprobante == "I" and contacto:
            self.db.add(
                CuentaPorCobrar(
                    empresa_id=empresa_id,
                    cfdi_id=cfdi.id,
                    contacto_id=contacto.id,
                    saldo_original=parsed.total,
                    saldo_actual=parsed.total,
                )
            )
        elif parsed.tipo_comprobante == "E" and contacto:
            self.db.add(
                CuentaPorPagar(
                    empresa_id=empresa_id,
                    cfdi_id=cfdi.id,
                    contacto_id=contacto.id,
                    saldo_original=parsed.total,
                    saldo_actual=parsed.total,
                )
            )

        self.db.commit()
        self.db.refresh(cfdi)
        return cfdi

    def fiscal_snapshot(self, iva_trasladado: Decimal, iva_acreditable: Decimal, ingresos: Decimal, deducciones: Decimal) -> dict:
        return {
            "iva_trasladado": iva_trasladado,
            "iva_acreditable": iva_acreditable,
            "iva_por_pagar": self.fiscal.calcular_iva_por_pagar(iva_trasladado, iva_acreditable),
            "ingresos_acumulables": ingresos,
            "deducciones_autorizadas": deducciones,
            "isr_estimado": self.fiscal.calcular_isr_estimado(ingresos, deducciones),
        }

    def _get_or_create_contacto(self, empresa_id: UUID, empresa_rfc: str, parsed) -> Contacto | None:
        tipo_contacto = self.classifier.infer_contact_type(empresa_rfc, parsed.rfc_emisor, parsed.rfc_receptor)
        if tipo_contacto == TipoContacto.CLIENTE:
            rfc, nombre = parsed.rfc_receptor, parsed.nombre_receptor
        elif tipo_contacto == TipoContacto.PROVEEDOR:
            rfc, nombre = parsed.rfc_emisor, parsed.nombre_emisor
        else:
            return None

        contacto = (
            self.db.query(Contacto)
            .filter(Contacto.empresa_id == empresa_id, Contacto.rfc == rfc)
            .first()
        )
        if contacto:
            return contacto

        contacto = Contacto(
            empresa_id=empresa_id,
            rfc=rfc,
            nombre=nombre,
            tipo_contacto=tipo_contacto,
            activo=True,
        )
        self.db.add(contacto)
        self.db.flush()
        return contacto
