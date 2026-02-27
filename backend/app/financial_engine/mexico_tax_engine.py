"""
Motor de cálculos fiscales específico para México (SAT).

Incluye cálculos de:
- ISR (Impuesto Sobre la Renta)
- IVA (Impuesto al Valor Agregado) - general y fronterizo
- IEPS (Impuesto Especial sobre Producción y Servicios)
- Retenciones de ISR e IVA
- Acreditamiento de impuestos
- DIOT (Declaración Informativa de Operaciones con Terceros)
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from app.core.mexico_fiscal import (
    obtener_tasa_iva,
    calcular_ieps,
    IEPS_TASAS,
    RegimenFiscal,
)
from app.core.config import get_settings

settings = get_settings()


def round_sat(value: Decimal) -> Decimal:
    """Redondeo según normas del SAT (2 decimales)."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class ImpuestoCalculado:
    """Resultado de cálculo de impuesto."""

    base: Decimal
    tasa: Decimal
    importe: Decimal
    tipo_factor: str = "Tasa"


@dataclass
class DesgloseImpuestos:
    """Desglose completo de impuestos para una operación."""

    iva_trasladado: ImpuestoCalculado
    iva_retenido: ImpuestoCalculado
    ieps: ImpuestoCalculado
    isr_retenido: ImpuestoCalculado
    total_impuestos_trasladados: Decimal
    total_impuestos_retenidos: Decimal


