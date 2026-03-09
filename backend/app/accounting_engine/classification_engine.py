"""Clasificación contable basada en tipo de CFDI y contacto."""

from __future__ import annotations

from app.models.accounting_models import TipoContacto


class CFDIClassifier:
    TYPE_MAP = {
        "I": "ingreso",
        "E": "egreso",
        "N": "nomina",
        "R": "recepcion_pago",
    }

    def classify_cfdi_type(self, tipo_comprobante: str) -> str:
        return self.TYPE_MAP.get(tipo_comprobante, "desconocido")

    def infer_contact_type(self, company_rfc: str, rfc_emisor: str, rfc_receptor: str) -> TipoContacto:
        if company_rfc == rfc_emisor:
            return TipoContacto.CLIENTE
        if company_rfc == rfc_receptor:
            return TipoContacto.PROVEEDOR
        return TipoContacto.AMBOS
