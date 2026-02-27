"""
API endpoints específicos para México (CFDI, DIOT, Retenciones).
"""

from datetime import date
from decimal import Decimal
from typing import Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.schemas import (
    CFDICreate,
    CFDIResponse,
    CFDIConceptoCreate,
    RetencionISRCreate,
    RetencionISRResponse,
    DIOTOperacionCreate,
    DIOTOperacionResponse,
    DIOTResumen,
    CalculoFiscalMX,
    EmpresaMXCreate,
    EmpresaMXResponse,
)
from app.financial_engine.mexico_tax_engine import MotorFiscalMX, proyectar_isres_anual

router = APIRouter()


@router.post("/empresa", response_model=EmpresaMXResponse)
async def registrar_empresa_mx(
    empresa: EmpresaMXCreate,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
):
    """
    Registra datos fiscales de empresa mexicana.

    Incluye RFC, régimen fiscal, datos del SAT.
    """
    # Validar RFC (simplificado)
    if len(empresa.rfc) not in [12, 13]:
        raise HTTPException(status_code=400, detail="RFC inválido")

    # En implementación real: guardar en BD
    return {
        "id": "uuid-generado",
        **empresa.model_dump(),
        "es_zona_fronteriza": empresa.codigo_postal.startswith("21")
        or empresa.codigo_postal.startswith("83"),
        "activa_en_sat": True,
        "created_at": date.today().isoformat(),
    }


