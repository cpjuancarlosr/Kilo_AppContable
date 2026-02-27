"""
Configuración fiscal específica para México.

Incluye:
- Tasas de IVA (general y fronterizo)
- IEPS por tipo de producto
- Códigos postales de zonas fronterizas
- Regímenes fiscales SAT
- Periodicidad de declaraciones
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class RegimenFiscal(str, Enum):
    """Regímenes fiscales del SAT para personas morales."""

    GENERAL_LEY = "601"  # General de Ley Personas Morales
    PERSONAS_MORALES_FIDEICOMISOS = "603"
    SUELDOS_SALARIOS = "605"  # Personas físicas
    ARRENDAMIENTO = "606"  # Personas físicas
    ENAJENACION_ACCIONES = "607"
    DEMás_INGRESOS = "608"  # Personas físicas
    RESIDENTES_EXTRANJERO = "610"
    INGRESOS_DIVIDENDOS = "611"
    PERSONAS_FISICAS_EMPRESARIAL = "612"
    INGRESOS_INTERESES = "614"
    SIN_OBLIGACIONES_FISCALES = "616"
    INCORPORACION_FISCAL = "621"  # Régimen de Incorporación Fiscal
    ACTIVIDADES_AGRICOLAS = "622"
    OPCIONAL_GRUPOS_SOCIEDADES = "623"
    COORDINADOS = "624"
    HIDROCARBUROS = "628"
    ENAJENACION_BIENES = "607"
    PREFERENTES_EXTRANJEROS = "629"


class RegimenFiscalPersonaFisica(str, Enum):
    """Regímenes fiscales del SAT para personas físicas."""

    SUELDOS_SALARIOS = "605"
    ARRENDAMIENTO = "606"
    ACTIVIDAD_EMPRESARIAL = "612"
    PROFESIONAL = "612"
    INTERMEDIARIO = "612"
    RESIDENTES_EXTRANJERO = "610"


class UsoCFDI(str, Enum):
    """Usos CFDI catálogo del SAT."""

    ADQUISICION_MERCANCIAS = "G01"
    DEVOLUCIONES_DESCUENTOS = "G02"
    GASTOS_GENERALES = "G03"
    CONSTRUCCIONES = "I01"
    MOBILIARIO_EQUIPO = "I02"
    EQUIPO_COMPUTO = "I03"
    DADOS_TROQUELES = "I04"
    COMUNICACIONES_TELEFONICAS = "I05"
    COMUNICACIONES_SATELITALES = "I06"
    OTRA_MAQUINARIA = "I07"
    HONORARIOS_MEDICOS = "D01"
    GASTOS_MEDICOS = "D02"
    GASTOS_FUNERALES = "D03"
    DONATIVOS = "D04"
    INTERESES_REALES_HIPOTECARIOS = "D05"
    APORTACIONES_VOLUNTARIAS_SAR = "D06"
    PRIMAS_SEGUROS_GASTOS_MEDICOS = "D07"
    GASTOS_TRANSPORTACION_ESCOLAR = "D08"
    CUENTAS_AHORRO_PENSIONES = "D09"
    SERVICIOS_EDUCATIVOS = "D10"
    POR_DEFINIR = "P01"


class FormaPago(str, Enum):
    """Formas de pago catálogo del SAT."""

    EFECTIVO = "01"
    CHEQUE_NOMINATIVO = "02"
    TRANSFERENCIA_ELECTRONICA = "03"
    TARJETA_CREDITO = "04"
    MONEDERO_ELECTRONICO = "05"
    DINERO_ELECTRONICO = "06"
    VALES_DESPENSA = "08"
    DACION_PAGO = "12"
    SUBROGACION = "13"
    CONDONACION = "14"
    COMPENSACION = "17"
    NOVACION = "23"
    CONFUSION = "24"
    REMISION_DEUDA = "25"
    PRESCRIPCION_O_CADUCIDAD = "26"
    SATISFACCION_ACREEDOR = "27"
    TARJETA_DEBITO = "28"
    TARJETA_SERVICIOS = "29"
    APLICACION_ANTICIPOS = "30"
    POR_DEFINIR = "99"


class MetodoPago(str, Enum):
    """Métodos de pago catálogo del SAT."""

    PAGO_UNA_EXHIBICION = "PUE"
    PAGO_PARCIALIDADES = "PPD"


class TipoComprobante(str, Enum):
    """Tipos de comprobante CFDI."""

    INGRESO = "I"
    EGRESO = "E"
    TRASLADO = "T"
    NOMINA = "N"
    PAGO = "P"


# Zonas fronterizas de México (códigos postales)
# Fuente: SAT - Resolución Miscelánea Fiscal
ZONAS_FRONTERIZAS: List[str] = [
    # Baja California
    "21000",
    "21001",
    "21002",
    "21003",
    "21004",
    "21005",
    "21006",
    "21007",
    "21008",
    "21009",
    "21010",
    "21011",
    "21012",
    "21013",
    "21014",
    "21015",
    "21016",
    "21017",
    "21018",
    "21019",
    "21020",
    "21021",
    "21022",
    "21023",
    "21024",
    "21025",
    "21026",
    "21027",
    "21028",
    "21029",
    "21030",
    "21031",
    "21032",
    "21033",
    "21034",
    "21035",
    "21036",
    "21037",
    "21038",
    "21039",
    "21040",
    "21041",
    "21042",
    "21043",
    "21044",
    "21045",
    "21046",
    "21047",
    "21048",
    "21049",
    "21050",
    "21051",
    "21052",
    "21053",
    "21054",
    "21055",
    "21056",
    "21057",
    "21058",
    "21059",
    "21060",
    "21061",
    "21062",
    "21063",
    "21064",
    "21065",
    "21066",
    "21067",
    "21068",
    "21069",
    "21070",
    "21071",
    "21072",
    "21073",
    "21074",
    "21075",
    "21076",
    "21077",
    "21078",
    "21079",
    "21080",
    "21081",
    "21082",
    "21083",
    "21084",
    "21085",
    "21086",
    "21087",
    "21088",
    "21089",
    "21090",
    "21091",
    "21092",
    "21093",
    "21094",
    "21095",
    "21096",
    "21097",
    "21098",
    "21099",
    "21100",
    "21110",
    "21111",
    "21112",
    "21113",
    "21114",
    "21115",
    "21116",
    "21117",
    "21118",
    "21119",
    "21120",
    "21121",
    "21122",
    "21123",
    "21124",
    "21125",
    "21126",
    "21127",
    "21128",
    "21129",
    "21130",
    "21200",
    "21210",
    "21220",
    "21230",
    "21240",
    "21250",
    "21260",
    "21270",
    "21280",
    "21290",
    "21300",
    "21310",
    "21320",
    "21330",
    "21340",
    "21350",
    "21360",
    "21370",
    "21380",
    "21390",
    "21400",
    "21410",
    "21420",
    "21430",
    "21440",
    "21450",
    "21460",
    "21470",
    "21480",
    "21490",
    "21500",
    "21505",
    "21507",
    "21510",
    "21520",
    "21530",
    "21540",
    "21550",
    "21560",
    "21570",
    "21580",
    "21590",
    "21600",
    "21610",
    "21620",
    "21630",
    "21640",
    "21650",
    "21660",
    "21670",
    "21680",
    "21690",
    "21700",
    "21710",
    "21720",
    "21730",
    "21740",
    "21750",
    "21760",
    "21770",
    "21780",
    "21790",
    "21800",
    "21810",
    "21820",
    "21830",
    "21840",
    "21850",
    "21860",
    "21870",
    "21880",
    "21890",
    "21900",
    "21910",
    "21920",
    "21930",
    "21940",
    "21950",
    "21960",
    "21970",
    # Sonora (parcial)
    "83000",
    "83010",
    "83015",
    "83040",
    "83100",
    "83105",
    "83106",
    "83107",
    "83108",
    "83109",
    "83110",
    "83115",
    "83116",
    "83117",
    "83118",
    "83119",
    "83120",
    "83125",
    "83126",
    "83127",
    "83128",
    "83129",
    "83130",
    "83135",
    "83136",
    "83137",
    "83138",
    "83139",
    "83140",
    "83145",
    "83146",
    "83147",
    "83148",
    "83149",
    "83150",
    "83155",
    "83156",
    "83157",
    "83158",
    "83159",
    "83160",
    "83165",
    "83166",
    "83167",
    "83168",
    "83169",
    "83170",
    "83175",
    "83176",
    "83177",
    "83178",
    "83179",
    "83180",
    "83185",
    "83186",
    "83187",
    "83188",
    "83189",
    "83190",
    "83195",
    "83196",
    "83197",
    "83198",
    "83199",
    "83200",
    "83240",
    "83260",
    "83280",
    "83290",
    "83300",
    "83303",
    "83304",
    "83305",
    "83306",
    "83307",
    "83308",
    "83309",
    "83310",
    "83313",
    "83314",
    "83315",
    "83316",
    "83317",
    "83318",
    "83319",
    "83320",
    "83323",
    "83324",
    "83325",
    "83326",
    "83327",
    "83328",
    "83329",
    "83330",
    "83333",
    "83334",
    "83335",
    "83336",
    "83337",
    "83338",
    "83339",
    "83340",
    "83343",
    "83344",
    "83345",
    "83346",
    "83347",
    "83348",
    "83349",
    "83350",
    "83353",
    "83354",
    "83355",
    "83356",
    "83357",
    "83358",
    "83359",
]

# Tasas de IEPS por tipo de producto
# Fuente: Ley del IEPS Artículo 2-A
IEPS_TASAS: Dict[str, Dict[str, float]] = {
    "gasolina_magna": {"tasa": 0.0, "cuota_especifica": 0.0},  # Variable mensual
    "gasolina_premium": {"tasa": 0.0, "cuota_especifica": 0.0},
    "diesel": {"tasa": 0.0, "cuota_especifica": 0.0},
    "cerveza": {"tasa": 0.50, "cuota_especifica": 0.0},
    "bebidas_alcoholicas": {"tasa": 0.50, "cuota_especifica": 0.0},
    "tabaco": {"tasa": 1.60, "cuota_especifica": 0.0},
    "bebidas_saborizadas": {"tasa": 0.0, "cuota_especifica": 1.5737},  # Por litro
    "alimentos_calorias": {"tasa": 0.08, "cuota_especifica": 0.0},
}


@dataclass
class PeriodicidadFiscal:
    """Periodicidad de obligaciones fiscales en México."""

    nombre: str
    dias: int
    meses: float


PERIODICIDAD_DECLARACIONES = {
    "mensual": PeriodicidadFiscal("Mensual", 30, 1),
    "bimestral": PeriodicidadFiscal("Bimestral", 60, 2),
    "trimestral": PeriodicidadFiscal("Trimestral", 90, 3),
    "cuatrimestral": PeriodicidadFiscal("Cuatrimestral", 120, 4),
    "semestral": PeriodicidadFiscal("Semestral", 180, 6),
    "anual": PeriodicidadFiscal("Anual", 365, 12),
}


# Días de declaración SAT
DIAS_DECLARACION = {
    "ISR_personas_morales": 17,  # Días del mes siguiente
    "IVA": 17,  # Días del mes siguiente
    "DIOT": 17,  # Días del mes siguiente
    "IEPS": 17,  # Días del mes siguiente
    "ISR_retenido": 17,  # Días del mes siguiente
}


def es_zona_fronteriza(codigo_postal: str) -> bool:
    """
    Determina si un código postal pertenece a zona fronteriza.

    En zonas fronterizas aplica IVA del 8% en lugar del 16%.
    """
    cp_limpio = codigo_postal.zfill(5)
    return cp_limpio in ZONAS_FRONTERIZAS


def obtener_tasa_iva(codigo_postal: str) -> float:
    """
    Obtiene la tasa de IVA aplicable según el código postal.

    Args:
        codigo_postal: Código postal de 5 dígitos

    Returns:
        Tasa de IVA (0.08 o 0.16)
    """
    if es_zona_fronteriza(codigo_postal):
        return 0.08
    return 0.16


def calcular_ieps(tipo_producto: str, cantidad: float, valor: float) -> float:
    """
    Calcula el IEPS para un producto específico.

    Args:
        tipo_producto: Clave del tipo de producto
        cantidad: Cantidad en unidades (litros, piezas, etc.)
        valor: Valor del producto

    Returns:
        Monto de IEPS calculado
    """
    if tipo_producto not in IEPS_TASAS:
        return 0.0

    config = IEPS_TASAS[tipo_producto]

    # IEPS por cuota específica (por unidad)
    if config["cuota_especifica"] > 0:
        return cantidad * config["cuota_especifica"]

    # IEPS por tasa ad valorem
    return valor * config["tasa"]


# Reglas de deducibilidad SAT (máximos permitidos)
DEDUCIBILIDAD_LIMITES = {
    "honorarios_administradores": 0.0,  # No deducible
    "gastos_representacion": 0.0,  # No deducible desde 2018
    "primas_seguro_vida": 0.0,  # No deducible
    "donativos": 0.07,  # 7% de utilidad fiscal del ejercicio anterior
    "aportaciones_retiro": 0.125,  # 12.5% de ingresos de personal
    "cuotas_sindicales": 1.0,  # Deducible
    "gastos_viaje_nacional": 1.0,  # Deducible con comprobante
    "gastos_viaje_extranjero": 1.0,  # Deducible con comprobante
}


@dataclass
class InformacionFiscalMX:
    """Información fiscal completa para una empresa en México."""

    rfc: str
    razon_social: str
    regimen_fiscal: RegimenFiscal
    codigo_postal: str
    actividad_economica: str  # Código SCIAN
    es_zona_fronteriza: bool = False

    def __post_init__(self):
        self.es_zona_fronteriza = es_zona_fronteriza(self.codigo_postal)

    @property
    def tasa_iva_aplicable(self) -> float:
        """Retorna la tasa de IVA según ubicación."""
        return 0.08 if self.es_zona_fronteriza else 0.16
