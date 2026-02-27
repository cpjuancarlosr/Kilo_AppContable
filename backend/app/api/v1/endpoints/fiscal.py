"""
API endpoints para la Capa Fiscal Estratégica.
Análisis de carga fiscal, proyecciones y riesgo fiscal.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.financial_engine.calculator import FinancialEngine

router = APIRouter()


@router.get("/summary")
async def get_tax_summary(
    company_id: UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Resumen de carga fiscal para el período.

    Incluye:
    - Ingresos gravables
    - ISR pagado/provisionado
    - IVA neto
    - Tasa efectiva de impuestos
    """
    # En implementación real, estos datos vendrían de la base de datos
    # Aquí usamos valores de ejemplo

    revenue = Decimal("1000000")
    taxable_income = Decimal("200000")
    vat_collected = Decimal("160000")
    vat_paid = Decimal("80000")

    engine = FinancialEngine(str(company_id))
    tax_data = engine.calculate_tax_burden(
        revenue=revenue,
        taxable_income=taxable_income,
        vat_collected=vat_collected,
        vat_paid=vat_paid,
    )

    return {
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "tax_summary": tax_data,
    }


@router.get("/projection")
async def get_tax_projection(
    company_id: UUID,
    base_revenue: Decimal = Query(..., description="Ingresos base mensuales"),
    base_taxable_income: Decimal = Query(..., description="Utilidad gravable base"),
    growth_rate: float = Query(
        0.05, description="Tasa de crecimiento mensual esperada"
    ),
    months: int = Query(12, ge=1, le=36),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Proyección de impuestos a 12 meses.
    """
    # Generar tasas de crecimiento
    growth_rates = [growth_rate] * months

    engine = FinancialEngine(str(company_id))
    projections = engine.project_taxes(
        base_revenue=base_revenue,
        base_taxable_income=base_taxable_income,
        growth_rates=growth_rates,
    )

    return {
        "parameters": {
            "base_revenue": base_revenue,
            "base_taxable_income": base_taxable_income,
            "growth_rate": growth_rate,
            "months": months,
        },
        "projections": projections,
        "totals": {
            "total_revenue": sum(p["projected_revenue"] for p in projections),
            "total_tax": projections[-1]["cumulative_tax"] if projections else 0,
        },
    }


@router.get("/effective-rate-history")
async def get_effective_tax_rate_history(
    company_id: UUID,
    years: int = Query(3, ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Histórico de tasa efectiva de impuestos.
    """
    # Datos de ejemplo - en producción se calculan de la base de datos
    history = [
        {"year": date.today().year - 2, "effective_rate": 28.5, "revenue": 850000},
        {"year": date.today().year - 1, "effective_rate": 29.2, "revenue": 920000},
        {"year": date.today().year, "effective_rate": 30.1, "revenue": 1000000},
    ]

    return {"company_id": str(company_id), "history": history[-years:]}


@router.post("/impact-simulation")
async def simulate_tax_impact(
    company_id: UUID,
    revenue_change_pct: float,
    cost_structure_change: float = 0,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Simula impacto fiscal ante cambios en ingresos.
    """
    base_revenue = Decimal("1000000")
    base_taxable = Decimal("200000")

    # Escenario base
    engine = FinancialEngine(str(company_id))
    base_tax = engine.calculate_tax_burden(
        base_revenue, base_taxable, Decimal("160000"), Decimal("80000")
    )

    # Escenario modificado
    new_revenue = base_revenue * Decimal(str(1 + revenue_change_pct))
    new_taxable = base_taxable * Decimal(
        str(1 + revenue_change_pct + cost_structure_change)
    )
    new_tax = engine.calculate_tax_burden(
        new_revenue,
        new_taxable,
        new_revenue * Decimal("0.16"),
        new_revenue * Decimal("0.08"),
    )

    return {
        "scenarios": {"base": base_tax, "projected": new_tax},
        "impact": {
            "tax_change": float(new_tax["total_tax"] - base_tax["total_tax"]),
            "effective_rate_change": new_tax["effective_tax_rate"]
            - base_tax["effective_tax_rate"],
        },
    }


@router.get("/risk-assessment")
async def get_fiscal_risk_assessment(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Evaluación de riesgo fiscal.

    Analiza:
    - Cumplimiento de obligaciones
    - Variaciones anormales
    - Deductibilidad de gastos
    """
    # Implementación simplificada
    risk_factors = [
        {"factor": "variacion_ingresos", "risk_level": "low", "score": 2},
        {"factor": "deducciones", "risk_level": "medium", "score": 5},
        {"factor": "retenciones", "risk_level": "low", "score": 1},
    ]

    total_score = sum(r["score"] for r in risk_factors)

    risk_level = "low"
    if total_score > 10:
        risk_level = "high"
    elif total_score > 5:
        risk_level = "medium"

    return {
        "company_id": str(company_id),
        "risk_level": risk_level,
        "total_score": total_score,
        "factors": risk_factors,
        "recommendations": [
            "Revisar documentación de gastos deducibles",
            "Verificar retenciones de ISR",
            "Actualizar pago de impuestos",
        ]
        if risk_level != "low"
        else [],
    }