@router.post("/cfdi/calcular")
async def calcular_cfdi(
    conceptos: List[CFDIConceptoCreate],
    codigo_postal_emisor: str = Query(..., min_length=5, max_length=5),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Calcula impuestos para un CFDI antes de emitirlo.

    Devuelve desglose de IVA, IEPS y totales.
    """
    motor = MotorFiscalMX(codigo_postal=codigo_postal_emisor)

    conceptos_dict = [c.model_dump() for c in conceptos]
    resultado = motor.calcular_factura_completa(conceptos_dict)

    return {
        "desglose": resultado,
        "tasa_iva_aplicada": resultado["tasa_iva_aplicada"],
        "es_zona_fronteriza": motor.tasa_iva == 0.08,
    }


@router.get("/cfdi/validar-rfc/{rfc}")
async def validar_rfc(
    rfc: str,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Valida formato de RFC mexicano.

    En producción: consultar servicio del SAT.
    """
    # Validación básica de formato
    es_valido = len(rfc) in [12, 13]
    es_persona_fisica = len(rfc) == 13

    return {
        "rfc": rfc,
        "valido": es_valido,
        "tipo": "persona_fisica" if es_persona_fisica else "persona_moral",
        "situacion_sat": "ACTIVO",  # En producción: consultar SAT
        "supuestos": [],
    }


@router.post("/retenciones/calcular")
async def calcular_retencion_isr(
    base: Decimal = Query(..., gt=0),
    tipo_pago: str = Query(
        ...,
        enum=["arrendamiento", "honorarios", "comisiones", "dividendos", "intereses"],
    ),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Calcula retención de ISR según tipo de pago.

    Tasas:
    - Arrendamiento: 10%
    - Honorarios: 10%
    - Comisiones: 10%
    - Dividendos: 10%
    - Intereses: 0.15% a 20%
    """
    motor = MotorFiscalMX()
    retencion = motor.calcular_isr_retenido(base, tipo_pago)

    return {
        "tipo_pago": tipo_pago,
        "base": float(retencion.base),
        "tasa": float(retencion.tasa),
        "retencion_isr": float(retencion.importe),
        "monto_neto": float(base - retencion.importe),
    }


@router.get("/retenciones/acreditables")
async def get_retenciones_acreditables(
    company_id: UUID,
    ejercicio: int = Query(..., ge=2020, le=2030),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Obtiene retenciones de ISR acreditables por período.

    Estas retenciones se acreditan contra ISR a cargo.
    """
    # Datos de ejemplo
    retenciones = [
        {"mes": 1, "monto": 15000, "tipo": "honorarios", "acreditada": True},
        {"mes": 2, "monto": 12000, "tipo": "arrendamiento", "acreditada": True},
        {"mes": 3, "monto": 18000, "tipo": "honorarios", "acreditada": False},
    ]

    total_acreditado = sum(r["monto"] for r in retenciones if r["acreditada"])
    total_pendiente = sum(r["monto"] for r in retenciones if not r["acreditada"])

    return {
        "ejercicio": ejercicio,
        "retenciones": retenciones,
        "totales": {
            "acreditado": total_acreditado,
            "pendiente": total_pendiente,
            "total": total_acreditado + total_pendiente,
        },
    }


@router.post("/diot/calcular")
async def calcular_diot(
    company_id: UUID,
    ejercicio: int = Query(...),
    mes: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Calcula declaración DIOT mensual.

    Incluye operaciones con proveedores y acreditamiento de IVA.
    """
    # En producción: calcular desde facturas recibidas
    proveedores = [
        {
            "rfc": "ABC010101ABC",
            "nombre": "Proveedor A",
            "valor": 100000,
            "iva": 16000,
            "tipo": "04",
        },
        {
            "rfc": "DEF020202DEF",
            "nombre": "Proveedor B",
            "valor": 80000,
            "iva": 6400,
            "tipo": "04",
        },
        {
            "rfc": "GHI030303GHI",
            "nombre": "Proveedor C",
            "valor": 50000,
            "iva": 0,
            "tipo": "05",
        },  # Extranjero
    ]

    total_iva_acreditable = sum(p["iva"] for p in proveedores)
    total_operaciones = sum(p["valor"] for p in proveedores)

    return {
        "company_id": str(company_id),
        "periodo": f"{ejercicio}-{mes:02d}",
        "resumen": {
            "total_proveedores": len(proveedores),
            "total_operaciones": total_operaciones,
            "total_iva_acreditable": total_iva_acreditable,
            "total_iva_no_acreditable": 0,
        },
        "proveedores": proveedores,
        "fecha_limite_presentacion": f"{ejercicio}-{mes + 1:02d}-17"
        if mes < 12
        else f"{ejercicio + 1}-01-17",
    }


@router.post("/isr/proyeccion-anual")
async def proyectar_isr_anual(
    company_id: UUID,
    ingresos_mensuales: List[float] = Query(...),
    deducciones_estimadas: float = Query(...),
    isr_retenido_estimado: float = Query(default=0),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Proyecta ISR anual basado en ingresos mensuales estimados.

    Útil para planificación fiscal y estimación de pagos provisionales.
    """
    ingresos = [Decimal(str(i)) for i in ingresos_mensuales]

    proyeccion = proyectar_isres_anual(
        ingresos_mensuales=ingresos,
        deducciones_estimadas=Decimal(str(deducciones_estimadas)),
        isr_retenido_estimado=Decimal(str(isr_retenido_estimado)),
    )

    return {
        "company_id": str(company_id),
        "proyeccion": proyeccion,
        "meses_ingresos": len(ingresos_mensuales),
        "promedio_mensual_ingresos": sum(ingresos) / len(ingresos) if ingresos else 0,
    }


@router.post("/isr/pago-provisional")
async def calcular_pago_provisional(
    company_id: UUID,
    ingresos_acumulables: float = Query(...),
    deducciones_autorizadas: float = Query(...),
    isr_retenido_periodo: float = Query(default=0),
    pagos_provisionales_anteriores: float = Query(default=0),
    coeficiente_utilidad: float = Query(default=0.10),
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Calcula pago provisional de ISR mensual.

    Para personas morales con fines de lucro.
    """
    motor = MotorFiscalMX()

    calculo = motor.calcular_pago_provisional_isr(
        ingresos_acumulables_periodo=Decimal(str(ingresos_acumulables)),
        deducciones_autorizadas_periodo=Decimal(str(deducciones_autorizadas)),
        isr_retenido_periodo=Decimal(str(isr_retenido_periodo)),
        pagos_provisionales_anteriores=Decimal(str(pagos_provisionales_anteriores)),
        coeficiente_utilidad=Decimal(str(coeficiente_utilidad)),
    )

    return {
        "company_id": str(company_id),
        "calculo_isr": calculo,
        "fecha_limite_pago": "17 del mes siguiente",
        "medio_pago": "Banca electrónica o línea de captura",
    }


@router.get("/catalogos/regimenes-fiscales")
async def get_regimenes_fiscales(
    db: Session = Depends(get_db), current_user: Dict = Depends(get_current_user)
) -> List[Dict[str, str]]:
    """
    Retorna catálogo de regímenes fiscales del SAT.
    """
    return [
        {"clave": "601", "descripcion": "General de Ley Personas Morales"},
        {"clave": "603", "descripcion": "Personas Morales con Fines no Lucrativos"},
        {
            "clave": "605",
            "descripcion": "Sueldos y Salarios e Ingresos Asimilados a Salarios",
        },
        {"clave": "606", "descripcion": "Arrendamiento"},
        {"clave": "608", "descripcion": "Demás ingresos"},
        {"clave": "609", "descripcion": "Consolidación"},
        {
            "clave": "610",
            "descripcion": "Residentes en el Extranjero sin Establecimiento Permanente en México",
        },
        {
            "clave": "611",
            "descripcion": "Ingresos por Dividendos (socios y accionistas)",
        },
        {
            "clave": "612",
            "descripcion": "Personas Físicas con Actividades Empresariales y Profesionales",
        },
        {"clave": "614", "descripcion": "Ingresos por intereses"},
        {
            "clave": "615",
            "descripcion": "Régimen de los ingresos por obtención de premios",
        },
        {"clave": "616", "descripcion": "Sin obligaciones fiscales"},
        {
            "clave": "620",
            "descripcion": "Sociedades Cooperativas de Producción que optan por diferir sus ingresos",
        },
        {"clave": "621", "descripcion": "Incorporación Fiscal"},
        {
            "clave": "622",
            "descripcion": "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras",
        },
        {"clave": "623", "descripcion": "Opcional para Grupos de Sociedades"},
        {"clave": "624", "descripcion": "Coordinados"},
        {
            "clave": "625",
            "descripcion": "Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas",
        },
        {"clave": "626", "descripcion": "Régimen Simplificado de Confianza"},
    ]


@router.get("/catalogos/usos-cfdi")
async def get_usos_cfdi(
    db: Session = Depends(get_db), current_user: Dict = Depends(get_current_user)
) -> List[Dict[str, str]]:
    """
    Retorna catálogo de usos CFDI del SAT.
    """
    return [
        {"clave": "G01", "descripcion": "Adquisición de mercancías"},
        {"clave": "G02", "descripcion": "Devoluciones, descuentos o bonificaciones"},
        {"clave": "G03", "descripcion": "Gastos en general"},
        {"clave": "I01", "descripcion": "Construcciones"},
        {
            "clave": "I02",
            "descripcion": "Mobiliario y equipo de oficina por inversiones",
        },
        {"clave": "I03", "descripcion": "Equipo de transporte"},
        {"clave": "I04", "descripcion": "Equipo de computo y accesorios"},
        {
            "clave": "I05",
            "descripcion": "Dados, troqueles, moldes, matrices y herramental",
        },
        {"clave": "I06", "descripcion": "Comunicaciones telefónicas"},
        {"clave": "I07", "descripcion": "Comunicaciones satelitales"},
        {"clave": "I08", "descripcion": "Otra maquinaria y equipo"},
        {
            "clave": "D01",
            "descripcion": "Honorarios médicos, dentales y gastos hospitalarios",
        },
        {
            "clave": "D02",
            "descripcion": "Gastos médicos por incapacidad o discapacidad",
        },
        {"clave": "D03", "descripcion": "Gastos funerales"},
        {"clave": "D04", "descripcion": "Donativos"},
        {
            "clave": "D05",
            "descripcion": "Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación)",
        },
        {"clave": "D06", "descripcion": "Aportaciones voluntarias al SAR"},
        {"clave": "D07", "descripcion": "Primas por seguros de gastos médicos"},
        {"clave": "D08", "descripcion": "Gastos de transportación escolar obligatoria"},
        {
            "clave": "D09",
            "descripcion": "Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones",
        },
        {
            "clave": "D10",
            "descripcion": "Pagos por servicios educativos (colegiaturas)",
        },
        {"clave": "S01", "descripcion": "Sin efectos fiscales"},
        {"clave": "CP01", "descripcion": "Pagos"},
        {"clave": "CN01", "descripcion": "Nómina"},
    ]
