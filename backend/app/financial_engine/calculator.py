"""
Motor de cálculos financieros - Core del sistema FinAnalytix.

Implementa todos los algoritmos de análisis financiero:
- Métricas de rentabilidad (EBITDA, márgenes)
- Análisis de punto de equilibrio
- Ciclo de conversión de efectivo
- Análisis fiscal
- Simulación de escenarios
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np


# ============== UTILIDADES NUMÉRICAS ==============


def round_money(value: Decimal) -> Decimal:
    """Redondea valores monetarios a 2 decimales."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def safe_division(
    numerator: Decimal, denominator: Decimal, default: Decimal = Decimal("0")
) -> Decimal:
    """División segura que evita división por cero."""
    if denominator == 0:
        return default
    return numerator / denominator


def calculate_percentage_change(current: Decimal, previous: Decimal) -> float:
    """Calcula el cambio porcentual entre dos valores."""
    if previous == 0:
        return 0.0
    return float((current - previous) / previous)


# ============== MODELOS DE DATOS FINANCIEROS ==============


@dataclass
class TrialBalanceRow:
    """Fila de balanza de comprobación."""

    account_id: str
    account_code: str
    account_name: str
    account_type: str
    initial_debit: Decimal
    initial_credit: Decimal
    period_debit: Decimal
    period_credit: Decimal
    final_debit: Decimal
    final_credit: Decimal

    @property
    def final_balance(self) -> Decimal:
        """Saldo final (deudor - acreedor)."""
        return self.final_debit - self.final_credit


@dataclass
class IncomeStatement:
    """Estado de resultados."""

    revenue: Decimal
    cost_of_goods_sold: Decimal
    gross_profit: Decimal
    operating_expenses: Decimal
    operating_income: Decimal
    depreciation_amortization: Decimal
    ebitda: Decimal
    financial_expenses: Decimal
    other_expenses: Decimal
    income_tax: Decimal
    net_income: Decimal

    # Márgenes calculados
    @property
    def gross_margin_pct(self) -> float:
        return float(safe_division(self.gross_profit, self.revenue, Decimal("0")))

    @property
    def operating_margin_pct(self) -> float:
        return float(safe_division(self.operating_income, self.revenue, Decimal("0")))

    @property
    def ebitda_margin_pct(self) -> float:
        return float(safe_division(self.ebitda, self.revenue, Decimal("0")))

    @property
    def net_margin_pct(self) -> float:
        return float(safe_division(self.net_income, self.revenue, Decimal("0")))


@dataclass
class BalanceSheet:
    """Balance general."""

    # Activos
    current_assets: Decimal
    cash: Decimal
    accounts_receivable: Decimal
    inventory: Decimal
    other_current_assets: Decimal
    non_current_assets: Decimal
    total_assets: Decimal

    # Pasivos
    current_liabilities: Decimal
    accounts_payable: Decimal
    short_term_debt: Decimal
    other_current_liabilities: Decimal
    non_current_liabilities: Decimal
    long_term_debt: Decimal
    total_liabilities: Decimal

    # Patrimonio
    equity: Decimal
    total_liabilities_equity: Decimal


@dataclass
class CashFlowMetrics:
    """Métricas de flujo de efectivo."""

    operating_cash_flow: Decimal
    investing_cash_flow: Decimal
    financing_cash_flow: Decimal
    net_cash_flow: Decimal
    beginning_cash: Decimal
    ending_cash: Decimal


# ============== CLASE PRINCIPAL: FINANCIAL ENGINE ==============


