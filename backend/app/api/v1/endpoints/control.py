"""
API endpoints para la Capa de Control Financiero.
Análisis vertical, horizontal, ratios y métricas detalladas.
"""

from datetime import date
from typing import Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.schemas import (
    VerticalAnalysis,
    HorizontalAnalysis,
    FinancialRatios,
    CashConversionCycle,
    BreakEvenAnalysis,
    MarginAnalysis,
)
from app.services.financial_service import FinancialService

router = APIRouter()


@router.get("/complete-analysis")
async def get_complete_financial_analysis(
    company_id: UUID,
    start_date: date = Query(..., description="Fecha inicio período (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha fin período (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Obtiene análisis financiero completo para el período.

    Incluye:
    - Análisis vertical del estado de resultados
    - Análisis horizontal vs período anterior
    - Ratios financieros clave
    - Ciclo de conversión de efectivo
    - Análisis de punto de equilibrio
    """
    service = FinancialService(db)

    try:
        analysis = service.get_financial_control_data(company_id, start_date, end_date)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en análisis financiero: {str(e)}"
        )


@router.get("/vertical-analysis")
async def get_vertical_analysis(
    company_id: UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Análisis vertical: cada partida como % de ventas totales.
    """
    service = FinancialService(db)
    data = service.get_financial_control_data(company_id, start_date, end_date)

    return {"period": data["period"], "analysis": data["vertical_analysis"]}


@router.get("/horizontal-analysis")
async def get_horizontal_analysis(
    company_id: UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Análisis horizontal: comparación vs período anterior.
    """
    service = FinancialService(db)
    data = service.get_financial_control_data(company_id, start_date, end_date)

    return {"period": data["period"], "analysis": data["horizontal_analysis"]}


@router.get("/ratios")
async def get_financial_ratios(
    company_id: UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Ratios financieros calculados.

    Ratios incluidos:
    - Liquidez: current_ratio, quick_ratio
    - Solvencia: debt_to_equity
    - Rentabilidad: roa, roe, márgenes
    - Eficiencia: inventory_turnover, asset_turnover
    """
    service = FinancialService(db)
    data = service.get_financial_control_data(company_id, start_date, end_date)

    return {"period": data["period"], "ratios": data["ratios"]}


@router.get("/cash-conversion-cycle")
async def get_cash_conversion_cycle(
    company_id: UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Ciclo de conversión de efectivo (CCC).

    CCC = DSO + DIO - DPO
    - DSO: Días de ventas pendientes
    - DIO: Días de inventario
    - DPO: Días de cuentas por pagar
    """
    service = FinancialService(db)
    data = service.get_financial_control_data(company_id, start_date, end_date)

    return {
        "period": data["period"],
        "cash_conversion_cycle": data["cash_conversion_cycle"],
    }


@router.get("/break-even")
async def get_break_even_analysis(
    company_id: UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Análisis de punto de equilibrio operativo.
    """
    service = FinancialService(db)
    data = service.get_financial_control_data(company_id, start_date, end_date)

    return {"period": data["period"], "break_even": data["break_even"]}


@router.get("/margins")
async def get_margin_analysis(
    company_id: UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Análisis detallado de márgenes.
    """
    service = FinancialService(db)
    data = service.get_financial_control_data(company_id, start_date, end_date)
    income = data["income_statement"]

    return {
        "period": data["period"],
        "revenue": income["revenue"],
        "margins": income["margins"],
        "absolute_values": {
            "gross_profit": income["gross_profit"],
            "ebitda": income["ebitda"],
            "operating_income": income["operating_income"],
            "net_income": income["net_income"],
        },
    }
