"""
Herramientas comunes a todas las capas: mensajes, peticiones HTTP con reintentos
y guardar en Parquet.
"""
# time: para esperar entre reintentos
import time
# datetime: la hora de los mensajes; timedelta: sumar dias
from datetime import datetime, timedelta

# pandas: tablas en memoria
import pandas as pd
# requests: hacer peticiones a las APIs por internet
import requests

# La configuracion del proyecto
from src import config


# Funcion: imprime un mensaje en la terminal con la hora adelante
def log(mensaje: str) -> None:
    """Escribe un mensaje con la hora: [10:15:02] mensaje."""
    # flush=True: que salga de inmediato (importante dentro de Docker)
    print(f"[{datetime.now():%H:%M:%S}] {mensaje}", flush=True)


# Funcion: pide algo a una URL (GET o POST) y reintenta si falla
# **kwargs: recibe cualquier otro parametro (por ejemplo json=...) y se lo pasa a requests
def pedir(metodo: str, url: str, **kwargs) -> requests.Response:
    """Hace una peticion HTTP. Si falla, espera y lo intenta otra vez."""
    # Repite el intento 1, 2, 3 (HTTP_REINTENTOS veces)
    for intento in range(1, config.HTTP_REINTENTOS + 1):
        # try/except: si la peticion falla, se atrapa el error para reintentar
        try:
            # La peticion, con un tiempo maximo de espera
            respuesta = requests.request(metodo, url, timeout=config.HTTP_TIMEOUT, **kwargs)
            # Si el servidor respondio con error (404, 500...), se trata como falla
            respuesta.raise_for_status()
            # Si llego aqui, todo salio bien: devuelve la respuesta
            return respuesta
        except requests.RequestException as error:
            # Si fue el ultimo intento, se rinde y avisa
            if intento == config.HTTP_REINTENTOS:
                raise RuntimeError(f"No respondio {url}: {error}") from error
            # Si no, espera 2, 4, 8... segundos y vuelve a intentar
            log(f"   ! intento {intento} fallo; reintento en {2 ** intento} s")
            # sleep: pausa el programa esos segundos
            time.sleep(2 ** intento)


# Funcion generadora: entrega los pedazos de fechas uno por uno (con yield)
def ventanas(inicio, fin, dias: int):
    """Parte el rango de fechas en pedazos de 'dias' dias (XM pide maximo 30)."""
    # 'a' es el comienzo del pedazo actual
    a = inicio
    # Mientras el comienzo no pase del fin, se arma otro pedazo
    while a <= fin:
        # El final del pedazo: 'dias' dias despues, sin pasarse del fin
        b = min(a + timedelta(days=dias - 1), fin)
        # yield: entrega el pedazo (a, b) y sigue desde aqui en la siguiente vuelta
        yield a, b
        # El siguiente pedazo empieza el dia despues
        a = b + timedelta(days=1)


# Funcion: guarda una tabla de pandas como archivo Parquet
def guardar(df: pd.DataFrame, carpeta, nombre: str) -> None:
    """Guarda una tabla en carpeta/nombre.parquet y dice cuantas filas tiene."""
    # Crea la carpeta si no existe
    carpeta.mkdir(parents=True, exist_ok=True)
    # index=False: no guarda la columna de numeros de fila de pandas
    df.to_parquet(carpeta / f"{nombre}.parquet", index=False)
    # Avisa en la terminal que archivo guardo y cuantas filas tiene
    log(f"   + {carpeta.name}/{nombre}.parquet: {len(df):,} filas")
