"""
Indicadores financieros avanzados y críticos para toma de decisiones.

Incluye:
- Altman Z-Score (predicción de bancarrota)
- Análisis Dupont (descomposición del ROE)
- Ratios de distress financiero
- Indicadores de eficiencia operativa
- Cash flow quality metrics
- Análisis de crecimiento sostenible
- Métricas de valor económico agregado
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

from app.financial_engine.calculator import round_money, safe_division


@dataclass
class AltmanZScore:
    """Resultado del Z-Score de Altman para predicción de bancarrota."""

    z_score: float
    probabilidad_bancarrota: float
    interpretacion: str
    componentes: Dict[str, float]

    # Umbrales según Altman
    ZONA_SEGURA = 3.0
    ZONA_GRISES = 1.8

    @property
    def riesgo(self) -> str:
        if self.z_score > self.ZONA_SEGURA:
            return "BAJO"
        elif self.z_score > self.ZONA_GRISES:
            return "MODERADO"
        else:
            return "ALTO - Distress financiero"


@dataclass
class AnalisisDuPont:
    """Descomposición DuPont del ROE."""

    roe: float  # Return on Equity
    roa: float  # Return on Assets
    margen_neto: float
    rotacion_activos: float
    multiplicador_capital: float

    # Descomposición en 3 pasos
    # ROE = Margen Neto × Rotación de Activos × Multiplicador de Capital

    def verificar(self) -> bool:
        """Verifica que ROE = Margen × Rotación × Multiplicador."""
        roe_calculado = (
            self.margen_neto * self.rotacion_activos * self.multiplicador_capital
        )
        return abs(roe_calculado - self.roe) < 0.001


@dataclass
class CashFlowQuality:
    """Métricas de calidad de flujo de efectivo."""

    operating_cash_flow: Decimal
    net_income: Decimal

    # Métricas clave
    cash_earnings_ratio: float  # OCF / Net Income
    accruals_ratio: float  # (Net Income - OCF) / Total Assets

    @property
    def calidad_cash_flow(self) -> str:
        """Evalúa calidad: >1 es alta calidad, <1 es baja."""
        if self.cash_earnings_ratio > 1.2:
            return "EXCELENTE"
        elif self.cash_earnings_ratio > 1.0:
            return "BUENA"
        elif self.cash_earnings_ratio > 0.8:
            return "REGULAR"
        else:
            return "BAJA - Posible manipulación contable"


@dataclass
class CrecimientoSostenible:
    """Análisis de crecimiento sostenible (Sustainable Growth Rate)."""

    sgr: float  # Tasa de crecimiento sostenible
    roe: float
    tasa_retencion: float  # Proporción de utilidades retenidas

    # Fórmula: SGR = ROE × Retención
    # Si la empresa crece más rápido que SGR, necesita financiamiento externo


@dataclass
class EconomicValueAdded:
    """Valor Económico Agregado (EVA)."""

    nopat: Decimal  # Net Operating Profit After Tax
    capital_invertido: Decimal
    wacc: float  # Weighted Average Cost of Capital
    eva: Decimal
    eva_margin: float  # EVA como % de ventas

    # EVA = NOPAT - (Capital Invertido × WACC)


class IndicadoresAvanzados:
    """
    Calculadora de indicadores financieros avanzados para análisis profundo.
    """

    @staticmethod
    def calcular_altman_zscore(
        activo_circulante: Decimal,
        pasivo_circulante: Decimal,
        utilidad_retenida: Decimal,
        ebit: Decimal,
        capital_social: Decimal,
        ventas: Decimal,
        total_activos: Decimal,
        total_pasivos: Decimal,
    ) -> AltmanZScore:
        """
        Calcula el Z-Score de Altman para empresas manufactureras.

        Fórmula: Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5

        X1 = (Activo Circulante - Pasivo Circulante) / Total Activos
        X2 = Utilidades Retenidas / Total Activos
        X3 = EBIT / Total Activos
        X4 = Valor de Mercado del Capital / Total Pasivos
        X5 = Ventas / Total Activos

        Interpretación:
        - Z > 3.0: Zona segura (bajo riesgo)
        - 1.8 < Z < 3.0: Zona gris (riesgo moderado)
        - Z < 1.8: Zona de distress (alto riesgo)

        Args:
            activo_circulante: Activos circulantes
            pasivo_circulante: Pasivos circulantes
            utilidad_retenida: Utilidades retenidas acumuladas
            ebit: Utilidad antes de intereses e impuestos
            capital_social: Capital contable (patrimonio)
            ventas: Ventas totales
            total_activos: Total de activos
            total_pasivos: Total de pasivos

        Returns:
            AltmanZScore con análisis completo
        """
        if total_activos == 0:
            return AltmanZScore(
                z_score=0,
                probabilidad_bancarrota=1.0,
                interpretacion="Error: Sin activos",
                componentes={},
            )

        # Calcular componentes
        x1 = float((activo_circulante - pasivo_circulante) / total_activos)
        x2 = float(utilidad_retenida / total_activos)
        x3 = float(ebit / total_activos)
        x4 = float(capital_social / total_pasivos) if total_pasivos > 0 else 0
        x5 = float(ventas / total_activos)

        # Calcular Z-Score
        z_score = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (1.0 * x5)

        # Calcular probabilidad de bancarrota (simplificado)
        # Más valores negativos = mayor probabilidad
        if z_score > 3:
            prob = 0.05
            interp = "Salud financiera sólida"
        elif z_score > 2:
            prob = 0.15
            interp = "Atención requerida"
        elif z_score > 1.8:
            prob = 0.35
            interp = "Riesgo moderado de distress"
        elif z_score > 1.0:
            prob = 0.60
            interp = "Riesgo alto de bancarrota"
        else:
            prob = 0.85
            interp = "Distress financiero severo - Acción inmediata requerida"

        return AltmanZScore(
            z_score=round(z_score, 2),
            probabilidad_bancarrota=prob,
            interpretacion=interp,
            componentes={
                "x1_capital_trabajo": round(x1, 3),
                "x2_utilidades_retenidas": round(x2, 3),
                "x3_rentabilidad_activos": round(x3, 3),
                "x4_apalancamiento": round(x4, 3),
                "x5_rotacion_activos": round(x5, 3),
            },
        )

    @staticmethod
    def calcular_dupont(
        utilidad_neta: Decimal,
        ventas: Decimal,
        total_activos: Decimal,
        patrimonio: Decimal,
    ) -> AnalisisDuPont:
        """
        Análisis DuPont de 3 pasos para descomponer ROE.

        ROE = Margen Neto × Rotación de Activos × Multiplicador de Capital

        Esto permite identificar qué está impulsando la rentabilidad:
        - Margen neto: Eficiencia operativa
        - Rotación: Eficiencia en uso de activos
        - Multiplicador: Apalancamiento financiero

        Args:
            utilidad_neta: Utilidad del período
            ventas: Ventas totales
            total_activos: Total de activos
            patrimonio: Patrimonio neto

        Returns:
            AnalisisDuPont con descomposición completa
        """
        if ventas == 0 or total_activos == 0 or patrimonio == 0:
            return AnalisisDuPont(0, 0, 0, 0, 0)

        margen_neto = float(utilidad_neta / ventas)
        rotacion_activos = float(ventas / total_activos)
        multiplicador_capital = float(total_activos / patrimonio)

        roa = margen_neto * rotacion_activos
        roe = roa * multiplicador_capital

        return AnalisisDuPont(
            roe=round(roe, 4),
            roa=round(roa, 4),
            margen_neto=round(margen_neto, 4),
            rotacion_activos=round(rotacion_activos, 4),
            multiplicador_capital=round(multiplicador_capital, 4),
        )

    @staticmethod
    def calcular_cash_flow_quality(
        flujo_operaciones: Decimal,
        utilidad_neta: Decimal,
        total_activos: Decimal,
        depreciacion: Decimal,
        provisiones: Decimal = Decimal("0"),
    ) -> CashFlowQuality:
        """
        Evalúa la calidad de las utilidades mediante flujo de efectivo.

        Métricas:
        - Cash Earnings Ratio: OCF / Net Income (ideal > 1)
        - Accruals Ratio: Ajustes contables / Activos (ideal bajo)
        - Depreciation Coverage: FFO / Depreciación

        Args:
            flujo_operaciones: Cash flow de operaciones
            utilidad_neta: Utilidad neta contable
            total_activos: Total de activos
            depreciacion: Depreciación del período
            provisiones: Provisiones no efectivas

        Returns:
            CashFlowQuality con evaluación completa
        """
        if utilidad_neta == 0:
            return CashFlowQuality(
                operating_cash_flow=flujo_operaciones,
                net_income=utilidad_neta,
                cash_earnings_ratio=0,
                accruals_ratio=0,
            )

        # Cash Earnings Ratio
        cash_earnings = float(flujo_operaciones / utilidad_neta)

        # Accruals Ratio
        accruals = utilidad_neta - flujo_operaciones
        accruals_ratio = float(accruals / total_activos) if total_activos > 0 else 0

        return CashFlowQuality(
            operating_cash_flow=flujo_operaciones,
            net_income=utilidad_neta,
            cash_earnings_ratio=round(cash_earnings, 2),
            accruals_ratio=round(accruals_ratio, 4),
        )

    @staticmethod
    def calcular_crecimiento_sostenible(
        roe: float, dividendos: Decimal, utilidad_neta: Decimal
    ) -> CrecimientoSostenible:
        """
        Calcula la tasa de crecimiento sostenible (SGR).

        SGR = ROE × (1 - Dividendos/Utilidad Neta)

        Si la empresa crece más rápido que SGR, necesitará:
        - Aumentar ROE
        - Reducir dividendos
        - Obtener financiamiento externo

        Args:
            roe: Return on Equity (decimal)
            dividendos: Total de dividendos pagados
            utilidad_neta: Utilidad neta del período

        Returns:
            CrecimientoSostenible con análisis
        """
        if utilidad_neta == 0:
            return CrecimientoSostenible(0, 0, 0)

        tasa_retencion = float((utilidad_neta - dividendos) / utilidad_neta)
        sgr = roe * tasa_retencion

        return CrecimientoSostenible(
            sgr=round(sgr, 4),
            roe=round(roe, 4),
            tasa_retencion=round(tasa_retencion, 4),
        )

    @staticmethod
    def calcular_eva(
        utilidad_operativa: Decimal,
        impuestos: Decimal,
        capital_invertido: Decimal,
        wacc: float,
        ventas: Decimal,
    ) -> EconomicValueAdded:
        """
        Calcula el Valor Económico Agregado (EVA).

        EVA = NOPAT - (Capital Invertido × WACC)

        NOPAT = Utilidad Operativa × (1 - Tasa Impuestos)

        Un EVA positivo indica que la empresa está creando valor
        más allá del costo de oportunidad del capital.

        Args:
            utilidad_operativa: EBIT o utilidad operativa
            impuestos: Impuestos pagados
            capital_invertido: Activos - Pasivos no remunerados
            wacc: Costo promedio ponderado de capital (decimal)
            ventas: Ventas totales

        Returns:
            EconomicValueAdded con EVA calculado
        """
        # NOPAT
        tasa_impuestos = safe_division(impuestos, utilidad_operativa, Decimal("0"))
        nopat = utilidad_operativa * (Decimal("1") - tasa_impuestos)

        # Costo del capital
        costo_capital = capital_invertido * Decimal(str(wacc))

        # EVA
        eva = nopat - costo_capital

        # EVA Margin
        eva_margin = float(safe_division(eva, ventas, Decimal("0")))

        return EconomicValueAdded(
            nopat=round_money(nopat),
            capital_invertido=capital_invertido,
            wacc=wacc,
            eva=round_money(eva),
            eva_margin=round(eva_margin, 4),
        )

    @staticmethod
    def calcular_ratios_distress(
        flujo_operaciones: Decimal,
        deuda_total: Decimal,
        ebitda: Decimal,
        intereses: Decimal,
        pasivo_circulante: Decimal,
        activo_circulante: Decimal,
    ) -> Dict[str, Any]:
        """
        Ratios de distress financiero para detectar problemas tempranos.

        Includes:
        - Debt Coverage Ratio: OCF / Deuda Total
        - Interest Coverage: EBITDA / Intereses
        - Financial Leverage: Deuda / Patrimonio
        - Current Ratio: Activo / Pasivo Circulante

        Args:
            flujo_operaciones: Cash flow operativo
            deuda_total: Total de deuda
            ebitda: Ganancias antes de intereses, impuestos, depreciación
            intereses: Gastos financieros
            pasivo_circulante: Pasivos circulantes
            activo_circulante: Activos circulantes

        Returns:
            Dict con ratios de distress y alertas
        """
        ratios = {}
        alertas = []

        # Debt Coverage Ratio
        if deuda_total > 0:
            debt_coverage = float(flujo_operaciones / deuda_total)
            ratios["debt_coverage"] = round(debt_coverage, 2)
            if debt_coverage < 0.15:
                alertas.append(
                    "Debt coverage bajo: Difícil pagar deuda con flujo operativo"
                )
        else:
            ratios["debt_coverage"] = None

        # Interest Coverage
        if intereses > 0:
            interest_coverage = float(ebitda / intereses)
            ratios["interest_coverage"] = round(interest_coverage, 2)
            if interest_coverage < 2:
                alertas.append("Interest coverage crítico: Riesgo de default")
            elif interest_coverage < 3:
                alertas.append("Interest coverage bajo: Monitorear deuda")
        else:
            ratios["interest_coverage"] = 999

        # Current Ratio
        if pasivo_circulante > 0:
            current_ratio = float(activo_circulante / pasivo_circulante)
            ratios["current_ratio"] = round(current_ratio, 2)
            if current_ratio < 1:
                alertas.append("Current ratio < 1: Posible insolvencia técnica")
            elif current_ratio < 1.5:
                alertas.append("Liquidez reducida: Revisar capital de trabajo")
        else:
            ratios["current_ratio"] = None

        # Nivel de distress
        num_alertas = len(alertas)
        if num_alertas >= 3:
            nivel_distress = "CRITICO"
            color = "red"
        elif num_alertas >= 1:
            nivel_distress = "MODERADO"
            color = "yellow"
        else:
            nivel_distress = "NORMAL"
            color = "green"

        return {
            "ratios": ratios,
            "alertas": alertas,
            "nivel_distress": nivel_distress,
            "color": color,
            "score": max(0, 100 - (num_alertas * 25)),
        }

    @staticmethod
    def calcular_eficiencia_operativa(
        ventas: Decimal,
        costo_ventas: Decimal,
        inventario_promedio: Decimal,
        cuentas_por_cobrar: Decimal,
        cuentas_por_pagar: Decimal,
        activos_totales: Decimal,
        dias_periodo: int = 365,
    ) -> Dict[str, Any]:
        """
        Métricas de eficiencia operativa.

        Incluye:
        - Inventory Turnover: Costo Ventas / Inventario
        - DSO: Días de ventas pendientes
        - DPO: Días de cuentas por pagar
        - Asset Turnover: Ventas / Activos
        - Cash Conversion Cycle

        Returns:
            Dict con métricas de eficiencia
        """
        resultados = {}

        # Rotación de inventario
        if inventario_promedio > 0:
            inventory_turnover = float(costo_ventas / inventario_promedio)
            resultados["inventory_turnover"] = round(inventory_turnover, 2)
            resultados["dias_inventario"] = round(dias_periodo / inventory_turnover, 1)
        else:
            resultados["inventory_turnover"] = None
            resultados["dias_inventario"] = None

        # DSO (Days Sales Outstanding)
        if ventas > 0:
            dso = float((cuentas_por_cobrar / ventas) * dias_periodo)
            resultados["dso"] = round(dso, 1)

            # Benchmark: < 45 días es bueno
            if dso > 60:
                resultados["alerta_dso"] = (
                    "Cartera muy vencida - Revisar políticas de crédito"
                )
            elif dso > 45:
                resultados["alerta_dso"] = "DSO por encima del óptimo"
        else:
            resultados["dso"] = None

        # DPO (Days Payable Outstanding)
        if costo_ventas > 0:
            dpo = float((cuentas_por_pagar / costo_ventas) * dias_periodo)
            resultados["dpo"] = round(dpo, 1)
        else:
            resultados["dpo"] = None

        # Asset Turnover
        if activos_totales > 0:
            asset_turnover = float(ventas / activos_totales)
            resultados["asset_turnover"] = round(asset_turnover, 2)
        else:
            resultados["asset_turnover"] = None

        # Cash Conversion Cycle
        if all(
            k in resultados and resultados[k] is not None
            for k in ["dso", "dias_inventario", "dpo"]
        ):
            ccc = resultados["dso"] + resultados["dias_inventario"] - resultados["dpo"]
            resultados["cash_conversion_cycle"] = round(ccc, 1)

            if ccc > 90:
                resultados["alerta_ccc"] = (
                    "CCC muy alto - Ineficiencia en ciclo de efectivo"
                )
            elif ccc < 0:
                resultados["alerta_ccc"] = (
                    "CCC negativo - Excelente gestión de capital de trabajo"
                )

        return resultados

    @staticmethod
    def calcular_kpis_sectoriales(
        ventas: Decimal,
        ebitda: Decimal,
        activos_netos: Decimal,
        empleados: int,
        sector: str = "general",
    ) -> Dict[str, float]:
        """
        KPIs específicos por sector para benchmarking.

        Args:
            ventas: Ventas totales
            ebitda: EBITDA
            activos_netos: Activos fijos netos
            empleados: Número de empleados
            sector: Sector económico

        Returns:
            Dict con KPIs sectoriales
        """
        kpis = {}

        # Productividad
        if empleados > 0:
            kpis["ventas_por_empleado"] = float(ventas / empleados)
            kpis["ebitda_por_empleado"] = float(ebitda / empleados)

        # Intensidad de capital
        if activos_netos > 0:
            kpis["ventas_por_activo"] = float(ventas / activos_netos)

        # Margen operativo por sector
        if ventas > 0:
            margen_ebitda = float(ebitda / ventas)
            kpis["margen_ebitda"] = round(margen_ebitda, 4)

            # Benchmarks por sector
            benchmarks = {
                "tecnologia": 0.25,
                "manufactura": 0.15,
                "retail": 0.10,
                "servicios": 0.20,
                "construccion": 0.12,
                "general": 0.15,
            }

            benchmark = benchmarks.get(sector.lower(), 0.15)
            diferencia = margen_ebitda - benchmark

            kpis["benchmark_sector"] = benchmark
            kpis["diferencia_vs_sector"] = round(diferencia, 4)

            if diferencia > 0.05:
                kpis["evaluacion"] = "SUPERIOR_AL_SECTOR"
            elif diferencia > -0.02:
                kpis["evaluacion"] = "DENTRO_PROMEDIO"
            else:
                kpis["evaluacion"] = "POR_DEBAJO_SECTOR"

        return kpis

    @staticmethod
    def calcular_sensibilidad(
        ventas_actuales: Decimal,
        utilidad_actual: Decimal,
        costos_fijos: Decimal,
        costos_variables: Decimal,
    ) -> Dict[str, float]:
        """
        Análisis de sensibilidad de utilidades.

        Calcula el impacto de cambios en ventas sobre la utilidad.

        Returns:
            Dict con análisis de sensibilidad
        """
        if ventas_actuales == 0:
            return {}

        # Margen de contribución
        margen_contribucion = ventas_actuales - costos_variables
        mc_ratio = float(margen_contribucion / ventas_actuales)

        # Grado de apalancamiento operativo (DOL)
        # % cambio utilidad / % cambio ventas
        if utilidad_actual > 0:
            dol = float(margen_contribucion / utilidad_actual)
        else:
            dol = float("inf")

        # Punto de equilibrio
        pe = float(costos_fijos / mc_ratio) if mc_ratio > 0 else float("inf")

        # Margen de seguridad
        if pe != float("inf"):
            ms = float((ventas_actuales - Decimal(str(pe))) / ventas_actuales * 100)
        else:
            ms = 0

        # Escenarios
        escenarios = {}
        for cambio in [-0.20, -0.10, 0.10, 0.20]:
            nuevas_ventas = ventas_actuales * Decimal(str(1 + cambio))
            nueva_utilidad = (
                margen_contribucion * Decimal(str(1 + cambio)) - costos_fijos
            )
            escenarios[f"ventas_{int(cambio * 100):+d}%"] = {
                "ventas": float(nuevas_ventas),
                "utilidad": float(nueva_utilidad),
                "cambio_utilidad_pct": round(
                    float((nueva_utilidad - utilidad_actual) / utilidad_actual * 100), 1
                )
                if utilidad_actual > 0
                else 0,
            }

        return {
            "margen_contribucion_ratio": round(mc_ratio, 4),
            "grado_apalancamiento_operativo": round(dol, 2),
            "punto_equilibrio": round(pe, 2),
            "margen_seguridad_pct": round(ms, 1),
            "escenarios_sensibilidad": escenarios,
            "interpretacion": (
                f"Un cambio del 10% en ventas produce un cambio del {round(dol * 10, 1)}% en utilidades"
            ),
        }
