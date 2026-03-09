"""API contable/fiscal basada en CFDI."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.accounting_models import CFDI
from app.reports.financial_reports import estado_resultados
from app.services.accounting_service import AccountingService

router = APIRouter()


class UploadCFDIRequest(BaseModel):
    empresa_id: UUID
    empresa_rfc: str
    xml_content: str


@router.post("/upload_cfdi")
def upload_cfdi(payload: UploadCFDIRequest, db: Session = Depends(get_db)):
    service = AccountingService(db)
    cfdi = service.process_cfdi(payload.empresa_id, payload.empresa_rfc, payload.xml_content)
    return {"uuid": cfdi.uuid_fiscal, "cfdi_id": cfdi.id}


@router.get("/cfdi/{uuid}")
def get_cfdi(uuid: str, db: Session = Depends(get_db)):
    cfdi = db.query(CFDI).filter(CFDI.uuid_fiscal == uuid).first()
    if not cfdi:
        raise HTTPException(status_code=404, detail="CFDI no encontrado")
    return {
        "uuid": cfdi.uuid_fiscal,
        "tipo": cfdi.tipo_comprobante,
        "emisor": cfdi.nombre_emisor,
        "receptor": cfdi.nombre_receptor,
        "total": cfdi.total,
    }


@router.get("/reportes/estado_resultados/{empresa_id}")
def reporte_estado_resultados(empresa_id: UUID, db: Session = Depends(get_db)):
    return estado_resultados(db, empresa_id)


@router.get("/reportes/balance_general/{empresa_id}")
def reporte_balance_general(empresa_id: UUID, db: Session = Depends(get_db)):
    er = estado_resultados(db, empresa_id)
    return {
        "activo": er["ingresos"],
        "pasivo": er["gastos"],
        "capital": er["utilidad_neta"],
    }


@router.get("/tax/snapshot")
def tax_snapshot(
    iva_trasladado: Decimal,
    iva_acreditable: Decimal,
    ingresos: Decimal,
    deducciones: Decimal,
    db: Session = Depends(get_db),
):
    service = AccountingService(db)
    return service.fiscal_snapshot(iva_trasladado, iva_acreditable, ingresos, deducciones)
