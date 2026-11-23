"""
CAPA BRONCE: traer los datos de cada fuente y guardarlos TAL CUAL llegan.

Regla de bronce: no se limpia ni se corrige nada. Si algo viene mal,
se arregla en la capa plata. Asi siempre se puede volver al dato original.

Fuentes:
  1. XM (API REST, JSON): embalses, precio de bolsa y precio de contrato, por dia
  2. NOAA (archivo de texto por URL): el indice ONI de El Nino
  3. EnerAndes (Excel interno): las ventas de energia de 2023

Cada funcion recibe sus parametros (fechas, URL, archivo): asi las puede
llamar el pipeline con los valores de config.py, o la pagina "Cargar datos"
con lo que el usuario escriba. Si una API falla, se usa el respaldo de data/ejemplo/.
"""
# io: para leer un texto como si fuera un archivo
import io
# shutil: copiar archivos (el respaldo)
import shutil

# pandas: tablas en memoria
import pandas as pd

# La configuracion y las herramientas comunes
from src import config
from src.utils import guardar, log, pedir, ventanas


# Funcion: descarga las metricas de XM; los parametros en None toman el valor de config.py
def extraer_xm(metricas=None, inicio=None, fin=None) -> dict:
    """
    Fuente 1: las metricas de XM entre inicio y fin, en pedazos de 30 dias.
    metricas: lista de (codigo, entidad, nombre); por defecto, las de config.py.
    Devuelve {nombre_archivo: tabla} y guarda cada tabla en data/bronze/.
    """
    # 'x or y': si no llego valor (None o vacio), usa el de config.py
    metricas = metricas or config.XM_METRICAS
    inicio = inicio or config.FECHA_INICIO
    fin = fin or config.FECHA_FIN
    # La direccion completa de la API para datos diarios
    url = config.XM_URL.format(periodo="daily")
    # Aqui se van guardando las tablas: {nombre: tabla}
    resultado = {}
    # Una vuelta por cada metrica (embalses, precio bolsa, precio contrato)
    for metrica, entidad, nombre in metricas:
        # Lista de filas de esta metrica: un diccionario por dia
        filas = []
        # Una consulta por cada pedazo de maximo 30 dias
        for a, b in ventanas(inicio, fin, config.XM_MAX_DIAS):
            # El cuerpo de la peticion: que metrica y entre que fechas
            cuerpo = {"MetricId": metrica, "Entity": entidad,
                      "StartDate": str(a), "EndDate": str(b), "Filter": []}
            # POST a la API y la respuesta en JSON
            datos = pedir("POST", url, json=cuerpo).json()
            # XM responde: Items (uno por dia) -> DailyEntities -> Value
            for item in datos.get("Items", []):
                for entidad_dia in item["DailyEntities"]:
                    # Se guarda solo la fecha y el valor, tal cual llegan
                    filas.append({"Date": item["Date"], "Value": entidad_dia["Value"]})
        # Avisa cuantos dias llegaron de esta metrica
        log(f"   XM {metrica}: {len(filas)} dias")
        # Convierte la lista de filas en una tabla de pandas
        tabla = pd.DataFrame(filas)
        # La guarda en data/bronze/<nombre>.parquet
        guardar(tabla, config.DIR_BRONCE, nombre)
        # Y la agrega al resultado
        resultado[nombre] = tabla
    # Devuelve todas las tablas descargadas
    return resultado


# Funcion: descarga el indice ONI de NOAA
def extraer_noaa(url=None) -> pd.DataFrame:
    """Fuente 2: el ONI de NOAA desde una URL (un texto separado por espacios)."""
    # GET a la URL (o a la de config.py) y se toma la respuesta como texto
    texto = pedir("GET", url or config.NOAA_ONI_URL).text
    # sep=r"\s+": las columnas se separan por uno o mas espacios
    # dtype=str: en bronce todo se guarda como texto, sin convertir
    tabla = pd.read_csv(io.StringIO(texto), sep=r"\s+", dtype=str)
    # La guarda en data/bronze/noaa_oni.parquet
    guardar(tabla, config.DIR_BRONCE, "noaa_oni")
    return tabla


