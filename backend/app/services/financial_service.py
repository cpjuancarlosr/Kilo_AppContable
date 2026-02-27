"""
Servicios de negocio que orquestan el motor financiero con la base de datos.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, between

from app.models import (
    Company,
    Account,
    JournalEntry,
    JournalEntryLine,
    Invoice,
    TrialBalanceRow,
    IncomeStatement,
    BalanceSheet,
)
from app.financial_engine.calculator import FinancialEngine


class FinancialService:
    """Servicio principal de operaciones financieras."""

    def __init__(self, db: Session):
        self.db = db

    def get_trial_balance(
        self, company_id: UUID, start_date: date, end_date: date
    ) -> List[TrialBalanceRow]:
        """
        Genera balanza de comprobación desde movimientos.

        Returns:
            Lista de TrialBalanceRow con todos los saldos
        """
        # Query para obtener movimientos agrupados por cuenta
        query = (
            self.db.query(
                Account.id,
                Account.code,
                Account.name,
                Account.account_type,
                func.coalesce(func.sum(JournalEntryLine.debit), Decimal("0")).label(
                    "debit"
                ),
                func.coalesce(func.sum(JournalEntryLine.credit), Decimal("0")).label(
                    "credit"
                ),
            )
            .outerjoin(JournalEntryLine, Account.id == JournalEntryLine.account_id)
            .outerjoin(
                JournalEntry,
                and_(
                    JournalEntryLine.journal_entry_id == JournalEntry.id,
                    JournalEntry.date.between(start_date, end_date),
                ),
            )
            .filter(Account.company_id == company_id, Account.is_active == True)
            .group_by(Account.id, Account.code, Account.name, Account.account_type)
        )

        results = []
        for row in query.all():
            balance = row.debit - row.credit

            # Determinar saldo deudor o acreedor según naturaleza
            if row.account_type in ["activo", "gasto"]:
                final_debit = max(Decimal("0"), balance)
                final_credit = max(Decimal("0"), -balance)
            else:
                final_debit = max(Decimal("0"), -balance)
                final_credit = max(Decimal("0"), balance)

            results.append(
                TrialBalanceRow(
                    account_id=str(row.id),
                    account_code=row.code,
                    account_name=row.name,
                    account_type=row.account_type.value
                    if hasattr(row.account_type, "value")
                    else row.account_type,
                    initial_debit=Decimal("0"),  # Simplificado
                    initial_credit=Decimal("0"),
                    period_debit=row.debit,
                    period_credit=row.credit,
                    final_debit=final_debit,
                    final_credit=final_credit,
                )
            )

        return results

    def get_executive_metrics(self, company_id: UUID, end_date: date) -> Dict[str, Any]:
        """
        Genera métricas ejecutivas para dashboard.

        Returns:
            Dict con métricas sintéticas y alertas
        """
        # Períodos para comparación
        current_start = date(end_date.year, 1, 1)
        previous_start = date(end_date.year - 1, 1, 1)
        previous_end = date(end_date.year - 1, 12, 31)

        # Balanzas de comprobación
        current_tb = self.get_trial_balance(company_id, current_start, end_date)
        previous_tb = self.get_trial_balance(company_id, previous_start, previous_end)

        # Estados de resultados
        engine = FinancialEngine(str(company_id))
        current_income = engine.build_income_statement(
            current_tb, current_start, end_date
        )
        previous_income = engine.build_income_statement(
            previous_tb, previous_start, previous_end
        )
        current_balance = engine.build_balance_sheet(current_tb)

        # Facturas para aging
        ar_invoices = (
            self.db.query(Invoice)
            .filter(
                Invoice.company_id == company_id,
                Invoice.invoice_type == "income",
                Invoice.status.in_(["pending", "overdue"]),
            )
            .all()
        )

        total_ar = sum(inv.total - inv.amount_paid for inv in ar_invoices)

        # Calcular runway (meses de efectivo)
        monthly_burn = current_income.operating_expenses / 12
        runway = None
        if monthly_burn > 0:
            runway = float(current_balance.cash / monthly_burn)

        # Alertas inteligentes
        alerts = []

        if current_income.net_income < 0:
            alerts.append(
                {
                    "type": "danger",
                    "title": "Pérdida Neta",
                    "message": f"La empresa reporta pérdidas de ${abs(current_income.net_income):,.2f}",
                }
            )

        if current_balance.cash < current_income.operating_expenses / 6:
            alerts.append(
                {
                    "type": "warning",
                    "title": "Efectivo Bajo",
                    "message": "El efectivo es menor a 2 meses de gastos operativos",
                }
            )

        # Cambios porcentuales
        revenue_change = engine.calculate_percentage_change(
            current_income.revenue, previous_income.revenue
        )
        net_income_change = engine.calculate_percentage_change(
            current_income.net_income, previous_income.net_income
        )

        return {
            "revenue_current": current_income.revenue,
            "revenue_previous": previous_income.revenue,
            "revenue_change_pct": round(revenue_change * 100, 2),
            "net_income_current": current_income.net_income,
            "net_income_previous": previous_income.net_income,
            "net_income_change_pct": round(net_income_change * 100, 2),
            "ebitda_current": current_income.ebitda,
            "ebitda_margin_pct": round(current_income.ebitda_margin_pct * 100, 2),
            "cash_balance": current_balance.cash,
            "cash_runway_months": round(runway, 1) if runway else None,
            "accounts_receivable": total_ar,
            "accounts_payable": current_balance.accounts_payable,
            "working_capital": current_balance.current_assets
            - current_balance.current_liabilities,
            "alerts": alerts,
        }

    def get_financial_control_data(
        self, company_id: UUID, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """
        Genera datos completos de la capa de control financiero.

        Returns:
            Dict con análisis vertical, horizontal, ratios, etc.
        """
        # Obtener balanzas
        current_tb = self.get_trial_balance(company_id, start_date, end_date)

        # Período anterior para análisis horizontal
        days_diff = (end_date - start_date).days
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=days_diff)
        previous_tb = self.get_trial_balance(company_id, prev_start, prev_end)

        # Motor financiero
        engine = FinancialEngine(str(company_id))

        current_income = engine.build_income_statement(current_tb, start_date, end_date)
        previous_income = engine.build_income_statement(
            previous_tb, prev_start, prev_end
        )
        current_balance = engine.build_balance_sheet(current_tb)

        # Calcular todos los análisis
        ratios = engine.calculate_ratios(current_income, current_balance)

        ccc = engine.calculate_cash_conversion_cycle(
            revenue=current_income.revenue,
            cogs=current_income.cost_of_goods_sold,
            accounts_receivable=current_balance.accounts_receivable,
            accounts_payable=current_balance.accounts_payable,
            inventory=current_balance.inventory,
            days_in_period=(end_date - start_date).days,
        )

        vertical = engine.vertical_analysis(current_income)
        horizontal = engine.horizontal_analysis(current_income, previous_income)

        # Análisis de punto de equilibrio
        # Separar costos fijos y variables (simplificado)
        variable_costs = current_income.cost_of_goods_sold + (
            current_income.operating_expenses * Decimal("0.6")
        )
        fixed_costs = (
            current_income.operating_expenses * Decimal("0.4")
            + current_income.depreciation_amortization
        )

        break_even = engine.calculate_break_even(
            revenue=current_income.revenue,
            variable_costs=variable_costs,
            fixed_costs=fixed_costs,
        )

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "income_statement": {
                "revenue": current_income.revenue,
                "gross_profit": current_income.gross_profit,
                "ebitda": current_income.ebitda,
                "operating_income": current_income.operating_income,
                "net_income": current_income.net_income,
                "margins": {
                    "gross": current_income.gross_margin_pct,
                    "ebitda": current_income.ebitda_margin_pct,
                    "operating": current_income.operating_margin_pct,
                    "net": current_income.net_margin_pct,
                },
            },
            "ratios": ratios,
            "cash_conversion_cycle": ccc,
            "vertical_analysis": vertical,
            "horizontal_analysis": horizontal,
            "break_even": break_even,
        }
