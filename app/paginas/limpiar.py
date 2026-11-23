"""
Pagina 2 · LIMPIAR (capa PLATA).
Muestra las reglas, las aplica con un boton y compara el antes y el despues.
"""
# pandas: tablas en memoria
import pandas as pd
# streamlit: los controles de la pagina
import streamlit as st

# La configuracion y la limpieza de la capa plata
from src import config
from src.plata import limpiar

# El titulo grande de la pagina
st.title("🧹 2 · Limpiar: capa plata")
# Un parrafo que explica la pagina
st.write("Las ventas de EnerAndes llegan con errores. Aquí se corrigen con **reglas** y se "
         "guardan en `data/silver/`. XM y NOAA no pasan por aquí: los ordena dbt.")

# Las reglas, en una tabla para leer
# pd.DataFrame arma la tabla con dos columnas; hide_index=True oculta los numeros de fila
st.dataframe(pd.DataFrame({
    "Regla": [1, 2, 3, 4, 5, 6, 7],
    "Qué hace": ["Nombres de columna estándar", "Quitar la fila TOTAL",
                 "Municipio → código DIVIPOLA y nombre oficial ('MEDELLIN', 'Medellín D.E.' → Medellín)",
                 "Segmento y tipo de compra estándar ('IND' → Industrial, 'CONTRATOS' → Contrato)",
                 "Texto → número", "Descartar filas incompletas y con energía ≤ 0",
                 "Descartar filas repetidas"],
}), hide_index=True)

# La ruta del archivo de ventas en bronce (lo crea la pagina 1)
archivo_bronce = config.DIR_BRONCE / "enerandes_ventas.parquet"
# Si todavia no existe, se avisa...
if not archivo_bronce.exists():
    st.warning("Primero carguen el Excel en 📥 *1 · Cargar datos*.")
    # ...y st.stop() detiene la pagina aqui: no se dibuja nada mas
    st.stop()

# Al hacer clic en el boton, se aplica la limpieza
if st.button("Limpiar las ventas", type="primary"):
    # Lee bronce, limpia y guarda en plata; devuelve las dos tablas para comparar
    bronce, plata = limpiar.main()
    # Tres numeros: cuantas entraron, cuantas quedaron y cuantas se descartaron
    c1, c2, c3 = st.columns(3)
    # st.metric: un numero grande con su etiqueta; {:,} pone separador de miles
    c1.metric("Filas en bronce", f"{len(bronce):,}")
    c2.metric("Filas limpias (plata)", f"{len(plata):,}")
    c3.metric("Descartadas", f"{len(bronce) - len(plata):,}")
    # El antes y el despues: como estaba escrito el municipio y como quedo
    a, d = st.columns(2)
    a.write("**Antes (bronce):** formas de escribir el municipio")
    # value_counts: cuenta cuantas filas hay de cada forma de escribir el municipio
    a.dataframe(bronce["Municipio"].value_counts().rename("filas"))
    d.write("**Después (plata):** un solo nombre por municipio")
    # Lo mismo en plata: ahora cada municipio aparece con un solo nombre
    d.dataframe(plata["municipio"].value_counts().rename("filas"))
    # Las primeras 20 filas de las ventas ya limpias
    st.write("**Así quedaron las ventas limpias:**")
    st.dataframe(plata.head(20), hide_index=True)
    # Mensaje verde: donde quedo guardado
    st.success("✅ Guardado en `data/silver/enerandes_ventas.parquet`")

# Una linea horizontal para separar
st.divider()
# Recuadro azul que dice cual es la siguiente pagina
st.info("**Siguiente paso:** 🏅 *3 · Modelo oro (dbt)*.")
