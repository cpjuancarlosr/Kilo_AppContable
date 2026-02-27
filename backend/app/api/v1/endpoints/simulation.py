"""
API endpoints para la Capa de Simulación Estratégica.
Modelado de escenarios, proyecciones y análisis de sensibilidad.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.schemas import ScenarioCreate, ScenarioResponse, ScenarioParameters
from app.financial_engine.calculator import FinancialEngine

router = APIRouter()


@router.post("/growth")
async def simulate_growth_scenario(
    company_id: UUID,
    base_revenue: Decimal = Query(..., description="Ingresos base mensuales"),
    base_expenses: Decimal = Query(..., description="Gastos base mensuales"),
    annual_growth_rate: float = Query(
        0.20, description="Tasa crecimiento anual (0.20 = 20%)"
    ),
    months: int = Query(12, ge=6, le=60),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Simula escenario de crecimiento.

    Proyecta ingresos, gastos y rentabilidad con la tasa de crecimiento especificada.
    """
    engine = FinancialEngine(str(company_id))

    simulation = engine.simulate_growth_scenario(
        base_revenue=base_revenue,
        base_expenses=base_expenses,
        growth_rate_annual=annual_growth_rate,
        months=months,
    )

    # Calcular métricas agregadas
    total_revenue = sum(s["revenue"] for s in simulation)
    total_net_income = sum(s["net_income"] for s in simulation)
    avg_margin = sum(
        s["net_income"] / s["revenue"] for s in simulation if s["revenue"] > 0
    ) / len(simulation)

    return {
        "scenario_type": "growth",
        "parameters": {
            "base_revenue": base_revenue,
            "base_expenses": base_expenses,
            "annual_growth_rate": annual_growth_rate,
            "months": months,
        },
        "summary": {
            "total_projected_revenue": total_revenue,
            "total_projected_net_income": total_net_income,
            "average_net_margin": avg_margin,
            "final_month_revenue": simulation[-1]["revenue"] if simulation else 0,
            "final_month_net_income": simulation[-1]["net_income"] if simulation else 0,
        },
        "monthly_projections": simulation,
    }