class MotorFiscalMX:
    """
    Motor de cálculos fiscales para México.
    Implementa las reglas del SAT para CFDI 4.0.
    """

    def __init__(self, codigo_postal: str = "01000", regimen_fiscal: str = "601"):
        self.codigo_postal = codigo_postal
        self.regimen_fiscal = regimen_fiscal
        self.tasa_iva = obtener_tasa_iva(codigo_postal)
        self.tasa_isr = Decimal("0.30")  # Personas morales

    # ============== IVA ==============

    def calcular_iva_trasladado(
        self, base: Decimal, tasa: Optional[Decimal] = None, exento: bool = False
    ) -> ImpuestoCalculado:
        """
        Calcula IVA trasladado.

        Args:
            base: Base gravable
            tasa: Tasa específica (si no, usa la del CP)
            exento: Si es operación exenta de IVA

        Returns:
            ImpuestoCalculado con el resultado
        """
        if exento:
            return ImpuestoCalculado(
                base=base, tasa=Decimal("0"), importe=Decimal("0"), tipo_factor="Exento"
            )

        tasa_aplicar = tasa if tasa else Decimal(str(self.tasa_iva))
        importe = round_sat(base * tasa_aplicar)

        return ImpuestoCalculado(
            base=base, tasa=tasa_aplicar, importe=importe, tipo_factor="Tasa"
        )

    def calcular_iva_retenido(
        self, base: Decimal, tipo_servicio: str = "general"
    ) -> ImpuestoCalculado:
        """
        Calcula IVA retenido.

        Retenciones según tipo de servicio:
        - Arrendamiento: 10.6667% del monto total (equivale a 2/3 del IVA)
        - Honorarios: 10.6667%
        - Comisiones: 10.6667%
        - Fletes: 4%

        Args:
            base: Base gravable
            tipo_servicio: Tipo de servicio prestado

        Returns:
            ImpuestoCalculado
        """
        tasas_retencion = {
            "general": Decimal("0"),
            "arrendamiento": Decimal("0.106667"),  # 16% * 2/3
            "honorarios": Decimal("0.106667"),
            "comisiones": Decimal("0.106667"),
            "fletes": Decimal("0.04"),
        }

        tasa = tasas_retencion.get(tipo_servicio, Decimal("0"))
        importe = round_sat(base * tasa)

        return ImpuestoCalculado(
            base=base, tasa=tasa, importe=importe, tipo_factor="Tasa"
        )

    def calcular_acreditamiento_iva(
        self, iva_facturado: Decimal, proporcion_acreditable: Decimal = Decimal("1.0")
    ) -> Decimal:
        """
        Calcula IVA acreditable considerando la proporción.

        La proporción se calcula como:
        Ingresos gravados / Ingresos totales

        Args:
            iva_facturado: IVA de la factura recibida
            proporcion_acreditable: Proporción de acreditamiento (0-1)

        Returns:
            IVA acreditable
        """
        return round_sat(iva_facturado * proporcion_acreditable)

    # ============== ISR ==============

    def calcular_isr_retenido(
        self, base: Decimal, tipo_pago: str = "honorarios"
    ) -> ImpuestoCalculado:
        """
        Calcula ISR retenido según tipo de pago.

        Tasas de retención:
        - Arrendamiento: 10%
        - Honorarios: 10%
        - Comisiones: 10%
        - Dividendos: 10%
        - Intereses: 0.15% a 20% (depende del monto)
        - Enajenación acciones: 10%

        Args:
            base: Monto del pago
            tipo_pago: Tipo de pago realizado

        Returns:
            ImpuestoCalculado
        """
        tasas_isr = {
            "arrendamiento": Decimal("0.10"),
            "honorarios": Decimal("0.10"),
            "comisiones": Decimal("0.10"),
            "dividendos": Decimal("0.10"),
            "intereses_bajo": Decimal("0.0015"),  # Hasta $5,377.50
            "intereses_medio": Decimal("0.2146"),  # Hasta $213,227.76
            "intereses_alto": Decimal("0.20"),  # Más de $213,227.76
            "enajenacion_acciones": Decimal("0.10"),
            "premios": Decimal("0.01"),
        }

        # Para intereses, determinar la tasa según el monto
        if tipo_pago == "intereses":
            if base <= Decimal("5377.50"):
                tasa = tasas_isr["intereses_bajo"]
            elif base <= Decimal("213227.76"):
                tasa = tasas_isr["intereses_medio"]
            else:
                tasa = tasas_isr["intereses_alto"]
        else:
            tasa = tasas_isr.get(tipo_pago, Decimal("0.10"))

        importe = round_sat(base * tasa)

        return ImpuestoCalculado(
            base=base, tasa=tasa, importe=importe, tipo_factor="Tasa"
        )

    def calcular_isr_causado(
        self,
        ingresos_gravados: Decimal,
        deducciones_autorizadas: Decimal,
        perdidas_fiscales: Decimal = Decimal("0"),
    ) -> Dict[str, Decimal]:
        """
        Calcula ISR causado para personas morales.

        Fórmula:
        Base gravable = Ingresos - Deducciones - Pérdidas fiscales
        ISR = Base gravable * 30%

        Args:
            ingresos_gravados: Total de ingresos gravables
            deducciones_autorizadas: Deducciones autorizadas
            perdidas_fiscales: Pérdidas fiscales de ejercicios anteriores

        Returns:
            Dict con desglose del cálculo
        """
        base_gravable = ingresos_gravados - deducciones_autorizadas - perdidas_fiscales

        if base_gravable < 0:
            base_gravable = Decimal("0")

        isr_causado = round_sat(base_gravable * self.tasa_isr)

        return {
            "ingresos_gravados": round_sat(ingresos_gravados),
            "deducciones_autorizadas": round_sat(deducciones_autorizadas),
            "perdidas_fiscales_aplicadas": round_sat(
                min(perdidas_fiscales, ingresos_gravados - deducciones_autorizadas)
            ),
            "base_gravable": round_sat(base_gravable),
            "tasa_isr": self.tasa_isr,
            "isr_causado": isr_causado,
        }

    def calcular_pago_provisional_isr(
        self,
        ingresos_acumulables_periodo: Decimal,
        deducciones_autorizadas_periodo: Decimal,
        isr_retenido_periodo: Decimal,
        pagos_provisionales_anteriores: Decimal = Decimal("0"),
        coeficiente_utilidad: Optional[Decimal] = None,
        perdidas_fiscales_acumuladas: Decimal = Decimal("0"),
    ) -> Dict[str, Decimal]:
        """
        Calcula pago provisional de ISR.

        Para personas morales con fines lucrativos:
        Base = (Ingresos - Deducciones) * Coeficiente de utilidad
        ISR = Base * 30%

        Args:
            ingresos_acumulables_periodo: Ingresos del período
            deducciones_autorizadas_periodo: Deducciones del período
            isr_retenido_periodo: ISR retenido en el período
            pagos_provisionales_anteriores: Pagos provisionales ya hechos
            coeficiente_utilidad: CU del ejercicio anterior
            perdidas_fiscales_acumuladas: PF pendientes de aplicar

        Returns:
            Dict con cálculo del pago provisional
        """
        # Si no se proporciona CU, usar 100% (estimación conservadora)
        if coeficiente_utilidad is None:
            coeficiente_utilidad = Decimal("1.0")

        base_estimada = (
            ingresos_acumulables_periodo - deducciones_autorizadas_periodo
        ) * coeficiente_utilidad

        # Aplicar pérdidas fiscales
        base_gravable = max(Decimal("0"), base_estimada - perdidas_fiscales_acumuladas)

        isr_causado = round_sat(base_gravable * self.tasa_isr)

        # Acreditamientos
        subtotal = isr_causado - isr_retenido_periodo - pagos_provisionales_anteriores

        # No puede ser negativo (no genera saldo a favor en provisionales)
        isr_a_pagar = max(Decimal("0"), subtotal)

        return {
            "ingresos_periodo": round_sat(ingresos_acumulables_periodo),
            "deducciones_periodo": round_sat(deducciones_autorizadas_periodo),
            "utilidad_presunta": round_sat(base_estimada),
            "base_gravable": round_sat(base_gravable),
            "isr_causado": isr_causado,
            "isr_retenido": isr_retenido_periodo,
            "pagos_anteriores": pagos_provisionales_anteriores,
            "isr_a_pagar": isr_a_pagar,
            "coeficiente_utilidad": coeficiente_utilidad,
        }

    # ============== IEPS ==============

    def calcular_ieps(
        self, tipo_producto: str, cantidad: Decimal, valor: Decimal
    ) -> ImpuestoCalculado:
        """
        Calcula IEPS para un producto específico.

        Args:
            tipo_producto: Clave del catálogo IEPS
            cantidad: Cantidad en unidades (litros, piezas)
            valor: Valor del producto

        Returns:
            ImpuestoCalculado
        """
        if tipo_producto not in IEPS_TASAS:
            return ImpuestoCalculado(
                base=valor, tasa=Decimal("0"), importe=Decimal("0")
            )

        config = IEPS_TASAS[tipo_producto]

        # Cuota específica (por unidad)
        if config["cuota_especifica"] > 0:
            importe = round_sat(cantidad * Decimal(str(config["cuota_especifica"])))
            return ImpuestoCalculado(
                base=cantidad,
                tasa=Decimal(str(config["cuota_especifica"])),
                importe=importe,
                tipo_factor="Cuota",
            )

        # Tasa ad valorem
        tasa = Decimal(str(config["tasa"]))
        importe = round_sat(valor * tasa)

        return ImpuestoCalculado(
            base=valor, tasa=tasa, importe=importe, tipo_factor="Tasa"
        )

    # ============== CÁLCULO COMPLETO DE FACTURA ==============

    def calcular_factura_completa(
        self, conceptos: List[Dict], codigo_postal_receptor: Optional[str] = None
    ) -> Dict:
        """
        Calcula todos los impuestos para una factura completa.

        Args:
            conceptos: Lista de conceptos con cantidad, precio, producto
            codigo_postal_receptor: CP del receptor (para determinar IVA)

        Returns:
            Dict con desglose completo de impuestos
        """
        subtotal = Decimal("0")
        descuento = Decimal("0")

        conceptos_calculados = []

        # Impuestos acumulados
        iva_trasladado_total = Decimal("0")
        iva_retenido_total = Decimal("0")
        ieps_total = Decimal("0")
        isr_retenido_total = Decimal("0")

        for concepto in conceptos:
            cantidad = Decimal(str(concepto.get("cantidad", 0)))
            precio = Decimal(str(concepto.get("valor_unitario", 0)))
            desc = Decimal(str(concepto.get("descuento", 0)))
            tipo_ieps = concepto.get("tipo_ieps")

            importe = round_sat(cantidad * precio)

            # IVA del concepto
            iva = self.calcular_iva_trasladado(importe - desc)
            iva_trasladado_total += iva.importe

            # IEPS si aplica
            ieps_importe = Decimal("0")
            if tipo_ieps:
                ieps = self.calcular_ieps(tipo_ieps, cantidad, importe)
                ieps_importe = ieps.importe
                ieps_total += ieps_importe

            conceptos_calculados.append(
                {
                    "descripcion": concepto.get("descripcion", ""),
                    "cantidad": cantidad,
                    "precio": precio,
                    "importe": importe,
                    "descuento": desc,
                    "iva": iva.importe,
                    "ieps": ieps_importe,
                }
            )

            subtotal += importe
            descuento += desc

        # Total de la factura
        total = subtotal - descuento + iva_trasladado_total + ieps_total

        return {
            "conceptos": conceptos_calculados,
            "subtotal": round_sat(subtotal),
            "descuento": round_sat(descuento),
            "impuestos": {
                "iva_trasladado": round_sat(iva_trasladado_total),
                "iva_retenido": round_sat(iva_retenido_total),
                "ieps": round_sat(ieps_total),
                "isr_retenido": round_sat(isr_retenido_total),
            },
            "total": round_sat(total),
            "tasa_iva_aplicada": self.tasa_iva,
        }

    # ============== UTILIDADES DIOT ==============

    def calcular_diot_proveedor(
        self,
        valor_factura: Decimal,
        iva_factura: Decimal,
        tipo_operacion: str = "03",  # Prestación de servicios
        iva_exento: bool = False,
        iva_tasa_cero: bool = False,
    ) -> Dict[str, Decimal]:
        """
        Calcula montos para declaración DIOT.

        Args:
            valor_factura: Valor de la operación
            iva_factura: IVA de la factura
            tipo_operacion: Tipo según catálogo SAT
            iva_exento: Si la operación es exenta
            iva_tasa_cero: Si aplica tasa 0%

        Returns:
            Dict con valores para DIOT
        """
        valor_neto = valor_factura
        iva_acreditable = iva_factura
        iva_no_acreditable = Decimal("0")

        # Si es exento o tasa cero, no hay IVA acreditable
        if iva_exento or iva_tasa_cero:
            iva_acreditable = Decimal("0")
            iva_no_acreditable = Decimal("0")

        return {
            "valor_neto": round_sat(valor_neto),
            "iva_acreditable": round_sat(iva_acreditable),
            "iva_no_acreditable": round_sat(iva_no_acreditable),
            "monto_total": round_sat(valor_neto + iva_acreditable),
        }

    def validar_deduccion_cfdi(self, uso_cfdi: str, tipo_comprobante: str) -> bool:
        """
        Valida si un CFDI es deducible según su uso.

        Args:
            uso_cfdi: Código de uso del CFDI
            tipo_comprobante: I (Ingreso), E (Egreso), etc.

        Returns:
            True si es deducible
        """
        # Los CFDI de ingreso (facturas recibidas) con uso G01, G02, G03 son deducibles
        usos_deducibles = [
            "G01",
            "G02",
            "G03",
            "I01",
            "I02",
            "I03",
            "I04",
            "I05",
            "I06",
            "I07",
        ]

        if tipo_comprobante != "I":  # Debe ser ingreso (recibida)
            return False

        return uso_cfdi in usos_deducibles


