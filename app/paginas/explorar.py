"""
Pagina 5 · EXPLORAR CAPAS.
Elegir una capa y un archivo, y verlo: filas, columnas, tipos y una muestra.
Sirve para comparar el MISMO dato en bronce, plata y oro.
"""
# pandas: leer los Parquet
import pandas as pd
# streamlit: los controles de la pagina
import streamlit as st

# La configuracion: donde esta cada capa
from src import config

# El titulo grande y un parrafo de explicacion
st.title("🔎 5 · Explorar las capas")
st.write("Elijan una capa y un archivo para ver **qué tiene adentro**.")

# Las tres capas y su carpeta
capas = {"🥉 Bronce (tal cual llegó)": config.DIR_BRONCE,
         "🥈 Plata (limpio)": config.DIR_PLATA,
         "🥇 Oro (modelo estrella)": config.DIR_ORO}
# st.radio: botones redondos para elegir UNA capa (horizontal=True: en una sola fila)
capa = st.radio("Capa", list(capas), horizontal=True)
# Los archivos .parquet de esa carpeta, en orden; si la carpeta no existe, lista vacia
archivos = sorted(capas[capa].glob("*.parquet")) if capas[capa].exists() else []

# Si no hay archivos: se avisa y se detiene la pagina
if not archivos:
    st.warning("Esta capa está vacía: ejecuten primero las páginas 1 a 3.")
    st.stop()

# st.selectbox: lista desplegable; format_func muestra solo el nombre del archivo
archivo = st.selectbox("Archivo", archivos, format_func=lambda a: a.name)
# Lee el archivo elegido como tabla de pandas
df = pd.read_parquet(archivo)

# Tres numeros del archivo
c1, c2, c3 = st.columns(3)
# Cuantas filas tiene la tabla
c1.metric("Filas", f"{len(df):,}")
# shape[1]: cuantas columnas tiene
c2.metric("Columnas", df.shape[1])
# El tamano del archivo en disco: st_size viene en bytes, / 1024 lo pasa a KB
c3.metric("Tamaño", f"{archivo.stat().st_size / 1024:,.0f} KB")

# Buscar dentro de la tabla: filtra las filas que contienen el texto
buscar = st.text_input("Buscar en la tabla (por ejemplo: Medellín, 2023-09, El Niño)")
# Pasa todo a texto, busca en cada columna (sin importar mayusculas) y deja las filas que coinciden
vista = df[df.astype(str).apply(lambda col: col.str.contains(buscar, case=False)).any(axis=1)] if buscar else df
# Muestra hasta 500 filas (para que la pagina no se ponga lenta)
st.dataframe(vista.head(500), hide_index=True)

# Los tipos de cada columna: en bronce todo es texto; en oro ya son numeros y fechas
with st.expander("Ver los tipos de cada columna"):
    # dtypes: el tipo de cada columna, pasado a texto para mostrarlo
    st.dataframe(df.dtypes.astype(str).rename("tipo"))
