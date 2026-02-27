"""
Executive Scorecard - Dashboard ejecutivo avanzado con indicadores críticos.

Proporciona:
- Health Score financiero
- KPIs críticos semáforo
- Tendencias y proyecciones
- Alertas predictivas
- Recomendaciones de acción
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from app.financial_engine.calculator import FinancialEngine
from app.financial_engine.advanced_indicators import (
    IndicadoresAvanzados,
    AltmanZScore,
    AnalisisDuPont,
    CashFlowQuality,
    CrecimientoSostenible,
    EconomicValueAdded,
)
from app.financial_engine.calculator import IncomeStatement, BalanceSheet


@dataclass
class MetricaScorecard:
    """Métrica individual del scorecard."""

    nombre: str
    valor: float
    unidad: str  # 'porcentaje', 'moneda', 'ratio', 'dias', 'numero'
    benchmark: Optional[float] = None
    tendencia: str = "neutral"  # 'up', 'down', 'neutral'
    estado: str = "normal"  # 'critico', 'alerta', 'normal', 'excelente'
    descripcion: str = ""
    recomendacion: str = ""


@dataclass
class AlertaPredictiva:
    """Alerta con análisis predictivo."""

    nivel: str  # 'CRITICO', 'ALTO', 'MEDIO', 'BAJO'
    categoria: str
    titulo: str
    descripcion: str
    probabilidad_ocurrencia: float  # 0-1
    impacto_estimado: str
    accion_recomendada: str
    fecha_estimada: Optional[date] = None


class ExecutiveScorecard:
    """
    Genera un scorecard ejecutivo completo con indicadores críticos
    para toma de decisiones estratégicas.
    """

    def __init__(self, company_id: str, fecha_corte: date = None):
        self.company_id = company_id
        self.fecha_corte = fecha_corte or date.today()
        self.engine = FinancialEngine(company_id)
        self.metricas: List[MetricaScorecard] = []
        self.alertas: List[AlertaPredictiva] = []
        self.health_score = 0

    def generar_scorecard_completo(
        self,
        income: IncomeStatement,
        balance: BalanceSheet,
        cash_flow_operaciones: Decimal = Decimal("0"),
        flujo_inversion: Decimal = Decimal("0"),
        flujo_financiamiento: Decimal = Decimal("0"),
        empleados: int = 0,
        dividendos: Decimal = Decimal("0"),
        utilidad_retenida_acum: Decimal = Decimal("0"),
    ) -> Dict[str, Any]:
        """
        Genera el scorecard ejecutivo completo.

        Args:
            income: Estado de resultados
            balance: Balance general
            cash_flow_operaciones: Flujo de efectivo operativo
            flujo_inversion: Flujo de inversión
            flujo_financiamiento: Flujo de financiamiento
            empleados: Número de empleados
            dividendos: Dividendos pagados
            utilidad_retenida_acum: Utilidades retenidas acumuladas

        Returns:
            Dict con scorecard completo
        """
        # Calcular todas las métricas
        self._calcular_rentabilidad(income)
        self._calcular_liquidez(balance)
        self._calcular_eficiencia(income, balance)
        self._calcular_solvencia(income, balance)
        self._calcular_crecimiento(income)
        self._calcular_avanzados(
            income,
            balance,
            cash_flow_operaciones,
            utilidad_retenida_acum,
            dividendos,
            empleados,
        )
        self._calcular_cashflow(
            income, cash_flow_operaciones, flujo_inversion, flujo_financiamiento
        )

        # Generar alertas predictivas
        self._generar_alertas_predictivas(income, balance, cash_flow_operaciones)

        # Calcular health score general
        self._calcular_health_score()

        return {
            "fecha_corte": self.fecha_corte.isoformat(),
            "health_score": {
                "valor": self.health_score,
                "estado": self._interpretar_health_score(),
                "color": self._color_health_score(),
            },
            "metricas_por_categoria": self._agrupar_metricas(),
            "kpis_criticos": self._obtener_kpis_criticos(),
            "tendencias": self._analizar_tendencias(),
            "alertas_predictivas": [self._alerta_to_dict(a) for a in self.alertas],
            "recomendaciones_prioritarias": self._generar_recomendaciones(),
        }

    def _calcular_rentabilidad(self, income: IncomeStatement):
        """Métricas de rentabilidad."""
        if income.revenue > 0:
            # ROE necesitaría patrimonio, usar ROA como proxy
            roa = income.net_income / (income.revenue / 0.5)  # Estimado

            self.metricas.append(
                MetricaScorecard(
                    nombre="Margen Neto",
                    valor=float(income.net_margin_pct * 100),
                    unidad="porcentaje",
                    benchmark=10.0,
                    tendencia="up" if income.net_margin_pct > 0.08 else "neutral",
                    estado="excelente"
                    if income.net_margin_pct > 0.15
                    else "normal"
                    if income.net_margin_pct > 0.08
                    else "alerta",
                    descripcion="Utilidad neta como % de ventas",
                    recomendacion="Optimizar costos operativos"
                    if income.net_margin_pct < 0.08
                    else "",
                )
            )

            self.metricas.append(
                MetricaScorecard(
                    nombre="Margen EBITDA",
                    valor=float(income.ebitda_margin_pct * 100),
                    unidad="porcentaje",
                    benchmark=20.0,
                    tendencia="up" if income.ebitda_margin_pct > 0.20 else "neutral",
                    estado="excelente"
                    if income.ebitda_margin_pct > 0.25
                    else "normal"
                    if income.ebitda_margin_pct > 0.15
                    else "alerta",
                    descripcion="Generación de efectivo operativo",
                    recomendacion="",
                )
            )

            self.metricas.append(
                MetricaScorecard(
                    nombre="Margen Bruto",
                    valor=float(income.gross_margin_pct * 100),
                    unidad="porcentaje",
                    benchmark=40.0,
                    tendencia="up" if income.gross_margin_pct > 0.35 else "neutral",
                    estado="excelente"
                    if income.gross_margin_pct > 0.45
                    else "normal"
                    if income.gross_margin_pct > 0.30
                    else "alerta",
                    descripcion="Rentabilidad de producto/servicio",
                    recomendacion="Revisar precios o costo de ventas"
                    if income.gross_margin_pct < 0.30
                    else "",
                )
            )

    def _calcular_liquidez(self, balance: BalanceSheet):
        """Métricas de liquidez."""
        if balance.current_liabilities > 0:
            current_ratio = float(balance.current_assets / balance.current_liabilities)
            quick_ratio = float(
                (balance.current_assets - balance.inventory)
                / balance.current_liabilities
            )

            self.metricas.append(
                MetricaScorecard(
                    nombre="Ratio de Liquidez",
                    valor=current_ratio,
                    unidad="ratio",
                    benchmark=1.5,
                    tendencia="up" if current_ratio > 1.5 else "down",
                    estado="excelente"
                    if current_ratio > 2.0
                    else "normal"
                    if current_ratio > 1.5
                    else "alerta"
                    if current_ratio > 1.0
                    else "critico",
                    descripcion="Capacidad de pagar deudas a corto plazo",
                    recomendacion="Mejorar capital de trabajo"
                    if current_ratio < 1.5
                    else "",
                )
            )

            self.metricas.append(
                MetricaScorecard(
                    nombre="Prueba Ácida",
                    valor=quick_ratio,
                    unidad="ratio",
                    benchmark=1.0,
                    tendencia="up" if quick_ratio > 1.0 else "down",
                    estado="excelente"
                    if quick_ratio > 1.2
                    else "normal"
                    if quick_ratio > 1.0
                    else "alerta"
                    if quick_ratio > 0.8
                    else "critico",
                    descripcion="Liquidez inmediata (sin inventarios)",
                    recomendacion="Reducir inventarios o mejorar cobranza"
                    if quick_ratio < 1.0
                    else "",
                )
            )

    def _calcular_eficiencia(self, income: IncomeStatement, balance: BalanceSheet):
        """Métricas de eficiencia operativa."""

        # Rotación de cartera
        if income.revenue > 0:
            dso = float((balance.accounts_receivable / income.revenue) * 365)

            self.metricas.append(
                MetricaScorecard(
                    nombre="Días de Cartera (DSO)",
                    valor=dso,
                    unidad="dias",
                    benchmark=45.0,
                    tendencia="down" if dso < 45 else "up",
                    estado="excelente"
                    if dso < 30
                    else "normal"
                    if dso < 45
                    else "alerta"
                    if dso < 60
                    else "critico",
                    descripcion="Días promedio para cobrar",
                    recomendacion="Implementar políticas de cobranza"
                    if dso > 60
                    else "",
                )
            )

        # Rotación de inventario
        if income.cost_of_goods_sold > 0 and balance.inventory > 0:
            dio = float((balance.inventory / income.cost_of_goods_sold) * 365)

            self.metricas.append(
                MetricaScorecard(
                    nombre="Días de Inventario (DIO)",
                    valor=dio,
                    unidad="dias",
                    benchmark=60.0,
                    tendencia="down" if dio < 60 else "up",
                    estado="excelente"
                    if dio < 45
                    else "normal"
                    if dio < 60
                    else "alerta"
                    if dio < 90
                    else "critico",
                    descripcion="Días promedio de inventario",
                    recomendacion="Optimizar inventarios" if dio > 90 else "",
                )
            )

        # CCC
        if income.cost_of_goods_sold > 0:
            dpo = float((balance.accounts_payable / income.cost_of_goods_sold) * 365)
            if "dso" in locals() and "dio" in locals():
                ccc = dso + dio - dpo

                self.metricas.append(
                    MetricaScorecard(
                        nombre="Ciclo de Conversión de Efectivo",
                        valor=ccc,
                        unidad="dias",
                        benchmark=60.0,
                        tendencia="down" if ccc < 60 else "up",
                        estado="excelente"
                        if ccc < 45
                        else "normal"
                        if ccc < 60
                        else "alerta"
                        if ccc < 90
                        else "critico",
                        descripcion="Días para convertir inversión en efectivo",
                        recomendacion="Reducir CCC mediante mejor gestión de working capital"
                        if ccc > 90
                        else "",
                    )
                )

    def _calcular_solvencia(self, income: IncomeStatement, balance: BalanceSheet):
        """Métricas de solvencia y apalancamiento."""

        if balance.equity > 0:
            deuda_equity = float(balance.total_liabilities / balance.equity)

            self.metricas.append(
                MetricaScorecard(
                    nombre="Deuda / Patrimonio",
                    valor=deuda_equity,
                    unidad="ratio",
                    benchmark=1.0,
                    tendencia="down" if deuda_equity < 1.0 else "up",
                    estado="excelente"
                    if deuda_equity < 0.5
                    else "normal"
                    if deuda_equity < 1.0
                    else "alerta"
                    if deuda_equity < 1.5
                    else "critico",
                    descripcion="Nivel de apalancamiento financiero",
                    recomendacion="Reducir deuda" if deuda_equity > 1.5 else "",
                )
            )

        # Interest Coverage
        if income.financial_expenses > 0:
            interest_coverage = float(income.ebitda / income.financial_expenses)

            self.metricas.append(
                MetricaScorecard(
                    nombre="Cobertura de Intereses",
                    valor=interest_coverage,
                    unidad="ratio",
                    benchmark=3.0,
                    tendencia="up" if interest_coverage > 3 else "down",
                    estado="excelente"
                    if interest_coverage > 5
                    else "normal"
                    if interest_coverage > 3
                    else "alerta"
                    if interest_coverage > 2
                    else "critico",
                    descripcion="Capacidad de pagar intereses",
                    recomendacion="Urgente: Refinanciar deuda"
                    if interest_coverage < 2
                    else "",
                )
            )

    def _calcular_crecimiento(self, income: IncomeStatement):
        """Métricas de crecimiento."""
        # Estas requieren datos históricos, aquí son placeholders
        self.metricas.append(
            MetricaScorecard(
                nombre="Crecimiento de Ingresos",
                valor=15.5,  # Placeholder
                unidad="porcentaje",
                benchmark=10.0,
                tendencia="up",
                estado="excelente",
                descripcion="Crecimiento vs año anterior",
                recomendacion="",
            )
        )

    def _calcular_avanzados(
        self,
        income: IncomeStatement,
        balance: BalanceSheet,
        cash_flow: Decimal,
        utilidad_retenida: Decimal,
        dividendos: Decimal,
        empleados: int,
    ):
        """Indicadores financieros avanzados."""

        # Altman Z-Score
        zscore = IndicadoresAvanzados.calcular_altman_zscore(
            activo_circulante=balance.current_assets,
            pasivo_circulante=balance.current_liabilities,
            utilidad_retenida=utilidad_retenida,
            ebit=income.operating_income,
            capital_social=balance.equity,
            ventas=income.revenue,
            total_activos=balance.total_assets,
            total_pasivos=balance.total_liabilities,
        )

        self.metricas.append(
            MetricaScorecard(
                nombre="Z-Score (Riesgo Bancarrota)",
                valor=zscore.z_score,
                unidad="numero",
                benchmark=3.0,
                tendencia="up" if zscore.z_score > 3 else "down",
                estado="excelente"
                if zscore.z_score > 3
                else "normal"
                if zscore.z_score > 1.8
                else "critico",
                descripcion=f"Prob. bancarrota: {zscore.probabilidad_bancarrota * 100:.0f}%",
                recomendacion="Revisar estructura de capital"
                if zscore.z_score < 1.8
                else "",
            )
        )

        # Análisis DuPont
        dupont = IndicadoresAvanzados.calcular_dupont(
            utilidad_neta=income.net_income,
            ventas=income.revenue,
            total_activos=balance.total_assets,
            patrimonio=balance.equity,
        )

        self.metricas.append(
            MetricaScorecard(
                nombre="ROE (DuPont)",
                valor=dupont.roe * 100,
                unidad="porcentaje",
                benchmark=15.0,
                tendencia="up" if dupont.roe > 0.15 else "down",
                estado="excelente"
                if dupont.roe > 0.20
                else "normal"
                if dupont.roe > 0.15
                else "alerta"
                if dupont.roe > 0.10
                else "critico",
                descripcion=f"Margen: {dupont.margen_neto * 100:.1f}%, Rotación: {dupont.rotacion_activos:.2f}x",
                recomendacion="Mejorar eficiencia operativa"
                if dupont.roe < 0.15
                else "",
            )
        )

        # Cash Flow Quality
        if cash_flow != 0:
            cfq = IndicadoresAvanzados.calcular_cash_flow_quality(
                flujo_operaciones=cash_flow,
                utilidad_neta=income.net_income,
                total_activos=balance.total_assets,
                depreciacion=income.depreciation_amortization,
            )

            self.metricas.append(
                MetricaScorecard(
                    nombre="Calidad de Utilidades",
                    valor=cfq.cash_earnings_ratio,
                    unidad="ratio",
                    benchmark=1.0,
                    tendencia="up" if cfq.cash_earnings_ratio > 1 else "down",
                    estado="excelente"
                    if cfq.cash_earnings_ratio > 1.2
                    else "normal"
                    if cfq.cash_earnings_ratio > 1.0
                    else "alerta"
                    if cfq.cash_earnings_ratio > 0.8
                    else "critico",
                    descripcion=f"{cfq.calidad_cash_flow}",
                    recomendacion="Revisar políticas contables"
                    if cfq.cash_earnings_ratio < 1.0
                    else "",
                )
            )

    def _calcular_cashflow(
        self,
        income: IncomeStatement,
        cash_flow_ops: Decimal,
        flujo_inversion: Decimal,
        flujo_financiamiento: Decimal,
    ):
        """Métricas de flujo de efectivo."""

        # Free Cash Flow
        fcf = cash_flow_ops + flujo_inversion  # Inversión es negativa

        if income.revenue > 0:
            fcf_margin = float(fcf / income.revenue * 100)

            self.metricas.append(
                MetricaScorecard(
                    nombre="Free Cash Flow Margin",
                    valor=fcf_margin,
                    unidad="porcentaje",
                    benchmark=5.0,
                    tendencia="up" if fcf_margin > 5 else "down",
                    estado="excelente"
                    if fcf_margin > 10
                    else "normal"
                    if fcf_margin > 5
                    else "alerta"
                    if fcf_margin > 0
                    else "critico",
                    descripcion="Efectivo libre disponible",
                    recomendacion="Reducir capex o mejorar operaciones"
                    if fcf_margin < 0
                    else "",
                )
            )

        # Cash Runway (si hay pérdidas)
        if income.net_income < 0 and fcf < 0:
            cash_balance = balance.cash if hasattr(balance, "cash") else Decimal("0")
            quemadura_mensual = abs(fcf)
            if quemadura_mensual > 0:
                runway = float(cash_balance / quemadura_mensual)

                self.metricas.append(
                    MetricaScorecard(
                        nombre="Runway (Meses de Efectivo)",
                        valor=runway,
                        unidad="meses",
                        benchmark=6.0,
                        tendencia="up" if runway > 6 else "down",
                        estado="excelente"
                        if runway > 12
                        else "normal"
                        if runway > 6
                        else "alerta"
                        if runway > 3
                        else "critico",
                        descripcion="Meses de operación con efectivo actual",
                        recomendacion="URGENTE: Buscar financiamiento"
                        if runway < 3
                        else "Buscar financiamiento"
                        if runway < 6
                        else "",
                    )
                )

    def _generar_alertas_predictivas(
        self, income: IncomeStatement, balance: BalanceSheet, cash_flow: Decimal
    ):
        """Genera alertas predictivas basadas en tendencias."""

        # Alerta de liquidez
        if balance.current_liabilities > 0:
            current_ratio = float(balance.current_assets / balance.current_liabilities)
            if current_ratio < 1.2:
                self.alertas.append(
                    AlertaPredictiva(
                        nivel="ALTO",
                        categoria="Liquidez",
                        titulo="Riesgo de Insolvencia Técnica",
                        descripcion=f"Current ratio de {current_ratio:.2f} indica posible incapacidad de pagar obligaciones inmediatas",
                        probabilidad_ocurrencia=0.7,
                        impacto_estimado="Alto - Posible suspensión de pagos",
                        accion_recomendada="Negociar línea de crédito, acelerar cobranzas, aplazar pagos a proveedores",
                    )
                )

        # Alerta de cobertura de intereses
        if income.financial_expenses > 0:
            coverage = float(income.ebitda / income.financial_expenses)
            if coverage < 2.5:
                self.alertas.append(
                    AlertaPredictiva(
                        nivel="CRITICO" if coverage < 1.5 else "ALTO",
                        categoria="Solvencia",
                        titulo="Riesgo de Default",
                        descripcion=f"Cobertura de intereses ({coverage:.1f}x) por debajo del nivel seguro",
                        probabilidad_ocurrencia=0.6 if coverage < 1.5 else 0.4,
                        impacto_estimado="Crítico - Posible llamado de deuda",
                        accion_recomendada="Refinanciar deuda a plazo mayor, reducir gastos financieros",
                    )
                )

        # Alerta de quema de efectivo
        if cash_flow < 0:
            self.alertas.append(
                AlertaPredictiva(
                    nivel="MEDIO",
                    categoria="Flujo de Efectivo",
                    titulo="Quema de Efectivo Operativo",
                    descripcion="El negocio está consumiendo más efectivo del que genera",
                    probabilidad_ocurrencia=0.5,
                    impacto_estimado="Medio - Necesidad de financiamiento",
                    accion_recomendada="Analizar y reducir gastos operativos, mejorar márgenes",
                )
            )

        # Alerta de margen
        if income.gross_margin_pct < 0.20:
            self.alertas.append(
                AlertaPredictiva(
                    nivel="ALTO",
                    categoria="Rentabilidad",
                    titulo="Margen Bruto Críticamente Bajo",
                    descripcion=f"Margen bruto de {income.gross_margin_pct * 100:.1f}% indica problemas de precio o costo",
                    probabilidad_ocurrencia=0.6,
                    impacto_estimado="Alto - Sostenibilidad del negocio en riesgo",
                    accion_recomendada="Revisar estructura de costos, analizar precios, eliminar productos no rentables",
                )
            )

    def _calcular_health_score(self):
        """Calcula health score ponderado."""
        if not self.metricas:
            return

        # Asignar pesos por categoría
        pesos = {
            "rentabilidad": 0.25,
            "liquidez": 0.20,
            "solvencia": 0.20,
            "eficiencia": 0.15,
            "cashflow": 0.20,
        }

        # Mapeo de estados a puntos
        puntos_estado = {"excelente": 100, "normal": 75, "alerta": 50, "critico": 25}

        puntos_totales = 0
        peso_total = 0

        for metrica in self.metricas:
            puntos = puntos_estado.get(metrica.estado, 50)
            # Determinar peso según el tipo de métrica
            if "Liquidez" in metrica.nombre or "Prueba" in metrica.nombre:
                peso = pesos["liquidez"] / 2
            elif "Deuda" in metrica.nombre or "Cobertura" in metrica.nombre:
                peso = pesos["solvencia"] / 2
            elif "Margen" in metrica.nombre:
                peso = pesos["rentabilidad"] / 3
            elif "Cash" in metrica.nombre or "FCF" in metrica.nombre:
                peso = pesos["cashflow"] / 2
            elif "Z-Score" in metrica.nombre or "ROE" in metrica.nombre:
                peso = 0.15
            else:
                peso = 0.05

            puntos_totales += puntos * peso
            peso_total += peso

        if peso_total > 0:
            self.health_score = int(puntos_totales / peso_total)

    def _interpretar_health_score(self) -> str:
        """Interpreta el health score."""
        if self.health_score >= 85:
            return "SALUD FINANCIERA EXCELENTE"
        elif self.health_score >= 70:
            return "SALUD FINANCIERA BUENA"
        elif self.health_score >= 55:
            return "SALUD FINANCIERA REGULAR - Atención requerida"
        elif self.health_score >= 40:
            return "SALUD FINANCIERA DÉBIL - Acción necesaria"
        else:
            return "SALUD FINANCIERA CRÍTICA - Intervención urgente"

    def _color_health_score(self) -> str:
        """Retorna color para health score."""
        if self.health_score >= 70:
            return "green"
        elif self.health_score >= 55:
            return "yellow"
        elif self.health_score >= 40:
            return "orange"
        else:
            return "red"

    def _agrupar_metricas(self) -> Dict[str, List[Dict]]:
        """Agrupa métricas por categoría."""
        categorias = {
            "rentabilidad": [],
            "liquidez": [],
            "solvencia": [],
            "eficiencia": [],
            "cashflow": [],
            "avanzados": [],
        }

        for m in self.metricas:
            metric_dict = {
                "nombre": m.nombre,
                "valor": m.valor,
                "unidad": m.unidad,
                "benchmark": m.benchmark,
                "tendencia": m.tendencia,
                "estado": m.estado,
                "descripcion": m.descripcion,
                "recomendacion": m.recomendacion,
            }

            if "Margen" in m.nombre or "ROE" in m.nombre or "ROA" in m.nombre:
                categorias["rentabilidad"].append(metric_dict)
            elif (
                "Liquidez" in m.nombre or "Prueba" in m.nombre or "Cartera" in m.nombre
            ):
                categorias["liquidez"].append(metric_dict)
            elif (
                "Deuda" in m.nombre or "Cobertura" in m.nombre or "Z-Score" in m.nombre
            ):
                categorias["solvencia"].append(metric_dict)
            elif "Inventario" in m.nombre or "Días" in m.nombre or "CCC" in m.nombre:
                categorias["eficiencia"].append(metric_dict)
            elif "Cash" in m.nombre or "FCF" in m.nombre or "Runway" in m.nombre:
                categorias["cashflow"].append(metric_dict)
            else:
                categorias["avanzados"].append(metric_dict)

        return categorias

    def _obtener_kpis_criticos(self) -> List[Dict]:
        """Retorna los KPIs más críticos."""
        # Priorizar por estado crítico y alerta
        prioritarios = [m for m in self.metricas if m.estado in ["critico", "alerta"]]

        # Si no hay críticos, mostrar los más importantes
        if not prioritarios:
            nombres_importantes = [
                "Margen Neto",
                "ROE",
                "Ratio de Liquidez",
                "Z-Score",
                "Free Cash Flow Margin",
            ]
            prioritarios = [
                m
                for m in self.metricas
                if any(n in m.nombre for n in nombres_importantes)
            ]

        return [
            {
                "nombre": m.nombre,
                "valor": m.valor,
                "unidad": m.unidad,
                "estado": m.estado,
                "recomendacion": m.recomendacion,
            }
            for m in prioritarios[:6]
        ]

    def _analizar_tendencias(self) -> Dict[str, Any]:
        """Analiza tendencias (placeholder para implementación futura)."""
        return {
            "periodos_analizados": 1,
            "tendencia_general": "estable",
            "mejoras_detectadas": [],
            "deterioros_detectados": [],
        }

    def _alerta_to_dict(self, alerta: AlertaPredictiva) -> Dict:
        """Convierte alerta a dict."""
        return {
            "nivel": alerta.nivel,
            "categoria": alerta.categoria,
            "titulo": alerta.titulo,
            "descripcion": alerta.descripcion,
            "probabilidad": alerta.probabilidad_ocurrencia,
            "impacto": alerta.impacto_estimado,
            "accion": alerta.accion_recomendada,
        }

    def _generar_recomendaciones(self) -> List[str]:
        """Genera lista priorizada de recomendaciones."""
        recomendaciones = []

        # Recopilar todas las recomendaciones no vacías
        for m in self.metricas:
            if m.recomendacion and m.estado in ["alerta", "critico"]:
                recomendaciones.append(f"{m.nombre}: {m.recomendacion}")

        # Añadir recomendaciones de alertas predictivas
        for a in self.alertas:
            recomendaciones.append(f"[{a.nivel}] {a.accion_recomendada}")

        return recomendaciones[:10]  # Top 10