class FinancialEngine:
    """
    Motor principal de cálculos financieros.
    Recibe datos contables y genera análisis completos.
    """

    def __init__(self, company_id: str, currency: str = "MXN"):
        self.company_id = company_id
        self.currency = currency
        self.tax_rate = Decimal("0.30")  # Default: México

    # ============== MÉTODOS: ANÁLISIS DE ESTADOS FINANCIEROS ==============

    def build_income_statement(
        self, trial_balance: List[TrialBalanceRow], start_date: date, end_date: date
    ) -> IncomeStatement:
        """
        Construye estado de resultados desde balanza de comprobación.

        Args:
            trial_balance: Lista de cuentas con movimientos
            start_date: Fecha inicio período
            end_date: Fecha fin período

        Returns:
            IncomeStatement con todos los componentes
        """
        # Agrupar por tipo de cuenta
        income_accounts = [r for r in trial_balance if r.account_type == "ingreso"]
        expense_accounts = [r for r in trial_balance if r.account_type == "gasto"]

        # Calcular ingresos (negativo porque los ingresos son acreedores)
        revenue = sum(
            -r.final_balance for r in income_accounts if r.account_code.startswith("4")
        )  # Cuentas de ventas

        # Costo de ventas
        cogs_accounts = [r for r in expense_accounts if r.account_code.startswith("5")]
        cost_of_goods_sold = sum(r.final_balance for r in cogs_accounts)

        # Gastos operativos
        op_accounts = [
            r
            for r in expense_accounts
            if r.account_code.startswith("6") or r.account_code.startswith("7")
        ]
        operating_expenses = sum(r.final_balance for r in op_accounts)

        # Depreciación y amortización
        depr_accounts = [
            r
            for r in expense_accounts
            if "depreciacion" in r.account_name.lower()
            or "amortizacion" in r.account_name.lower()
        ]
        depreciation = sum(r.final_balance for r in depr_accounts)

        # Gastos financieros
        fin_accounts = [
            r for r in expense_accounts if "intereses" in r.account_name.lower()
        ]
        financial_expenses = sum(r.final_balance for r in fin_accounts)

        # Impuestos
        tax_accounts = [
            r for r in expense_accounts if r.account_code.startswith("82")
        ]  # ISR
        income_tax = sum(r.final_balance for r in tax_accounts)

        # Calcular derivados
        gross_profit = revenue - cost_of_goods_sold
        ebitda = gross_profit - operating_expenses + depreciation
        operating_income = ebitda - depreciation
        other_expenses = Decimal("0")  # Simplificado
        net_income = operating_income - financial_expenses - other_expenses - income_tax

        return IncomeStatement(
            revenue=round_money(revenue),
            cost_of_goods_sold=round_money(cost_of_goods_sold),
            gross_profit=round_money(gross_profit),
            operating_expenses=round_money(operating_expenses),
            operating_income=round_money(operating_income),
            depreciation_amortization=round_money(depreciation),
            ebitda=round_money(ebitda),
            financial_expenses=round_money(financial_expenses),
            other_expenses=round_money(other_expenses),
            income_tax=round_money(income_tax),
            net_income=round_money(net_income),
        )

    def build_balance_sheet(self, trial_balance: List[TrialBalanceRow]) -> BalanceSheet:
        """
        Construye balance general desde balanza.

        Args:
            trial_balance: Lista de cuentas con saldos

        Returns:
            BalanceSheet con todos los componentes
        """
        # Activos circulantes
        asset_accounts = [r for r in trial_balance if r.account_type == "activo"]

        cash = sum(
            r.final_balance for r in asset_accounts if r.account_code.startswith("11")
        )  # Bancos y caja
        ar = sum(
            r.final_balance for r in asset_accounts if r.account_code.startswith("12")
        )  # Clientes
        inventory = sum(
            r.final_balance for r in asset_accounts if r.account_code.startswith("13")
        )  # Inventarios
        other_ca = sum(
            r.final_balance
            for r in asset_accounts
            if r.account_code.startswith("14") or r.account_code.startswith("15")
        )

        current_assets = cash + ar + inventory + other_ca

        # Activos no circulantes
        nca = sum(
            r.final_balance for r in asset_accounts if r.account_code.startswith("2")
        )
        total_assets = current_assets + nca

        # Pasivos
        liability_accounts = [r for r in trial_balance if r.account_type == "pasivo"]

        ap = sum(
            r.final_balance
            for r in liability_accounts
            if r.account_code.startswith("21")
        )  # Proveedores
        std = sum(
            r.final_balance
            for r in liability_accounts
            if r.account_code.startswith("22")
        )  # Deuda corto plazo
        other_cl = sum(
            r.final_balance
            for r in liability_accounts
            if r.account_code.startswith("23")
        )

        current_liabilities = ap + std + other_cl

        ncl = sum(
            r.final_balance
            for r in liability_accounts
            if r.account_code.startswith("3")
        )
        ltd = sum(
            r.final_balance
            for r in liability_accounts
            if "largo" in r.account_name.lower()
        )

        total_liabilities = current_liabilities + ncl

        # Patrimonio
        equity_accounts = [r for r in trial_balance if r.account_type == "patrimonio"]
        equity = sum(r.final_balance for r in equity_accounts)

        return BalanceSheet(
            current_assets=round_money(current_assets),
            cash=round_money(cash),
            accounts_receivable=round_money(ar),
            inventory=round_money(inventory),
            other_current_assets=round_money(other_ca),
            non_current_assets=round_money(nca),
            total_assets=round_money(total_assets),
            current_liabilities=round_money(current_liabilities),
            accounts_payable=round_money(ap),
            short_term_debt=round_money(std),
            other_current_liabilities=round_money(other_cl),
            non_current_liabilities=round_money(ncl),
            long_term_debt=round_money(ltd),
            total_liabilities=round_money(total_liabilities),
            equity=round_money(equity),
            total_liabilities_equity=round_money(total_liabilities + equity),
        )

    # ============== MÉTODOS: RATIOS Y MÉTRICAS ==============

    def calculate_ratios(
        self, income: IncomeStatement, balance: BalanceSheet
    ) -> Dict[str, Optional[float]]:
        """
        Calcula ratios financieros clave.

        Returns:
            Dict con ratios calculados
        """
        ratios = {}

        # Liquidez
        if balance.current_liabilities > 0:
            ratios["current_ratio"] = float(
                safe_division(balance.current_assets, balance.current_liabilities)
            )
            quick_assets = balance.current_assets - balance.inventory
            ratios["quick_ratio"] = float(
                safe_division(quick_assets, balance.current_liabilities)
            )
        else:
            ratios["current_ratio"] = None
            ratios["quick_ratio"] = None

        # Solvencia
        if balance.equity > 0:
            ratios["debt_to_equity"] = float(
                safe_division(balance.total_liabilities, balance.equity)
            )
        else:
            ratios["debt_to_equity"] = None

        # Rentabilidad
        if balance.total_assets > 0:
            ratios["roa"] = float(
                safe_division(income.net_income, balance.total_assets)
            )
        else:
            ratios["roa"] = None

        if balance.equity > 0:
            ratios["roe"] = float(safe_division(income.net_income, balance.equity))
        else:
            ratios["roe"] = None

        # Márgenes
        ratios["gross_margin"] = income.gross_margin_pct
        ratios["operating_margin"] = income.operating_margin_pct
        ratios["net_margin"] = income.net_margin_pct

        # Rotación
        if balance.inventory > 0:
            cogs = income.cost_of_goods_sold
            ratios["inventory_turnover"] = (
                float(safe_division(cogs, balance.inventory)) * 12
            )  # Anualizado
        else:
            ratios["inventory_turnover"] = None

        if balance.total_assets > 0:
            ratios["asset_turnover"] = float(
                safe_division(income.revenue, balance.total_assets)
            )
        else:
            ratios["asset_turnover"] = None

        return ratios

    # ============== MÉTODOS: PUNTO DE EQUILIBRIO ==============

    def calculate_break_even(
        self,
        revenue: Decimal,
        variable_costs: Decimal,
        fixed_costs: Decimal,
        unit_price: Optional[Decimal] = None,
    ) -> Dict[str, Any]:
        """
        Calcula punto de equilibrio operativo.

        Args:
            revenue: Ingresos totales
            variable_costs: Costos variables
            fixed_costs: Costos fijos
            unit_price: Precio unitario (opcional, para calcular unidades)

        Returns:
            Dict con análisis de punto de equilibrio
        """
        contribution_margin = revenue - variable_costs
        cm_ratio = safe_division(contribution_margin, revenue, Decimal("0"))

        if cm_ratio > 0:
            break_even_revenue = safe_division(fixed_costs, cm_ratio, Decimal("0"))
            safety_margin = safe_division(
                revenue - break_even_revenue, revenue, Decimal("0")
            )
        else:
            break_even_revenue = Decimal("0")
            safety_margin = Decimal("0")

        result = {
            "fixed_costs": round_money(fixed_costs),
            "variable_costs": round_money(variable_costs),
            "contribution_margin": round_money(contribution_margin),
            "contribution_margin_pct": float(cm_ratio),
            "break_even_revenue": round_money(break_even_revenue),
            "safety_margin_pct": float(safety_margin),
            "current_revenue": round_money(revenue),
        }

        # Calcular en unidades si se proporciona precio
        if unit_price and unit_price > 0:
            cm_per_unit = unit_price * cm_ratio
            if cm_per_unit > 0:
                be_units = safe_division(fixed_costs, cm_per_unit, Decimal("0"))
                result["break_even_units"] = float(be_units)
                result["current_units"] = float(safe_division(revenue, unit_price))

        return result

    # ============== MÉTODOS: CICLO DE EFECTIVO ==============

    def calculate_cash_conversion_cycle(
        self,
        revenue: Decimal,
        cogs: Decimal,
        accounts_receivable: Decimal,
        accounts_payable: Decimal,
        inventory: Decimal,
        days_in_period: int = 365,
    ) -> Dict[str, float]:
        """
        Calcula ciclo de conversión de efectivo (Cash Conversion Cycle).

        CCC = DSO + DIO - DPO

        Args:
            revenue: Ingresos del período
            cogs: Costo de ventas
            accounts_receivable: Cuentas por cobrar
            accounts_payable: Cuentas por pagar
            inventory: Inventario
            days_in_period: Días en el período analizado

        Returns:
            Dict con DSO, DIO, DPO y CCC
        """
        # DSO - Days Sales Outstanding
        if revenue > 0:
            dso = float((accounts_receivable / revenue) * days_in_period)
        else:
            dso = 0.0

        # DIO - Days Inventory Outstanding
        if cogs > 0:
            dio = float((inventory / cogs) * days_in_period)
        else:
            dio = 0.0

        # DPO - Days Payable Outstanding
        if cogs > 0:
            dpo = float((accounts_payable / cogs) * days_in_period)
        else:
            dpo = 0.0

        ccc = dso + dio - dpo

        return {
            "dso": round(dso, 1),
            "dio": round(dio, 1),
            "dpo": round(dpo, 1),
            "ccc": round(ccc, 1),
        }

    # ============== MÉTODOS: ANÁLISIS FISCAL ==============

    def calculate_tax_burden(
        self,
        revenue: Decimal,
        taxable_income: Decimal,
        vat_collected: Decimal,
        vat_paid: Decimal,
        other_taxes: Decimal = Decimal("0"),
    ) -> Dict[str, Any]:
        """
        Calcula carga fiscal total y efectiva.

        Returns:
            Dict con desglose fiscal
        """
        income_tax = taxable_income * self.tax_rate
        vat_net = vat_collected - vat_paid
        total_tax = income_tax + other_taxes + max(Decimal("0"), vat_net)

        effective_rate = safe_division(total_tax, revenue, Decimal("0"))

        return {
            "revenue": round_money(revenue),
            "taxable_income": round_money(taxable_income),
            "income_tax": round_money(income_tax),
            "vat_collected": round_money(vat_collected),
            "vat_paid": round_money(vat_paid),
            "vat_net": round_money(vat_net),
            "other_taxes": round_money(other_taxes),
            "total_tax": round_money(total_tax),
            "effective_tax_rate": float(effective_rate),
        }

    def project_taxes(
        self,
        base_revenue: Decimal,
        base_taxable_income: Decimal,
        growth_rates: List[float],
        vat_rate: float = 0.16,
        income_tax_rate: float = 0.30,
    ) -> List[Dict[str, Any]]:
        """
        Proyecta impuestos a 12 meses con diferentes tasas de crecimiento.

        Args:
            base_revenue: Ingresos base
            base_taxable_income: Utilidad gravable base
            growth_rates: Lista de tasas de crecimiento mensual
            vat_rate: Tasa de IVA
            income_tax_rate: Tasa de ISR

        Returns:
            Lista de proyecciones mensuales
        """
        projections = []
        cumulative_tax = Decimal("0")

        for month, growth in enumerate(growth_rates, 1):
            # Calcular ingresos proyectados
            growth_factor = Decimal(str(1 + growth))
            projected_revenue = base_revenue * growth_factor
            projected_taxable = base_taxable_income * growth_factor

            # Calcular impuestos
            projected_income_tax = projected_taxable * Decimal(str(income_tax_rate))
            projected_vat = projected_revenue * Decimal(str(vat_rate))
            projected_total = projected_income_tax + projected_vat

            cumulative_tax += projected_total

            projections.append(
                {
                    "month": month,
                    "growth_rate": growth,
                    "projected_revenue": round_money(projected_revenue),
                    "projected_taxable_income": round_money(projected_taxable),
                    "projected_income_tax": round_money(projected_income_tax),
                    "projected_vat": round_money(projected_vat),
                    "projected_total_tax": round_money(projected_total),
                    "cumulative_tax": round_money(cumulative_tax),
                }
            )

            # Actualizar base para siguiente mes
            base_revenue = projected_revenue
            base_taxable_income = projected_taxable

        return projections

    # ============== MÉTODOS: SIMULACIÓN DE ESCENARIOS ==============

    def simulate_growth_scenario(
        self,
        base_revenue: Decimal,
        base_expenses: Decimal,
        growth_rate_annual: float,
        months: int = 12,
    ) -> List[Dict[str, Any]]:
        """
        Simula escenario de crecimiento.

        Args:
            base_revenue: Ingresos base mensuales
            base_expenses: Gastos base mensuales
            growth_rate_annual: Tasa de crecimiento anual (ej: 0.20 = 20%)
            months: Meses a proyectar

        Returns:
            Lista de resultados mensuales
        """
        # Convertir crecimiento anual a mensual compuesto
        monthly_rate = (1 + growth_rate_annual) ** (1 / 12) - 1

        results = []
        cumulative_revenue = Decimal("0")
        cumulative_expenses = Decimal("0")

        current_revenue = base_revenue
        current_expenses = base_expenses

        for month in range(1, months + 1):
            # Aplicar crecimiento
            if month > 1:
                current_revenue *= Decimal(str(1 + monthly_rate))
                # Asumir que gastos variables crecen proporcionalmente
                # pero gastos fijos se mantienen
                variable_ratio = Decimal("0.6")  # 60% de gastos son variables
                fixed_expenses = current_expenses * (Decimal("1") - variable_ratio)
                variable_expenses = (current_expenses * variable_ratio) * Decimal(
                    str(1 + monthly_rate)
                )
                current_expenses = fixed_expenses + variable_expenses

            ebitda = current_revenue - current_expenses
            # Asumir depreciación del 5% de EBITDA para simplificar
            depreciation = ebitda * Decimal("0.05")
            operating_income = ebitda - depreciation
            tax = max(Decimal("0"), operating_income * self.tax_rate)
            net_income = operating_income - tax

            cumulative_revenue += current_revenue
            cumulative_expenses += current_expenses

            results.append(
                {
                    "month": month,
                    "revenue": round_money(current_revenue),
                    "expenses": round_money(current_expenses),
                    "ebitda": round_money(ebitda),
                    "depreciation": round_money(depreciation),
                    "operating_income": round_money(operating_income),
                    "tax": round_money(tax),
                    "net_income": round_money(net_income),
                    "cumulative_revenue": round_money(cumulative_revenue),
                    "cumulative_net_income": round_money(
                        sum(r["net_income"] for r in results) + net_income
                    ),
                }
            )

        return results

    def simulate_price_change(
        self,
        base_revenue: Decimal,
        base_expenses: Decimal,
        price_change_pct: float,
        volume_change_pct: float = 0,
        months: int = 12,
    ) -> Dict[str, Any]:
        """
        Simula impacto de cambio en precios.

        Args:
            base_revenue: Ingresos base
            base_expenses: Gastos base
            price_change_pct: Cambio porcentual en precios
            volume_change_pct: Cambio porcentual esperado en volumen
            months: Meses a proyectar

        Returns:
            Comparativa antes/después
        """
        # Escenario actual (base)
        base_ebitda = base_revenue - base_expenses

        # Escenario con nuevo precio
        price_factor = 1 + price_change_pct
        volume_factor = 1 + volume_change_pct
        new_revenue = base_revenue * Decimal(str(price_factor * volume_factor))

        # Asumir que costos variables cambian con volumen
        variable_cost_ratio = Decimal("0.6")
        fixed_costs = base_expenses * (Decimal("1") - variable_cost_ratio)
        variable_costs = (base_expenses * variable_cost_ratio) * Decimal(
            str(volume_factor)
        )
        new_expenses = fixed_costs + variable_costs

        new_ebitda = new_revenue - new_expenses

        # Proyección a 12 meses
        base_annual = base_ebitda * months
        new_annual = new_ebitda * months

        return {
            "price_change_pct": price_change_pct,
            "volume_change_pct": volume_change_pct,
            "base_scenario": {
                "monthly_revenue": round_money(base_revenue),
                "monthly_expenses": round_money(base_expenses),
                "monthly_ebitda": round_money(base_ebitda),
                "annual_ebitda": round_money(base_annual),
            },
            "new_scenario": {
                "monthly_revenue": round_money(new_revenue),
                "monthly_expenses": round_money(new_expenses),
                "monthly_ebitda": round_money(new_ebitda),
                "annual_ebitda": round_money(new_annual),
            },
            "impact": {
                "monthly_ebitda_change": round_money(new_ebitda - base_ebitda),
                "annual_ebitda_change": round_money(new_annual - base_annual),
                "ebitda_change_pct": float(
                    safe_division(new_ebitda - base_ebitda, base_ebitda, Decimal("0"))
                ),
            },
        }

    def simulate_financing_impact(
        self,
        current_revenue: Decimal,
        current_expenses: Decimal,
        current_debt: Decimal,
        new_financing: Decimal,
        interest_rate: float,
        term_months: int = 36,
    ) -> Dict[str, Any]:
        """
        Simula impacto de nuevo financiamiento.

        Args:
            current_revenue: Ingresos actuales mensuales
            current_expenses: Gastos actuales mensuales
            current_debt: Deuda actual
            new_financing: Monto de nuevo financiamiento
            interest_rate: Tasa de interés anual
            term_months: Plazo en meses

        Returns:
            Análisis de impacto del financiamiento
        """
        monthly_rate = interest_rate / 12

        # Calcular pago mensual (amortización tipo francés)
        if monthly_rate > 0:
            payment = (new_financing * Decimal(str(monthly_rate))) / (
                Decimal("1")
                - (
                    Decimal("1")
                    / ((Decimal("1") + Decimal(str(monthly_rate))) ** term_months)
                )
            )
        else:
            payment = new_financing / term_months

        # Escenario actual
        current_ebitda = current_revenue - current_expenses
        # Asumir costo actual de deuda del 8% anual
        current_interest = current_debt * Decimal("0.08") / 12
        current_net = current_ebitda - current_interest

        # Escenario con nueva deuda
        new_interest = (current_debt + new_financing) * Decimal(str(interest_rate)) / 12
        new_total_payment = payment  # Pago total incluye capital + interés
        new_net = current_ebitda - new_total_payment

        return {
            "financing_details": {
                "amount": round_money(new_financing),
                "annual_rate": interest_rate,
                "term_months": term_months,
                "monthly_payment": round_money(payment),
                "total_interest": round_money(payment * term_months - new_financing),
            },
            "current_scenario": {
                "ebitda": round_money(current_ebitda),
                "interest_expense": round_money(current_interest),
                "net_flow": round_money(current_net),
            },
            "new_scenario": {
                "ebitda": round_money(current_ebitda),
                "total_debt_service": round_money(new_total_payment),
                "interest_portion": round_money(new_interest),
                "principal_portion": round_money(payment - new_interest),
                "net_flow": round_money(new_net),
            },
            "impact": {
                "monthly_flow_change": round_money(new_net - current_net),
                "dscr_current": float(
                    safe_division(
                        current_ebitda,
                        current_interest + (current_debt / 36),
                        Decimal("999"),
                    )
                ),
                "dscr_new": float(
                    safe_division(current_ebitda, new_total_payment, Decimal("999"))
                ),
            },
        }

    # ============== MÉTODOS: ANÁLISIS VERTICAL Y HORIZONTAL ==============

    def vertical_analysis(self, income: IncomeStatement) -> List[Dict[str, Any]]:
        """
        Análisis vertical: cada partida como % de ventas.

        Returns:
            Lista de partidas con porcentajes
        """
        revenue = income.revenue

        items = [
            ("Ventas", income.revenue),
            ("Costo de Ventas", income.cost_of_goods_sold),
            ("Utilidad Bruta", income.gross_profit),
            ("Gastos Operativos", income.operating_expenses),
            ("Utilidad Operativa", income.operating_income),
            ("Depreciación", income.depreciation_amortization),
            ("EBITDA", income.ebitda),
            ("Gastos Financieros", income.financial_expenses),
            ("Impuestos", income.income_tax),
            ("Utilidad Neta", income.net_income),
        ]

        result = []
        for name, amount in items:
            pct = float(safe_division(amount, revenue, Decimal("0")))
            result.append(
                {
                    "concept": name,
                    "amount": round_money(amount),
                    "percentage": round(pct * 100, 2),
                }
            )

        return result

    def horizontal_analysis(
        self, current: IncomeStatement, previous: IncomeStatement
    ) -> List[Dict[str, Any]]:
        """
        Análisis horizontal: comparación período vs período anterior.

        Returns:
            Lista de variaciones por concepto
        """
        comparisons = [
            ("Ventas", current.revenue, previous.revenue),
            (
                "Costo de Ventas",
                current.cost_of_goods_sold,
                previous.cost_of_goods_sold,
            ),
            ("Utilidad Bruta", current.gross_profit, previous.gross_profit),
            (
                "Gastos Operativos",
                current.operating_expenses,
                previous.operating_expenses,
            ),
            ("EBITDA", current.ebitda, previous.ebitda),
            ("Utilidad Operativa", current.operating_income, previous.operating_income),
            (
                "Gastos Financieros",
                current.financial_expenses,
                previous.financial_expenses,
            ),
            ("Impuestos", current.income_tax, previous.income_tax),
            ("Utilidad Neta", current.net_income, previous.net_income),
        ]

        result = []
        for name, curr, prev in comparisons:
            change = curr - prev
            change_pct = calculate_percentage_change(curr, prev)
            result.append(
                {
                    "concept": name,
                    "current": round_money(curr),
                    "previous": round_money(prev),
                    "absolute_change": round_money(change),
                    "percentage_change": round(change_pct * 100, 2),
                }
            )

        return result
