"""
El PIPELINE completo: las tres capas, en orden.

    python -m src.pipeline

  BRONCE  ->  traer los datos de XM, NOAA y EnerAndes, tal cual
  PLATA   ->  limpiar las ventas
  ORO     ->  dbt arma el modelo estrella, lo prueba y se exporta a Parquet

En Docker lo ejecuta el contenedor 'pipeline' (docker-compose.yml).
"""
# time: para medir cuanto tarda
import time

# Las tres capas
from src.bronce import extraer
from src.oro import construir
from src.plata import limpiar
# log: imprime mensajes con la hora
from src.utils import log


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
