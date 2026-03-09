"""Consultas de reportes financieros básicos."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.accounting_models import CFDI


def estado_resultados(db: Session, empresa_id):
    ingresos = (
        db.query(func.coalesce(func.sum(CFDI.subtotal), 0))
        .filter(CFDI.empresa_id == empresa_id, CFDI.tipo_comprobante == "I")
        .scalar()
    )
    gastos = (
        db.query(func.coalesce(func.sum(CFDI.subtotal), 0))
        .filter(CFDI.empresa_id == empresa_id, CFDI.tipo_comprobante == "E")
        .scalar()
    )
    utilidad = ingresos - gastos
    return {"ingresos": ingresos, "gastos": gastos, "utilidad_neta": utilidad}
