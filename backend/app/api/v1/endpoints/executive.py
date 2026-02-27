"""
API endpoints para la Capa Ejecutiva - Dashboard y métricas sintéticas.
"""

from datetime import date
from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.schemas import ExecutiveMetrics
from app.services.financial_service import FinancialService

router = APIRouter()


@router.get("/metrics", response_model=Dict[str, Any])
async def get_executive_metrics(
    company_id: UUID,
    as_of_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Obtiene métricas ejecutivas para el dashboard.

    Incluye:
    - Ingresos y variación interanual
    - Utilidad neta y margen
    - EBITDA y margen
    - Posición de efectivo
    - Alertas inteligentes
    """
    service = FinancialService(db)

    try:
        metrics = service.get_executive_metrics(company_id, as_of_date)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calculando métricas: {str(e)}"
        )


@router.get("/alerts")
async def get_active_alerts(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Obtiene alertas activas para la empresa.
    """
    # Implementación básica - en producción sería más compleja
    service = FinancialService(db)
    metrics = service.get_executive_metrics(company_id, date.today())

    return {
        "company_id": str(company_id),
        "alert_count": len(metrics.get("alerts", [])),
        "alerts": metrics.get("alerts", []),
    }


@router.get("/kpis")
async def get_key_performance_indicators(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    KPIs principales en formato para gráficos.
    """
    service = FinancialService(db)
    metrics = service.get_executive_metrics(company_id, date.today())

    return {
        "revenue": {
            "current": float(metrics["revenue_current"]),
            "previous": float(metrics["revenue_previous"]),
            "change_pct": metrics["revenue_change_pct"],
        },
        "profitability": {
            "net_income": float(metrics["net_income_current"]),
            "net_income_change_pct": metrics["net_income_change_pct"],
            "ebitda": float(metrics["ebitda_current"]),
            "ebitda_margin": metrics["ebitda_margin_pct"],
        },
        "liquidity": {
            "cash": float(metrics["cash_balance"]),
            "runway_months": metrics["cash_runway_months"],
            "working_capital": float(metrics["working_capital"]),
        },
    }
