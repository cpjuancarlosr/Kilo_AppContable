"""
API endpoints para importación de archivos y Executive Scorecard avanzado.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.services.import_service import ImportadorEstadoCuenta
from app.services.executive_scorecard import ExecutiveScorecard
from app.financial_engine.calculator import (
    FinancialEngine,
    IncomeStatement,
    BalanceSheet,
)

router = APIRouter()


@router.post("/importar-estado-cuenta")
async def importar_estado_cuenta(
    company_id: UUID = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Importa estado de cuenta bancario (PDF, CSV, Excel).

    Detecta automáticamente el banco y extrae transacciones.
    """
    # Validar tipo de archivo
    content_type = archivo.content_type or ""
    filename = archivo.filename or ""

    if "pdf" in filename.lower():
        tipo = "pdf"
    elif "csv" in filename.lower():
        tipo = "csv"
    elif any(ext in filename.lower() for ext in ["xlsx", "xls"]):
        tipo = "excel"
    else:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no soportado. Use PDF, CSV o Excel.",
        )

    # Leer archivo
    contenido = await archivo.read()

    # Importar
    importador = ImportadorEstadoCuenta()

    try:
        estado = importador.importar(contenido, tipo, filename)
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Error de importación: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error procesando archivo: {str(e)}"
        )

    # Generar resumen
    resumen_categorias = importador.generar_resumen_categorias(estado)

    return {
        "success": True,
        "banco": estado.banco,
        "cuenta": estado.cuenta,
        "moneda": estado.moneda,
        "periodo": {
            "inicio": estado.fecha_inicio.isoformat(),
            "fin": estado.fecha_fin.isoformat(),
        },
        "saldos": {
            "inicial": float(estado.saldo_inicial),
            "final": float(estado.saldo_final),
            "balance_verificado": estado.balance_verificado,
        },
        "movimientos": {
            "total": len(estado.transacciones),
            "total_cargos": float(estado.total_cargos),
            "total_abonos": float(estado.total_abonos),
            "neto": float(estado.total_abonos - estado.total_cargos),
        },
        "resumen_por_categoria": {
            cat: {
                "cantidad": data["cantidad"],
                "cargos": float(data["cargos"]),
                "abonos": float(data["abonos"]),
                "neto": float(data["neto"]),
            }
            for cat, data in resumen_categorias.items()
        },
        "transacciones": [
            {
                "fecha": t.fecha.isoformat(),
                "descripcion": t.descripcion,
                "categoria": t.categoria_sugerida,
                "cargo": float(t.cargo) if t.cargo else None,
                "abono": float(t.abono) if t.abono else None,
                "rfc_detectado": t.rfc_detectado,
            }
            for t in estado.transacciones[:50]  # Limitar a 50 para respuesta
        ],
        "errores_importacion": importador.errores,
    }


