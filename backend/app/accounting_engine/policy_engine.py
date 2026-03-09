"""Generación automática de pólizas contables."""

from __future__ import annotations

from decimal import Decimal


def build_policy_lines(tipo_comprobante: str, total: Decimal, subtotal: Decimal, iva: Decimal) -> list[dict]:
    """Genera plantilla de asientos para CFDI de ingreso/egreso."""
    if tipo_comprobante == "I":
        return [
            {"rol": "debe", "cuenta": "clientes", "monto": total},
            {"rol": "haber", "cuenta": "ingresos", "monto": subtotal},
            {"rol": "haber", "cuenta": "iva_trasladado", "monto": iva},
        ]
    if tipo_comprobante == "E":
        return [
            {"rol": "debe", "cuenta": "gasto", "monto": subtotal},
            {"rol": "debe", "cuenta": "iva_acreditable", "monto": iva},
            {"rol": "haber", "cuenta": "proveedores", "monto": total},
        ]
    return []