@router.post("/pricing")
async def simulate_pricing_scenario(
    company_id: UUID,
    base_revenue: Decimal = Query(...),
    base_expenses: Decimal = Query(...),
    price_change_pct: float = Query(
        0.10, description="Cambio en precios (0.10 = +10%)"
    ),
    expected_volume_change_pct: float = Query(
        -0.05, description="Cambio esperado en volumen"
    ),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Simula impacto de cambio en precios.

    Analiza cómo afecta a EBITDA un cambio en precios considerando
    elasticidad de demanda (cambio en volumen).
    """
    engine = FinancialEngine(str(company_id))

    simulation = engine.simulate_price_change(
        base_revenue=base_revenue,
        base_expenses=base_expenses,
        price_change_pct=price_change_pct,
        volume_change_pct=expected_volume_change_pct,
    )

    return {
        "scenario_type": "pricing",
        "parameters": {
            "base_revenue": base_revenue,
            "base_expenses": base_expenses,
            "price_change_pct": price_change_pct,
            "expected_volume_change_pct": expected_volume_change_pct,
        },
        "simulation": simulation,
    }


@router.post("/financing")
async def simulate_financing_impact(
    company_id: UUID,
    current_revenue: Decimal = Query(...),
    current_expenses: Decimal = Query(...),
    current_debt: Decimal = Query(default=Decimal("0")),
    new_financing: Decimal = Query(..., description="Monto de nuevo financiamiento"),
    interest_rate: float = Query(0.12, description="Tasa anual (0.12 = 12%)"),
    term_months: int = Query(36, ge=12, le=120),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Simula impacto de nuevo financiamiento.

    Calcula:
    - Pago mensual requerido
    - Impacto en flujo de efectivo
    - DSCR (Debt Service Coverage Ratio)
    """
    engine = FinancialEngine(str(company_id))

    simulation = engine.simulate_financing_impact(
        current_revenue=current_revenue,
        current_expenses=current_expenses,
        current_debt=current_debt,
        new_financing=new_financing,
        interest_rate=interest_rate,
        term_months=term_months,
    )

    return {
        "scenario_type": "financing",
        "parameters": {
            "current_revenue": current_revenue,
            "current_expenses": current_expenses,
            "current_debt": current_debt,
            "new_financing": new_financing,
            "interest_rate": interest_rate,
            "term_months": term_months,
        },
        "simulation": simulation,
    }


@router.post("/compare-scenarios")
async def compare_multiple_scenarios(
    company_id: UUID,
    base_revenue: Decimal = Query(...),
    base_expenses: Decimal = Query(...),
    scenarios: List[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Compara múltiples escenarios lado a lado.
    """
    if scenarios is None:
        # Escenarios por defecto
        scenarios = [
            {"name": "Conservador", "growth_rate": 0.05},
            {"name": "Base", "growth_rate": 0.10},
            {"name": "Optimista", "growth_rate": 0.25},
        ]

    engine = FinancialEngine(str(company_id))
    results = []

    for scenario in scenarios:
        sim = engine.simulate_growth_scenario(
            base_revenue=base_revenue,
            base_expenses=base_expenses,
            growth_rate_annual=scenario.get("growth_rate", 0.10),
            months=12,
        )

        total_revenue = sum(s["revenue"] for s in sim)
        total_net_income = sum(s["net_income"] for s in sim)

        results.append(
            {
                "name": scenario.get("name", "Escenario"),
                "growth_rate": scenario.get("growth_rate"),
                "total_revenue": total_revenue,
                "total_net_income": total_net_income,
                "avg_margin": float(total_net_income / total_revenue)
                if total_revenue > 0
                else 0,
                "final_ebitda": sim[-1]["ebitda"] if sim else 0,
            }
        )

    # Encontrar mejor escenario
    best = max(results, key=lambda x: x["total_net_income"])

    return {
        "base_parameters": {"revenue": base_revenue, "expenses": base_expenses},
        "comparison": results,
        "recommendation": {
            "best_scenario": best["name"],
            "expected_net_income": best["total_net_income"],
        },
    }


@router.post("/expansion")
async def simulate_expansion_scenario(
    company_id: UUID,
    current_revenue: Decimal = Query(...),
    current_expenses: Decimal = Query(...),
    expansion_investment: Decimal = Query(..., description="Inversión inicial"),
    additional_monthly_cost: Decimal = Query(
        ..., description="Costo operativo adicional mensual"
    ),
    revenue_uplift_pct: float = Query(
        0.30, description="Incremento esperado en ingresos"
    ),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Simula escenario de expansión (nueva ubicación, producto, etc.).
    """
    months = 24
    engine = FinancialEngine(str(company_id))

    # Escenario base (sin expansión)
    base_scenario = engine.simulate_growth_scenario(
        current_revenue, current_expenses, 0.05, months
    )

    # Escenario con expansión
    new_base_revenue = current_revenue * Decimal(str(1 + revenue_uplift_pct))
    new_base_expenses = current_expenses + additional_monthly_cost

    expansion_scenario = engine.simulate_growth_scenario(
        new_base_revenue, new_base_expenses, 0.05, months
    )

    # Calcular ROI de expansión
    base_profit = sum(s["net_income"] for s in base_scenario)
    expansion_profit = sum(s["net_income"] for s in expansion_scenario)
    incremental_profit = expansion_profit - base_profit

    roi = (
        float(incremental_profit / expansion_investment)
        if expansion_investment > 0
        else 0
    )

    # Mes de recuperación
    cumulative_diff = Decimal("0")
    payback_month = None
    for i, (base, exp) in enumerate(zip(base_scenario, expansion_scenario)):
        cumulative_diff += exp["net_income"] - base["net_income"]
        if cumulative_diff >= expansion_investment and payback_month is None:
            payback_month = i + 1

    return {
        "scenario_type": "expansion",
        "investment": expansion_investment,
        "analysis": {
            "base_scenario_profit": base_profit,
            "expansion_scenario_profit": expansion_profit,
            "incremental_profit": incremental_profit,
            "roi_24_months": roi,
            "payback_months": payback_month,
            "recommendation": "PROCEED"
            if roi > 0.5 and payback_month and payback_month <= 18
            else "REVIEW",
        },
        "monthly_comparison": [
            {
                "month": i + 1,
                "base_net_income": b["net_income"],
                "expansion_net_income": e["net_income"],
                "difference": e["net_income"] - b["net_income"],
            }
            for i, (b, e) in enumerate(zip(base_scenario, expansion_scenario))
        ],
    }
