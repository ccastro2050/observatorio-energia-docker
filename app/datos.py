"""
Los DATOS y los CALCULOS del dashboard (la "cocina").

Lee las tablas de la capa oro (data/gold/*.parquet) y hace los calculos.
No tiene nada de Streamlit: asi se puede probar con pytest (tests/).
"""
# Path: rutas que funcionan en Windows, Mac y Linux
from pathlib import Path

# pandas: tablas en memoria
import pandas as pd

# La carpeta de la capa oro: subir de app/ a la raiz y entrar a data/gold
CARPETA_ORO = Path(__file__).resolve().parent.parent / "data" / "gold"


# Funcion: recibe el nombre de una tabla y devuelve un DataFrame (tabla de pandas)
def cargar(tabla: str) -> pd.DataFrame:
    """Lee una tabla de la capa oro por su nombre: cargar('fact_mercado')."""
    # Lee el archivo data/gold/<tabla>.parquet
    df = pd.read_parquet(CARPETA_ORO / f"{tabla}.parquet")
    # El mes llega como fecha simple: se pasa a fecha de pandas para graficar
    if "mes" in df.columns:
        df["mes"] = pd.to_datetime(df["mes"])
    # Devuelve la tabla lista
    return df


# Funcion: une las ventas con los municipios para tener el nombre de cada uno
def ventas_con_nombres() -> pd.DataFrame:
    """Las ventas con el nombre del municipio: une el hecho con su dimension (JOIN)."""
    # merge: junta las dos tablas por la columna comun municipio_id
    return cargar("fact_ventas").merge(cargar("dim_municipio"), on="municipio_id")


# Funcion: calcula cuanto cuesta cada venta en bolsa y por contrato
def costos_de_compra(ventas: pd.DataFrame, mercado: pd.DataFrame) -> pd.DataFrame:
    """
    Cuanto cuesta la energia de cada venta si se compra en BOLSA o por CONTRATO,
    con los precios reales de XM del mismo mes. Agrega 3 columnas, en pesos.
    """
    # A cada venta le trae los dos precios de su mes (la llave es mes_id)
    # how="left": conserva todas las ventas, aunque su mes no tenga precio
    df = ventas.merge(mercado[["mes_id", "precio_bolsa_cop_kwh", "precio_contrato_cop_kwh"]],
                      on="mes_id", how="left")
    # kWh x COP/kWh = COP
    df["costo_bolsa"] = df["energia_kwh"] * df["precio_bolsa_cop_kwh"]
    df["costo_contrato"] = df["energia_kwh"] * df["precio_contrato_cop_kwh"]
    # Positivo = la bolsa habria salido mas cara que el contrato
    df["sobrecosto"] = df["costo_bolsa"] - df["costo_contrato"]
    # Devuelve las ventas con las 3 columnas nuevas
    return df


# Funcion: el precio promedio de bolsa en cada fase de El Nino
def precio_por_fase(mercado: pd.DataFrame) -> pd.DataFrame:
    """El precio de bolsa promedio en cada fase ENSO (El Nino, Neutral, La Nina)."""
    # groupby: junta los meses de cada fase y saca el promedio del precio
    # mean(): el promedio; round(0): sin decimales
    return (mercado.groupby("fase_enso", as_index=False)["precio_bolsa_cop_kwh"]
            .mean().round(0))
