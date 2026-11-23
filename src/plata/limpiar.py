"""
CAPA PLATA: limpiar las ventas de EnerAndes.

El Excel de la empresa trae errores tipicos: municipios escritos de varias
formas ('Medellin', 'MEDELLIN', 'Medellin D.E.'), segmentos abreviados ('IND'),
energia negativa, filas vacias, filas repetidas y una fila TOTAL al final.
Aqui se corrigen con REGLAS, y lo que no se puede corregir se descarta.

Los datos de XM y NOAA no pasan por aqui: los ordena dbt en la capa oro.
"""
# unicodedata: para quitar las tildes
import unicodedata

# pandas: tablas en memoria
import pandas as pd

# La configuracion y las herramientas comunes
from src import config
from src.utils import guardar, log

# Municipio (sin tildes y en minuscula) -> (codigo DIVIPOLA, nombre oficial)
MUNICIPIOS = {
    "medellin": ("05001", "Medellín"), "santa fe de antioquia": ("05042", "Santa Fe de Antioquia"),
    "apartado": ("05045", "Apartadó"), "bello": ("05088", "Bello"), "caldas": ("05129", "Caldas"),
    "caucasia": ("05154", "Caucasia"), "copacabana": ("05212", "Copacabana"),
    "envigado": ("05266", "Envigado"), "girardota": ("05308", "Girardota"),
    "itagui": ("05360", "Itagüí"), "la estrella": ("05380", "La Estrella"),
    "marinilla": ("05440", "Marinilla"), "rionegro": ("05615", "Rionegro"),
    "sabaneta": ("05631", "Sabaneta"), "turbo": ("05837", "Turbo"),
}
# Otras formas de escribir el mismo municipio -> la forma de la lista de arriba
ALIAS = {"rio negro": "rionegro", "rionegro (ant)": "rionegro", "medellin d.e.": "medellin",
         "sta fe de antioquia": "santa fe de antioquia", "santafe de antioquia": "santa fe de antioquia"}
# Formas de escribir el segmento y el tipo de compra -> valor estandar
SEGMENTOS = {"residencial": "Residencial", "resid.": "Residencial", "comercial": "Comercial",
             "industrial": "Industrial", "ind": "Industrial"}
TIPOS = {"bolsa": "Bolsa", "contrato": "Contrato", "contratos": "Contrato"}


# Funcion: deja un texto en una forma comun para poder compararlo
def normalizar(texto) -> str:
    """'  Medellín ' -> 'medellin': sin espacios a los lados, minuscula y sin tildes."""
    # Si la celda esta vacia (NaN o None), devuelve texto vacio
    if pd.isna(texto):
        return ""
    # NFKD separa la letra de la tilde; luego se quitan las tildes (combining)
    sin_tildes = "".join(c for c in unicodedata.normalize("NFKD", str(texto))
                         if not unicodedata.combining(c))
    # strip quita los espacios de los lados; lower lo pasa a minuscula
    return sin_tildes.strip().lower()


# Funcion: recibe la tabla de bronce y devuelve la tabla limpia
def limpiar(bronce: pd.DataFrame) -> pd.DataFrame:
    """Aplica las reglas de limpieza y devuelve las ventas limpias."""
    # copy(): trabaja sobre una copia para no cambiar la tabla original
    df = bronce.copy()
    # Regla 1: nombres de columna estandar (minuscula, sin espacios)
    df = df.rename(columns={"Fecha": "periodo", "Municipio": "municipio", "Segmento": "segmento",
                            "Tipo_Compra": "tipo_compra", "Energia_kWh": "energia_kwh",
                            "Valor_COP": "valor_cop", "Clientes": "clientes"})
    # Regla 2: quitar la fila TOTAL del final (no es una venta)
    df = df[df["periodo"] != "TOTAL"]
    # Regla 3: municipio -> codigo DIVIPOLA y nombre oficial
    # Normaliza el texto y cambia los alias por la forma oficial
    clave = df["municipio"].map(normalizar).replace(ALIAS)
    # Busca la clave en MUNICIPIOS: [0] es el codigo; si no la encuentra, queda vacio (None)
    df["municipio_id"] = clave.map(lambda c: MUNICIPIOS.get(c, (None, None))[0])
    # [1] es el nombre oficial
    df["municipio"] = clave.map(lambda c: MUNICIPIOS.get(c, (None, None))[1])
    # Regla 4: segmento y tipo de compra estandar
    # map(SEGMENTOS): cambia cada forma por el valor estandar; lo desconocido queda vacio
    df["segmento"] = df["segmento"].map(normalizar).map(SEGMENTOS)
    df["tipo_compra"] = df["tipo_compra"].map(normalizar).map(TIPOS)
    # Regla 5: texto -> numero (si no se puede, queda vacio)
    for columna in ("energia_kwh", "valor_cop", "clientes"):
        # errors="coerce": lo que no es numero queda vacio (NaN) en vez de dar error
        df[columna] = pd.to_numeric(df[columna], errors="coerce")
    # Regla 6: descartar filas incompletas y con energia negativa o cero
    # dropna: borra las filas que tienen vacia alguna de estas columnas
    df = df.dropna(subset=["municipio_id", "segmento", "tipo_compra", "energia_kwh", "valor_cop"])
    # Deja solo las filas con energia mayor que cero
    df = df[df["energia_kwh"] > 0]
    # Regla 7: descartar filas repetidas
    df = df.drop_duplicates()
    # El orden final de las columnas
    # reset_index(drop=True): vuelve a numerar las filas desde 0
    return df[["periodo", "municipio_id", "municipio", "segmento", "tipo_compra",
               "energia_kwh", "valor_cop", "clientes"]].reset_index(drop=True)


# Funcion principal de la capa plata
def main() -> tuple:
    """Lee bronce, limpia y guarda en plata. Devuelve (bronce, plata) para mostrarlos."""
    log("CAPA PLATA: limpiar las ventas de EnerAndes")
    # Lee las ventas tal cual quedaron en bronce
    bronce = pd.read_parquet(config.DIR_BRONCE / "enerandes_ventas.parquet")
    # Aplica las 7 reglas
    plata = limpiar(bronce)
    # Avisa cuantas filas entraron, cuantas quedaron y cuantas se descartaron
    log(f"   {len(bronce):,} filas en bronce -> {len(plata):,} filas limpias "
        f"({len(bronce) - len(plata)} descartadas)")
    # Guarda la tabla limpia en data/silver/enerandes_ventas.parquet
    guardar(plata, config.DIR_PLATA, "enerandes_ventas")
    # Devuelve las dos tablas (la pagina 2 las usa para comparar)
    return bronce, plata


# Si se ejecuta este archivo solo: python -m src.plata.limpiar
if __name__ == "__main__":
    main()
