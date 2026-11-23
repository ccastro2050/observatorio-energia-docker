"""
CAPA ORO: construir el modelo estrella con dbt y exportarlo a Parquet.

  1. dbt build: crea las vistas staging y las tablas de hechos y dimensiones
     dentro de la base data/observatorio.duckdb, y corre las pruebas de calidad.
  2. Exportar: copia cada tabla de la base DuckDB a data/gold/<tabla>.parquet.
     El dashboard (y Power BI) leen esos archivos, sin abrir la base.
"""
# subprocess: ejecutar un comando de la terminal (dbt) desde Python
import subprocess

# duckdb: la base de datos donde dbt deja la capa oro
import duckdb

# La configuracion y las herramientas comunes
from src import config
from src.utils import log

# Las tablas de la capa oro (los modelos de dbt/models/marts)
TABLAS_ORO = ["dim_mes", "dim_municipio", "fact_ventas", "fact_mercado"]


# Funcion: corre dbt build como si se escribiera en la terminal
def dbt_build() -> tuple:
    """
    Ejecuta dbt build: modelos + pruebas.
    Devuelve (bien, texto): bien=True si todo paso; texto = lo que escribio dbt.
    """
    log("   dbt build (modelos y pruebas)...")
    # capture_output: guarda lo que escribe dbt, para mostrarlo en la pagina o en la terminal
    # subprocess.run ejecuta: dbt build --no-use-colors --project-dir dbt --profiles-dir dbt
    # cwd=config.RAIZ: lo ejecuta parado en la carpeta del proyecto; text=True: salida como texto
    proceso = subprocess.run(["dbt", "build", "--no-use-colors", "--project-dir", "dbt",
                              "--profiles-dir", "dbt"],
                             cwd=config.RAIZ, capture_output=True, text=True)
    # Muestra en la terminal lo que escribio dbt
    print(proceso.stdout, flush=True)
    # returncode 0 = sin errores
    return proceso.returncode == 0, proceso.stdout


# Funcion: pasa las tablas de DuckDB a archivos Parquet
def exportar() -> dict:
    """Copia cada tabla de la base DuckDB a un archivo .parquet en data/gold/. Devuelve {tabla: filas}."""
    # Crea la carpeta data/gold/ si no existe
    config.DIR_ORO.mkdir(parents=True, exist_ok=True)
    # read_only=True: solo se lee; exportar no cambia nada en la base
    con = duckdb.connect(str(config.BASE_DUCKDB), read_only=True)
    # Aqui se guarda cuantas filas tiene cada tabla
    filas = {}
    # Una vuelta por cada tabla de la capa oro
    for tabla in TABLAS_ORO:
        # La ruta del archivo de salida: data/gold/<tabla>.parquet
        archivo = config.DIR_ORO / f"{tabla}.parquet"
        # COPY: la instruccion de DuckDB que copia una tabla a un archivo
        con.execute(f"COPY {tabla} TO '{archivo.as_posix()}' (FORMAT parquet)")
        # Cuenta las filas de la tabla; fetchone()[0] saca el numero del resultado
        filas[tabla] = con.execute(f"SELECT count(*) FROM {tabla}").fetchone()[0]
        log(f"   + gold/{tabla}.parquet: {filas[tabla]:,} filas")
    # Cierra la conexion con la base
    con.close()
    # Devuelve {tabla: filas}
    return filas


# Funcion principal de la capa oro
def main() -> None:
    log("CAPA ORO: modelo estrella con dbt")
    # Corre dbt; el '_' ignora el texto porque aqui no se necesita
    bien, _ = dbt_build()
    # Si una prueba fallo, se detiene: no se exportan datos malos
    if not bien:
        raise SystemExit("dbt build fallo: revise el mensaje de arriba")
    # Si todo paso, copia las tablas a data/gold/
    exportar()


# Si se ejecuta este archivo solo: python -m src.oro.construir
if __name__ == "__main__":
    main()