# Funcion: lee el Excel de ventas de EnerAndes
def extraer_enerandes(archivo=None) -> pd.DataFrame:
    """
    Fuente 3: el Excel de ventas, tal cual (con sus errores).
    archivo: una ruta o un archivo subido desde la pagina; por defecto, el de data/insumos/.
    """
    # dtype=str: todo como texto; asi no se pierde nada de lo que escribio la empresa
    # excel_activo(): el que subio el usuario, o el original si no ha subido ninguno
    tabla = pd.read_excel(archivo or config.excel_activo(), dtype=str)
    # La guarda en data/bronze/enerandes_ventas.parquet
    guardar(tabla, config.DIR_BRONCE, "enerandes_ventas")
    return tabla


# Las columnas que debe traer el Excel de ventas (la capa plata las necesita)
COLUMNAS_EXCEL = ["Fecha", "Municipio", "Segmento", "Tipo_Compra", "Energia_kWh", "Valor_COP", "Clientes"]


# Funcion: guarda el Excel que el usuario subio, para que TODO el proceso lo use
def guardar_excel_subido(archivo) -> pd.DataFrame:
    """
    Revisa que el Excel tenga las columnas de COLUMNAS_EXCEL y lo guarda como el Excel activo
    (data/insumos/ventas_enerandes_subido.xlsx). Si le faltan columnas, lanza un error que lo dice.
    """
    # Se lee para revisar las columnas (todo como texto)
    tabla = pd.read_excel(archivo, dtype=str)
    # Las columnas que el Excel NO trae
    faltan = [c for c in COLUMNAS_EXCEL if c not in tabla.columns]
    if faltan:
        raise ValueError(f"Al Excel le faltan estas columnas: {', '.join(faltan)}. "
                         f"Debe tener: {', '.join(COLUMNAS_EXCEL)}.")
    # getvalue(): el contenido del archivo subido, tal cual; se escribe en data/insumos/
    config.ENERANDES_SUBIDO.write_bytes(archivo.getvalue())
    log(f"   + insumos/{config.ENERANDES_SUBIDO.name}: Excel subido ({len(tabla):,} filas)")
    return tabla


# Funcion: deja de usar el Excel subido y vuelve al original
def volver_al_excel_original() -> None:
    # missing_ok=True: si no habia uno subido, no pasa nada
    config.ENERANDES_SUBIDO.unlink(missing_ok=True)


# Funcion: el plan B cuando no hay internet o la API falla
def usar_respaldo(nombres: list) -> None:
    """Copia los archivos de data/ejemplo/ a data/bronze/ cuando una API falla."""
    # Crea la carpeta de bronce si no existe
    config.DIR_BRONCE.mkdir(parents=True, exist_ok=True)
    # Por cada nombre, copia el archivo de ejemplo a bronce
    for nombre in nombres:
        shutil.copy(config.DIR_EJEMPLO / f"{nombre}.parquet", config.DIR_BRONCE / f"{nombre}.parquet")
        log(f"   + bronze/{nombre}.parquet: copiado del respaldo (data/ejemplo)")


# Funcion principal de la capa bronce
def main() -> None:
    """Las 3 fuentes con los valores de config.py (lo que usa el pipeline)."""
    log("CAPA BRONCE: traer los datos de las 3 fuentes")
    # try/except: si XM falla, se atrapa el error para usar el respaldo
    try:
        log("1. XM - API del mercado electrico")
        extraer_xm()
    except Exception as error:
        log(f"   ! XM no respondio ({error}). Se usa el respaldo.")
        # Copia los 3 archivos de XM desde data/ejemplo/
        usar_respaldo([nombre for _, _, nombre in config.XM_METRICAS])
    # Lo mismo con NOAA: si falla, se usa el respaldo
    try:
        log("2. NOAA - indice ONI de El Nino")
        extraer_noaa()
    except Exception as error:
        log(f"   ! NOAA no respondio ({error}). Se usa el respaldo.")
        usar_respaldo(["noaa_oni"])
    # El Excel esta en el disco: no necesita respaldo
    log("3. EnerAndes - Excel interno de ventas")
    extraer_enerandes()


# Si se ejecuta este archivo solo: python -m src.bronce.extraer
if __name__ == "__main__":
    main()
