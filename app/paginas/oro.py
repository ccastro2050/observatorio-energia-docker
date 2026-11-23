"""
Pagina 3 · MODELO ORO (dbt).
Con un boton: dbt build (modelos + pruebas) y la exportacion a Parquet.
Muestra el modelo estrella y lo que escribe dbt.
"""
# streamlit: los controles de la pagina
import streamlit as st

# La configuracion y la capa oro
from src import config
from src.oro.construir import dbt_build, exportar

# El titulo grande de la pagina
st.title("🏅 3 · Modelo oro: dbt")
# Un parrafo que explica que hace dbt
st.write("**dbt** lee bronce y plata, arma el **modelo estrella** dentro de la base "
         "`data/observatorio.duckdb` y **prueba** la calidad. Luego las tablas se copian a "
         "archivos `.parquet` en `data/gold/`, que es lo que lee el dashboard.")

# El modelo estrella, dibujado con texto
# st.code: muestra el texto en un recuadro de letra fija (language=None: sin colores)
st.code("""
            dim_mes (mes_id)                 dim_municipio (municipio_id)
                   \\                              /
                    \\                            /
                     fact_ventas  ── una venta: mes, municipio, segmento, Bolsa/Contrato, kWh, $
                          │  mes_id
                     fact_mercado ── un mes: embalses, precio bolsa, precio contrato, ONI, fase
""", language=None)

# Lo que necesita dbt: que existan los archivos de bronce y plata
# Lista de los archivos de bronce que NO existen todavia
faltan = [n for n in ("xm_embalses", "xm_precio_bolsa", "xm_precio_contrato", "noaa_oni")
          if not (config.DIR_BRONCE / f"{n}.parquet").exists()]
# Si falta el archivo de plata, tambien se agrega a la lista
if not (config.DIR_PLATA / "enerandes_ventas.parquet").exists():
    faltan.append("silver/enerandes_ventas")
# Si falta alguno: se avisa cuales y se detiene la pagina
if faltan:
    st.warning(f"Faltan archivos: {', '.join(faltan)}. Completen las páginas 1 y 2.")
    st.stop()

# Al hacer clic: se ejecuta dbt y luego se exporta a Parquet
if st.button("Ejecutar dbt build y exportar", type="primary"):
    # st.spinner: circulo girando mientras dbt trabaja
    with st.spinner("dbt está creando las tablas y corriendo las pruebas..."):
        # bien = True si todo paso; texto = lo que escribio dbt
        bien, texto = dbt_build()
    # La ultima linea de dbt dice cuantos pasaron: "Done. PASS=17 WARN=0 ERROR=0..."
    resumen = [linea for linea in texto.splitlines() if "PASS=" in linea]
    # Si dbt termino bien...
    if bien:
        # Mensaje verde con el resumen (lo que va despues de 'Done. ')
        st.success(f"✅ {resumen[-1].split('Done. ')[-1] if resumen else 'dbt terminó bien'}")
        # Copia las tablas de DuckDB a data/gold/ y devuelve cuantas filas tiene cada una
        filas = exportar()
        st.write("**Tablas exportadas a `data/gold/`:**")
        # Una tabla con el nombre de cada tabla exportada y sus filas
        st.dataframe([{"tabla": t, "filas": n} for t, n in filas.items()], hide_index=True)
    # Si dbt fallo: mensaje rojo y no se exporta
    else:
        st.error("❌ dbt falló: una prueba no pasó o un modelo tiene un error. No se exportó nada.")
    # Lo que escribio dbt, para leerlo con calma
    # st.expander: una seccion que se abre y se cierra con un clic
    with st.expander("Ver lo que escribió dbt"):
        st.code(texto, language=None)

# Una linea horizontal para separar
st.divider()
# Recuadro azul que dice cual es la siguiente pagina
st.info("**Siguiente paso:** 📊 *4 · Dashboard*.")
