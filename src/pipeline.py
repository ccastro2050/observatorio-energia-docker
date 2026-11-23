"""
El PIPELINE completo: las tres capas, en orden.

    python -m src.pipeline

  BRONCE  ->  traer los datos de XM, NOAA y EnerAndes, tal cual
  PLATA   ->  limpiar las ventas
  ORO     ->  dbt arma el modelo estrella, lo prueba y se exporta a Parquet

En Docker lo ejecuta el contenedor 'pipeline' (docker-compose.yml).
"""
# shutil: borrar carpetas completas (para empezar de cero)
import shutil
# time: para medir cuanto tarda
import time

# La configuracion: donde esta cada capa
from src import config
# Las tres capas
from src.bronce import extraer
from src.oro import construir
from src.plata import limpiar
# log: imprime mensajes con la hora
from src.utils import log


# Funcion: borra todo lo que genera el proceso, para empezar como recien clonado
def empezar_de_cero() -> None:
    """Borra bronce, plata, oro y la base DuckDB. NO borra insumos ni el respaldo (ejemplo)."""
    # Las tres carpetas de las capas
    for carpeta in (config.DIR_BRONCE, config.DIR_PLATA, config.DIR_ORO):
        # ignore_errors=True: si la carpeta no existe, no pasa nada
        shutil.rmtree(carpeta, ignore_errors=True)
    # La base DuckDB y su archivo temporal (.wal), si existen
    for archivo in (config.BASE_DUCKDB, config.BASE_DUCKDB.with_suffix(".duckdb.wal")):
        # missing_ok=True: si no existe, no pasa nada
        archivo.unlink(missing_ok=True)
    log("Se borraron bronce, plata, oro y la base: todo empieza de cero")


# Funcion principal: corre las tres capas una detras de otra
def main() -> None:
    # Guarda la hora de inicio (en segundos) para medir cuanto tarda
    inicio = time.time()
    log("=== PIPELINE: bronce -> plata -> oro ===")
    extraer.main()      # 1. BRONCE
    limpiar.main()      # 2. PLATA
    construir.main()    # 3. ORO
    # Hora actual menos hora de inicio = segundos que tardo
    log(f"=== Listo en {time.time() - inicio:.0f} s. El dashboard ya puede leer data/gold/ ===")


# Si se ejecuta este archivo solo (python -m src.pipeline), corre main()
if __name__ == "__main__":
    main()
