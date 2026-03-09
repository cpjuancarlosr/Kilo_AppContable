"""Motor fiscal de IVA e ISR para acumulados."""

from __future__ import annotations

from decimal import Decimal


class FiscalEngine:
    def calcular_iva_por_pagar(self, iva_trasladado: Decimal, iva_acreditable: Decimal) -> Decimal:
        return iva_trasladado - iva_acreditable

    def calcular_isr_base(self, ingresos_acumulables: Decimal, deducciones_autorizadas: Decimal) -> Decimal:
        return max(Decimal("0"), ingresos_acumulables - deducciones_autorizadas)

    def calcular_isr_estimado(
        self,
        ingresos_acumulables: Decimal,
        deducciones_autorizadas: Decimal,
        tasa: Decimal = Decimal("0.30"),
    ) -> Decimal:
        base = self.calcular_isr_base(ingresos_acumulables, deducciones_autorizadas)
        return base * tasa
