"""Parser CFDI 3.3 y 4.0 basado en ElementTree."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
import xml.etree.ElementTree as ET

CFDI_NS = "http://www.sat.gob.mx/cfd/4"
CFDI33_NS = "http://www.sat.gob.mx/cfd/3"
TFD_NS = "http://www.sat.gob.mx/TimbreFiscalDigital"
PAGO20_NS = "http://www.sat.gob.mx/Pagos20"
NOMINA12_NS = "http://www.sat.gob.mx/nomina12"


@dataclass
class CFDIParseResult:
    version: str
    uuid: str
    fecha_emision: str
    tipo_comprobante: str
    rfc_emisor: str
    nombre_emisor: str
    rfc_receptor: str
    nombre_receptor: str
    subtotal: Decimal
    iva_trasladado: Decimal
    iva_retenido: Decimal
    total: Decimal
    moneda: str
    metodo_pago: str | None
    forma_pago: str | None
    uso_cfdi: str | None
    tiene_timbre: bool
    tiene_complemento_pago: bool
    tiene_nomina: bool
    conceptos: list[dict[str, Any]] = field(default_factory=list)
    impuestos: list[dict[str, Any]] = field(default_factory=list)


class CFDIParser:
    def parse_xml_content(self, xml_content: str) -> CFDIParseResult:
        root = ET.fromstring(xml_content)
        version = root.attrib.get("Version", "4.0")
        ns_cfdi = CFDI_NS if version == "4.0" else CFDI33_NS
        ns = {"cfdi": ns_cfdi, "tfd": TFD_NS, "pago20": PAGO20_NS, "nomina12": NOMINA12_NS}

        emisor = root.find("cfdi:Emisor", ns)
        receptor = root.find("cfdi:Receptor", ns)
        conceptos_nodes = root.findall("cfdi:Conceptos/cfdi:Concepto", ns)
        impuestos_global = root.find("cfdi:Impuestos", ns)
        complemento = root.find("cfdi:Complemento", ns)

        uuid = ""
        tiene_timbre = False
        tiene_complemento_pago = False
        tiene_nomina = False
        if complemento is not None:
            timbre = complemento.find("tfd:TimbreFiscalDigital", ns)
            pagos = complemento.find("pago20:Pagos", ns)
            nomina = complemento.find("nomina12:Nomina", ns)
            if timbre is not None:
                uuid = timbre.attrib.get("UUID", "")
                tiene_timbre = True
            tiene_complemento_pago = pagos is not None
            tiene_nomina = nomina is not None

        conceptos = []
        for c in conceptos_nodes:
            conceptos.append(
                {
                    "clave_prod_serv": c.attrib.get("ClaveProdServ"),
                    "descripcion": c.attrib.get("Descripcion", ""),
                    "cantidad": Decimal(c.attrib.get("Cantidad", "0")),
                    "valor_unitario": Decimal(c.attrib.get("ValorUnitario", "0")),
                    "importe": Decimal(c.attrib.get("Importe", "0")),
                }
            )

        impuestos = []
        iva_trasladado = Decimal("0")
        iva_retenido = Decimal("0")
        if impuestos_global is not None:
            for traslado in impuestos_global.findall("cfdi:Traslados/cfdi:Traslado", ns):
                importe = Decimal(traslado.attrib.get("Importe", "0"))
                registro = {
                    "tipo": "traslado",
                    "impuesto": traslado.attrib.get("Impuesto", ""),
                    "tipo_factor": traslado.attrib.get("TipoFactor"),
                    "tasa_o_cuota": Decimal(traslado.attrib.get("TasaOCuota", "0")),
                    "base": Decimal(traslado.attrib.get("Base", root.attrib.get("SubTotal", "0"))),
                    "importe": importe,
                }
                impuestos.append(registro)
                if registro["impuesto"] == "002":
                    iva_trasladado += importe

            for retencion in impuestos_global.findall("cfdi:Retenciones/cfdi:Retencion", ns):
                importe = Decimal(retencion.attrib.get("Importe", "0"))
                registro = {
                    "tipo": "retencion",
                    "impuesto": retencion.attrib.get("Impuesto", ""),
                    "tipo_factor": retencion.attrib.get("TipoFactor"),
                    "tasa_o_cuota": Decimal(retencion.attrib.get("TasaOCuota", "0")),
                    "base": Decimal(retencion.attrib.get("Base", root.attrib.get("SubTotal", "0"))),
                    "importe": importe,
                }
                impuestos.append(registro)
                if registro["impuesto"] == "002":
                    iva_retenido += importe

        return CFDIParseResult(
            version=version,
            uuid=uuid,
            fecha_emision=root.attrib.get("Fecha", ""),
            tipo_comprobante=root.attrib.get("TipoDeComprobante", ""),
            rfc_emisor=emisor.attrib.get("Rfc", "") if emisor is not None else "",
            nombre_emisor=emisor.attrib.get("Nombre", "") if emisor is not None else "",
            rfc_receptor=receptor.attrib.get("Rfc", "") if receptor is not None else "",
            nombre_receptor=receptor.attrib.get("Nombre", "") if receptor is not None else "",
            subtotal=Decimal(root.attrib.get("SubTotal", "0")),
            iva_trasladado=iva_trasladado,
            iva_retenido=iva_retenido,
            total=Decimal(root.attrib.get("Total", "0")),
            moneda=root.attrib.get("Moneda", "MXN"),
            metodo_pago=root.attrib.get("MetodoPago"),
            forma_pago=root.attrib.get("FormaPago"),
            uso_cfdi=receptor.attrib.get("UsoCFDI") if receptor is not None else None,
            tiene_timbre=tiene_timbre,
            tiene_complemento_pago=tiene_complemento_pago,
            tiene_nomina=tiene_nomina,
            conceptos=conceptos,
            impuestos=impuestos,
        )