# ============== FUNCIONES DE AYUDA ==============


def obtener_coeficiente_utilidad(
    utilidad_fiscal_anterior: Decimal, ingresos_anteriores: Decimal
) -> Decimal:
    """
    Calcula el Coeficiente de Utilidad para pagos provisionales.

    Fórmula: CU = Utilidad del ejercicio anterior / Ingresos del ejercicio anterior

    Args:
        utilidad_fiscal_anterior: Utilidad fiscal del año anterior
        ingresos_anteriores: Ingresos del año anterior

    Returns:
        Coeficiente de utilidad (0-1)
    """
    if ingresos_anteriores == 0:
        return Decimal("1.0")

    cu = utilidad_fiscal_anterior / ingresos_anteriores

    # El CU no puede ser menor a 0.01 ni mayor a 1.0
    cu = max(Decimal("0.01"), min(Decimal("1.0"), cu))

    return round_sat(cu)


def proyectar_isres_anual(
    ingresos_mensuales: List[Decimal],
    deducciones_estimadas: Decimal,
    isr_retenido_estimado: Decimal,
) -> Dict:
    """
    Proyecta ISR anual basado en ingresos mensuales.

    Args:
        ingresos_mensuales: Lista de 12 ingresos proyectados
        deducciones_estimadas: Total de deducciones estimadas
        isr_retenido_estimado: ISR retenido estimado

    Returns:
        Dict con proyección anual
    """
    total_ingresos = sum(ingresos_mensuales)

    motor = MotorFiscalMX()
    calculo = motor.calcular_isr_causado(
        ingresos_gravados=total_ingresos, deducciones_autorizadas=deducciones_estimadas
    )

    isr_a_cargo = max(Decimal("0"), calculo["isr_causado"] - isr_retenido_estimado)

    return {
        "ingresos_proyectados": total_ingresos,
        "deducciones_estimadas": deducciones_estimadas,
        "base_gravable_proyectada": calculo["base_gravable"],
        "isr_causado_proyectado": calculo["isr_causado"],
        "isr_retenido_proyectado": isr_retenido_estimado,
        "isr_a_cargo_proyectado": isr_a_cargo,
        "pagos_provisionales_mensuales": round_sat(isr_a_cargo / 12),
    }
