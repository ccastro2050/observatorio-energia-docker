"""
El APLICATIVO completo, con Streamlit: el proceso de integracion paso a paso.

    streamlit run app/inicio.py      ->  http://localhost:8501

Cada pagina es una capa del proceso:
  1. Cargar datos   (BRONCE)  traer XM, NOAA y el Excel de EnerAndes
  2. Limpiar        (PLATA)   aplicar las reglas a las ventas
  3. Modelo oro     (ORO)     dbt arma el modelo estrella y lo prueba
  4. Dashboard                las preguntas de negocio y el simulador
  5. Explorar capas           ver cualquier archivo de cualquier capa
"""
# sys y Path: para que las paginas encuentren la carpeta src/ (la raiz del proyecto)
import sys
from pathlib import Path

# streamlit: convierte este programa de Python en una pagina web
import streamlit as st

# La raiz del proyecto (una carpeta arriba de app/) y la carpeta app/
RAIZ = Path(__file__).resolve().parent.parent
# Agrega las dos carpetas a sys.path (donde Python busca los import), si no estan ya
for carpeta in (RAIZ, RAIZ / "app"):
    if str(carpeta) not in sys.path:
        # insert(0, ...): la pone de primera en la lista de busqueda
        sys.path.insert(0, str(carpeta))

# El titulo de la pestana del navegador, el icono y usar todo el ancho
st.set_page_config(page_title="Observatorio Energía y Clima", page_icon="⚡", layout="wide")

# st.navigation: el MENU de la izquierda, con una entrada por pagina.
# url_path: la direccion de cada pagina (http://localhost:8501/cargar). El panel es la de inicio (/)
paginas = st.navigation({
    # Primer grupo del menu: las paginas de las capas
    "El proceso, capa por capa": [
        # default=True: el panel de control es la pagina que se abre al entrar
        st.Page("paginas/panel.py", title="0 · Panel de control", icon="🎛️", default=True),
        # st.Page: una pagina del menu (archivo, titulo, icono y direccion)
        st.Page("paginas/cargar.py", title="1 · Cargar datos (bronce)", icon="📥", url_path="cargar"),
        st.Page("paginas/limpiar.py", title="2 · Limpiar (plata)", icon="🧹", url_path="limpiar"),
        st.Page("paginas/oro.py", title="3 · Modelo oro (dbt)", icon="🏅", url_path="oro"),
    ],
    # Segundo grupo del menu: el resultado
    "El resultado": [
        st.Page("paginas/dashboard.py", title="4 · Dashboard", icon="📊", url_path="dashboard"),
        st.Page("paginas/explorar.py", title="5 · Explorar capas", icon="🔎", url_path="explorar"),
    ],
})
# Ejecuta la pagina que el usuario eligio en el menu
paginas.run()
