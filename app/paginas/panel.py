"""
Pagina 0 · PANEL DE CONTROL.
Todo el proceso sin escribir comandos: ver el estado de cada capa, empezar de cero,
correr todo o solo una capa, y ver en pantalla lo que va pasando.
"""
# contextlib.redirect_stdout: atrapar lo que el proceso escribe con print/log
from contextlib import redirect_stdout
# datetime: para decir hace cuanto se actualizo cada capa
from datetime import datetime
# io.StringIO: un "archivo" en memoria donde se guarda ese texto
from io import StringIO

# streamlit: los controles de la pagina
import streamlit as st

# La configuracion y las tres capas
from src import config
from src.bronce import extraer
from src.oro import construir
from src.pipeline import empezar_de_cero
from src.plata import limpiar

# El titulo grande y la explicacion
st.title("🎛️ 0 · Panel de control")
st.write("Desde aquí se maneja **todo el proceso sin comandos**: empezar de cero, correr todo "
         "o solo una capa. Al terminar, el **Dashboard se actualiza solo**.")


# Funcion: describe el estado de una carpeta (cuantos archivos y hace cuanto)
def estado(carpeta) -> dict:
    # Los archivos .parquet de la carpeta (lista vacia si la carpeta no existe)
    archivos = list(carpeta.glob("*.parquet")) if carpeta.exists() else []
    # Si no hay archivos: la capa esta vacia
    if not archivos:
        return {"Estado": "❌ vacía", "Archivos": 0, "Actualizada": "—"}
    # La fecha del archivo mas reciente (st_mtime = hora de la ultima modificacion)
    ultimo = datetime.fromtimestamp(max(a.stat().st_mtime for a in archivos))
    # Cuantos minutos han pasado desde entonces
    minutos = int((datetime.now() - ultimo).total_seconds() // 60)
    return {"Estado": "✅ lista", "Archivos": len(archivos),
            "Actualizada": f"hace {minutos} min" if minutos else "hace un momento"}


# --- El estado de las tres capas --------------------------------------------
st.subheader("Estado de las capas")
# Una fila por capa, con su carpeta y su estado
st.dataframe([{"Capa": "🥉 Bronce", "Carpeta": "data/bronze/", **estado(config.DIR_BRONCE)},
              {"Capa": "🥈 Plata", "Carpeta": "data/silver/", **estado(config.DIR_PLATA)},
              {"Capa": "🥇 Oro", "Carpeta": "data/gold/", **estado(config.DIR_ORO)}],
             hide_index=True)


# Funcion: corre una o varias capas, guarda lo que escribieron y recarga la pagina
def correr(pasos: list, titulo: str) -> None:
    # st.spinner: circulo girando mientras trabaja
    with st.spinner(f"{titulo}..."):
        # salida: aqui se guarda todo lo que el proceso escribe
        salida = StringIO()
        try:
            # Todo lo que se imprima dentro de este bloque va a 'salida', no a la terminal
            with redirect_stdout(salida):
                # Una vuelta por cada paso: (nombre, funcion)
                for nombre, funcion in pasos:
                    funcion()
            # Si todo salio bien
            resultado = (True, f"{titulo}: listo ✅")
        # SystemExit: lo que lanza la capa oro si una prueba de dbt falla
        except (Exception, SystemExit) as error:
            resultado = (False, f"{titulo}: falló ❌ — {error}")
    # Se borra la memoria del dashboard: la proxima vez lee los datos nuevos
    st.cache_data.clear()
    # st.session_state: la "memoria" de la pagina; sobrevive a la recarga de abajo
    st.session_state["ultima_corrida"] = (*resultado, salida.getvalue())
    # st.rerun: vuelve a dibujar la pagina desde arriba, con la tabla de estado al dia
    st.rerun()


# --- El Excel de ventas: usar el original o subir otro ------------------------
st.subheader("El Excel de ventas")
# Cual Excel se esta usando ahora
st.write(f"En uso: `data/insumos/{config.excel_activo().name}`"
         + (" — **subido por ustedes**" if config.ENERANDES_SUBIDO.exists() else " — el original"))
# st.file_uploader: arrastrar un .xlsx; queda como el Excel que usa todo el proceso
subido = st.file_uploader("Subir otro Excel de ventas (opcional)", type=["xlsx"])
if subido is not None:
    try:
        # Revisa las columnas y lo guarda como el Excel activo
        tabla = extraer.guardar_excel_subido(subido)
        st.success(f"✅ Excel guardado ({len(tabla):,} filas). Ahora: ▶️ Correr todo.")
    except Exception as error:
        st.error(f"No se pudo usar ese Excel: {error}")
# Volver al original (solo si hay uno subido)
if config.ENERANDES_SUBIDO.exists() and st.button("↩️ Volver al Excel original"):
    extraer.volver_al_excel_original()
    st.success("Listo: se usa otra vez el Excel original. Ahora: ▶️ Correr todo.")

# Los tres pasos del proceso: (nombre, funcion que lo ejecuta)
BRONCE = ("Bronce", extraer.main)
PLATA = ("Plata", limpiar.main)
ORO = ("Oro", construir.main)

# --- Los botones ---------------------------------------------------------------
st.subheader("Correr el proceso")
# Tres columnas para los botones principales
c1, c2, c3 = st.columns(3)

# Columna 1: empezar de cero, con una casilla de confirmacion para no borrar por error
with c1:
    seguro = st.checkbox("Sí, quiero borrar todo")
    if st.button("🗑️ Empezar de cero", disabled=not seguro, use_container_width=True):
        empezar_de_cero()
        # Se borra la memoria del dashboard
        st.cache_data.clear()
        # Se guarda el mensaje y se recarga la pagina, para que la tabla de estado diga "vacia"
        st.session_state["ultima_corrida"] = (True, "Se borraron bronce, plata, oro y la base. "
                                              "Ahora: ▶️ Correr todo.", "")
        st.rerun()

# Columna 2: correr las tres capas en orden
with c2:
    st.write("")   # un espacio, para alinear con la casilla de la columna 1
    todo = st.button("▶️ Correr todo (bronce → plata → oro)", type="primary",
                     use_container_width=True)

# Columna 3: un enlace directo al dashboard
with c3:
    st.write("")
    st.page_link("paginas/dashboard.py", label="Ver el Dashboard", icon="📊")

# Correr solo una capa: tres botones mas pequenos
st.write("**O solo una capa:**")
b1, b2, b3 = st.columns(3)
solo_bronce = b1.button("1 · Solo bronce (traer los datos)", use_container_width=True)
solo_plata = b2.button("2 · Solo plata (limpiar)", use_container_width=True)
solo_oro = b3.button("3 · Solo oro (dbt + exportar)", use_container_width=True)

# Segun el boton que se apreto, se corren esos pasos
if todo:
    correr([BRONCE, PLATA, ORO], "Corriendo bronce → plata → oro")
elif solo_bronce:
    correr([BRONCE], "Corriendo la capa bronce")
elif solo_plata:
    correr([PLATA], "Corriendo la capa plata")
elif solo_oro:
    correr([ORO], "Corriendo la capa oro")

# El resultado de la ultima vez que se corrio algo (lo guardo correr() antes de recargar)
if "ultima_corrida" in st.session_state:
    # bien: si salio bien; mensaje: el titulo; texto: lo que escribio el proceso
    bien, mensaje, texto = st.session_state["ultima_corrida"]
    # Verde si salio bien, rojo si fallo
    (st.success if bien else st.error)(mensaje)
    # Lo que escribio el proceso, en una seccion que se abre con clic
    if texto:
        with st.expander("Ver lo que hizo el proceso, paso a paso", expanded=True):
            st.code(texto, language=None)

st.divider()
st.caption("¿Quieren elegir fechas, cambiar la URL o subir otro Excel? Usen la página 📥 1 · Cargar datos.")