@router.get("/scorecard-ejecutivo")
async def get_executive_scorecard(
    company_id: UUID,
    fecha_corte: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Genera Executive Scorecard con indicadores críticos y alertas predictivas.

    Proporciona:
    - Health Score financiero
    - KPIs críticos semáforo
    - Alertas predictivas
    - Recomendaciones de acción
    """
    # Crear scorecard
    scorecard = ExecutiveScorecard(str(company_id), fecha_corte)

    # Datos de ejemplo para demostración
    # En producción, estos vendrían de la base de datos
    income = IncomeStatement(
        revenue=Decimal("2450000"),
        cost_of_goods_sold=Decimal("1400000"),
        gross_profit=Decimal("1050000"),
        operating_expenses=Decimal("612500"),
        operating_income=Decimal("437500"),
        depreciation_amortization=Decimal("175000"),
        ebitda=Decimal("612500"),
        financial_expenses=Decimal("87500"),
        other_expenses=Decimal("0"),
        income_tax=Decimal("105000"),
        net_income=Decimal("245000"),
    )

    balance = BalanceSheet(
        current_assets=Decimal("980000"),
        cash=Decimal("245000"),
        accounts_receivable=Decimal("367500"),
        inventory=Decimal("245000"),
        other_current_assets=Decimal("122500"),
        non_current_assets=Decimal("1470000"),
        total_assets=Decimal("2450000"),
        current_liabilities=Decimal("612500"),
        accounts_payable=Decimal("245000"),
        short_term_debt=Decimal("122500"),
        other_current_liabilities=Decimal("245000"),
        non_current_liabilities=Decimal("735000"),
        long_term_debt=Decimal("490000"),
        total_liabilities=Decimal("1347500"),
        equity=Decimal("1102500"),
        total_liabilities_equity=Decimal("2450000"),
    )

    # Generar scorecard
    resultado = scorecard.generar_scorecard_completo(
        income=income,
        balance=balance,
        cash_flow_operaciones=Decimal("367500"),
        flujo_inversion=Decimal("-175000"),
        flujo_financiamiento=Decimal("-70000"),
        empleados=25,
        dividendos=Decimal("50000"),
        utilidad_retenida_acum=Decimal("450000"),
    )

    return resultado


@router.get("/scorecard/metricas-avanzadas")
async def get_metricas_avanzadas(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Métricas financieras avanzadas para análisis profundo.

    Incluye:
    - Altman Z-Score
    - Análisis DuPont
    - Ratios de distress
    - Análisis de sensibilidad
    """
    from app.financial_engine.advanced_indicators import IndicadoresAvanzados

    # Datos de ejemplo
    ventas = Decimal("2450000")
    ebitda = Decimal("612500")
    utilidad_neta = Decimal("245000")
    activos = Decimal("2450000")
    patrimonio = Decimal("1102500")

    # Calcular indicadores
    dupont = IndicadoresAvanzados.calcular_dupont(
        utilidad_neta=utilidad_neta,
        ventas=ventas,
        total_activos=activos,
        patrimonio=patrimonio,
    )

    # Z-Score
    zscore = IndicadoresAvanzados.calcular_altman_zscore(
        activo_circulante=Decimal("980000"),
        pasivo_circulante=Decimal("612500"),
        utilidad_retenida=Decimal("450000"),
        ebit=Decimal("525000"),
        capital_social=patrimonio,
        ventas=ventas,
        total_activos=activos,
        total_pasivos=Decimal("1347500"),
    )

    # Ratios de distress
    distress = IndicadoresAvanzados.calcular_ratios_distress(
        flujo_operaciones=Decimal("367500"),
        deuda_total=Decimal("612500"),
        ebitda=ebitda,
        intereses=Decimal("87500"),
        pasivo_circulante=Decimal("612500"),
        activo_circulante=Decimal("980000"),
    )

    # Eficiencia operativa
    eficiencia = IndicadoresAvanzados.calcular_eficiencia_operativa(
        ventas=ventas,
        costo_ventas=Decimal("1400000"),
        inventario_promedio=Decimal("245000"),
        cuentas_por_cobrar=Decimal("367500"),
        cuentas_por_pagar=Decimal("245000"),
        activos_totales=activos,
    )

    return {
        "analisis_dupont": {
            "roe": dupont.roe,
            "roa": dupont.roa,
            "margen_neto": dupont.margen_neto,
            "rotacion_activos": dupont.rotacion_activos,
            "multiplicador_capital": dupont.multiplicador_capital,
        },
        "altman_zscore": {
            "valor": zscore.z_score,
            "riesgo": zscore.riesgo,
            "probabilidad_bancarrota": zscore.probabilidad_bancarrota,
            "interpretacion": zscore.interpretacion,
            "componentes": zscore.componentes,
        },
        "ratios_distress": distress,
        "eficiencia_operativa": eficiencia,
    }


@router.post("/analisis-sensibilidad")
async def analisis_sensibilidad(
    company_id: UUID,
    ventas_actuales: float = Query(...),
    utilidad_actual: float = Query(...),
    costos_fijos: float = Query(...),
    costos_variables: float = Query(...),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Análisis de sensibilidad de utilidades ante cambios en ventas.

    Muestra el impacto de escenarios de ventas en la utilidad.
    """
    from app.financial_engine.advanced_indicators import IndicadoresAvanzados

    sensibilidad = IndicadoresAvanzados.calcular_sensibilidad(
        ventas_actuales=Decimal(str(ventas_actuales)),
        utilidad_actual=Decimal(str(utilidad_actual)),
        costos_fijos=Decimal(str(costos_fijos)),
        costos_variables=Decimal(str(costos_variables)),
    )

    return {"company_id": str(company_id), "analisis": sensibilidad}


@router.get("/kpis-sectoriales")
async def get_kpis_sectoriales(
    company_id: UUID,
    sector: str = Query(
        "general",
        enum=[
            "tecnologia",
            "manufactura",
            "retail",
            "servicios",
            "construccion",
            "general",
        ],
    ),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    KPIs específicos por sector para benchmarking.
    """
    from app.financial_engine.advanced_indicators import IndicadoresAvanzados

    kpis = IndicadoresAvanzados.calcular_kpis_sectoriales(
        ventas=Decimal("2450000"),
        ebitda=Decimal("612500"),
        activos_netos=Decimal("1470000"),
        empleados=25,
        sector=sector,
    )

    return {"company_id": str(company_id), "sector": sector, "kpis": kpis}


@router.get("/tendencias")
async def analizar_tendencias(
    company_id: UUID,
    meses: int = Query(12, ge=3, le=36),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Análisis de tendencias históricas.

    Detecta patrones de mejora o deterioro en métricas clave.
    """
    # En producción: consultar datos históricos de la BD

    tendencias = {
        "periodos": meses,
        "ingresos": {
            "tendencia": "creciente",
            "cambio_promedio_mensual": 2.5,
            "proyeccion_3_meses": 2780000,
        },
        "margen_bruto": {"tendencia": "estable", "promedio": 0.42, "desviacion": 0.02},
        "liquidez": {
            "tendencia": "deterioro",
            "cambio": -0.15,
            "alerta": "Current ratio ha disminuido los últimos 3 meses",
        },
    }

    return {"company_id": str(company_id), "tendencias": tendencias}
