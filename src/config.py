"""
Configuracion central: todo lo que puede cambiar vive AQUI.
Fechas, direcciones de las fuentes y carpetas de cada capa.
"""
# date: para escribir fechas (ano, mes, dia)
from datetime import date
# Path: rutas de archivos que funcionan en Windows, Mac y Linux
from pathlib import Path

# --- El periodo que se analiza ---------------------------------------------
# El ano de las ventas de EnerAndes: 2023 (el ano en que empezo El Nino 2023-2024)
# Primer dia del periodo: 1 de enero de 2023
FECHA_INICIO = date(2023, 1, 1)
# Ultimo dia del periodo: 31 de diciembre de 2023
FECHA_FIN = date(2023, 12, 31)

# --- Las carpetas de cada capa -----------------------------------------------
# RAIZ: la carpeta del proyecto (dos niveles arriba de este archivo)
RAIZ = Path(__file__).resolve().parent.parent
# Insumos: los archivos que entrega la empresa (el Excel de ventas)
DIR_INSUMOS = RAIZ / "data" / "insumos"
# Ejemplo: copia de respaldo de la capa bronce, por si una API falla en clase
DIR_EJEMPLO = RAIZ / "data" / "ejemplo"
# BRONCE: los datos tal cual llegan de cada fuente
DIR_BRONCE = RAIZ / "data" / "bronze"
# PLATA: los datos limpios
DIR_PLATA = RAIZ / "data" / "silver"
# ORO: las tablas listas para el dashboard
DIR_ORO = RAIZ / "data" / "gold"
# La base DuckDB donde dbt construye la capa oro
BASE_DUCKDB = RAIZ / "data" / "observatorio.duckdb"

# --- Fuente 1: API de XM (el mercado electrico de Colombia) ------------------
# La direccion de la API: {periodo} se cambia por daily (datos por dia)
XM_URL = "https://servapibi.xm.com.co/{periodo}"
# XM no acepta pedir mas de 30 dias en una sola consulta
XM_MAX_DIAS = 30
# Las metricas que se piden: (codigo en XM, entidad, nombre del archivo en bronce)
XM_METRICAS = [
    ("PorcVoluUtilDiar", "Sistema", "xm_embalses"),          # % de agua en los embalses
    ("PPPrecBolsNaci", "Sistema", "xm_precio_bolsa"),        # precio de bolsa del dia (COP/kWh)
    ("PrecPromCont", "Sistema", "xm_precio_contrato"),       # precio de los contratos (COP/kWh)
]

# --- Fuente 2: NOAA (el indice de El Nino) -----------------------------------
# La direccion del archivo de texto con el indice ONI, mes a mes
NOAA_ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"

# --- Fuente 3: EnerAndes (el Excel interno de ventas) ------------------------
# La ruta del Excel de ventas, dentro de la carpeta de insumos
ENERANDES_EXCEL = DIR_INSUMOS / "ventas_enerandes_2023.xlsx"

# --- Como se pide a las APIs -------------------------------------------------
HTTP_TIMEOUT = 60       # segundos maximos de espera por respuesta
HTTP_REINTENTOS = 3     # intentos antes de rendirse
