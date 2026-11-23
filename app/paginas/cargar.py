"""
Pagina 1 · CARGAR DATOS (capa BRONCE).
El usuario elige que traer de cada fuente: metricas y fechas de XM, la URL de
NOAA y el Excel de EnerAndes (el incluido o uno que suba). Todo se guarda TAL CUAL.
"""
# date: para las fechas del calendario
from datetime import date

# streamlit: los controles de la pagina
import streamlit as st

# La configuracion y las funciones de la capa bronce
from src import config
from src.bronce.extraer import extraer_enerandes, extraer_noaa, extraer_xm, usar_respaldo

# El titulo grande de la pagina
st.title("📥 1 · Cargar datos: capa bronce")
# Un parrafo que explica la pagina (los ** ponen el texto en negrita)
st.write("Aquí se **traen** los datos de las 3 fuentes y se guardan **tal cual llegan** en "
         "`data/bronze/`. En bronce no se corrige nada: si algo viene mal, se arregla en plata.")

# Tres pestanas, una por fuente
f1, f2, f3 = st.tabs(["🔌 XM (API REST)", "🌊 NOAA (URL)", "📄 EnerAndes (Excel)"])

# --- Fuente 1: XM -------------------------------------------------------------
# with f1: todo lo que sigue se dibuja dentro de la primera pestana
with f1:
    # Subtitulo de la pestana
    st.subheader("XM: el mercado eléctrico de Colombia")
    # Nota gris con la direccion de la API (format cambia {periodo} por 'daily')
    st.caption(f"API: `{config.XM_URL.format(periodo='daily')}` · método POST · máximo 30 días por consulta")
    # Las metricas disponibles: el usuario marca cuales quiere
    # Diccionario: texto que ve el usuario -> (codigo, entidad, nombre del archivo)
    nombres = {f"{nombre} ({codigo})": (codigo, entidad, nombre)
               for codigo, entidad, nombre in config.XM_METRICAS}
    # st.multiselect: lista para marcar varias; por defecto vienen todas marcadas
    elegidas = st.multiselect("Métricas", list(nombres), default=list(nombres))
    # El rango de fechas: dos calendarios
    # st.columns(2): parte la pantalla en dos columnas, una para cada calendario
    c1, c2 = st.columns(2)
    # st.date_input: un calendario para elegir la fecha (no deja ir antes de 2015)
    inicio = c1.date_input("Desde", config.FECHA_INICIO, min_value=date(2015, 1, 1))
    fin = c2.date_input("Hasta", config.FECHA_FIN, min_value=date(2015, 1, 1))
    # Cuantos dias hay en el rango (+1 para contar tambien el ultimo dia)
    dias = (fin - inicio).days + 1
    # Nota con el numero de consultas: -(-dias // 30) es la division redondeada hacia arriba
    st.caption(f"{dias} días → {-(-dias // 30)} consultas por métrica (pedazos de 30 días). "
               "Las ventas son de 2023: para el dashboard, dejen el rango dentro de 2023.")
    # Boton principal: queda apagado si no hay metricas elegidas o las fechas estan al reves
    if st.button("Descargar de XM", type="primary", disabled=not elegidas or dias < 1):
        # st.status: un recuadro que muestra que esta pasando mientras descarga
        with st.status("Pidiendo los datos a XM...", expanded=True) as estado:
            # try/except: si la API falla, se atrapa el error y se muestra sin romper la pagina
            try:
                # Descarga las metricas elegidas y las guarda en bronce
                tablas = extraer_xm([nombres[n] for n in elegidas], inicio, fin)
                # Por cada archivo guardado, una linea con cuantas filas tiene
                for nombre, tabla in tablas.items():
                    st.write(f"✅ `bronze/{nombre}.parquet`: {len(tabla):,} filas")
                # Cambia el recuadro a 'listo' (en verde)
                estado.update(label="XM: listo", state="complete")
                # Muestra las primeras filas de la primera tabla descargada
                st.dataframe(next(iter(tablas.values())).head(), hide_index=True)
            # Si algo fallo: el recuadro se pone en rojo y se muestra el error
            except Exception as error:
                estado.update(label="XM no respondió", state="error")
                st.error(f"{error}")
    # Boton de respaldo: copia los archivos guardados de antes, sin usar internet
    if st.button("Usar el respaldo de XM (sin internet)"):
        usar_respaldo([nombre for _, _, nombre in config.XM_METRICAS])
        # Mensaje verde de exito
        st.success("Se copiaron los archivos de `data/ejemplo/` a `data/bronze/`.")

# --- Fuente 2: NOAA -----------------------------------------------------------
# Todo lo que sigue va dentro de la segunda pestana
with f2:
    # Subtitulo y nota gris de la pestana
    st.subheader("NOAA: el índice ONI de El Niño")
    st.caption("Un archivo de texto en internet: columnas separadas por espacios.")
    # La URL se puede cambiar: por ejemplo, para otro indice de NOAA
    # st.text_input: una caja de texto; trae escrita la URL de config.py
    url = st.text_input("URL del archivo", config.NOAA_ONI_URL)
    # Al hacer clic en el boton, se descarga el archivo
    if st.button("Descargar de NOAA", type="primary"):
        # st.spinner: muestra un circulo girando mientras descarga
        with st.spinner("Descargando..."):
            # try/except: si la descarga falla, se muestra el error sin romper la pagina
            try:
                # Descarga el texto de la URL y lo guarda en bronce
                tabla = extraer_noaa(url)
                st.success(f"✅ `bronze/noaa_oni.parquet`: {len(tabla):,} filas")
                # tail(6): muestra las ultimas 6 filas (los meses mas recientes)
                st.dataframe(tabla.tail(6), hide_index=True)
            except Exception as error:
                # Mensaje rojo con el error
                st.error(f"No se pudo descargar: {error}")
    # Boton de respaldo: copia el archivo de data/ejemplo/ sin usar internet
    if st.button("Usar el respaldo de NOAA (sin internet)"):
        usar_respaldo(["noaa_oni"])
        st.success("Se copió `noaa_oni.parquet` de `data/ejemplo/` a `data/bronze/`.")

# --- Fuente 3: EnerAndes ------------------------------------------------------
# Todo lo que sigue va dentro de la tercera pestana
with f3:
    # Subtitulo y nota gris de la pestana
    st.subheader("EnerAndes: el Excel interno de ventas")
    st.caption("Trae los errores típicos de un archivo hecho a mano: así se guarda en bronce.")
    # st.file_uploader: el usuario arrastra su archivo; si no sube nada, se usa el incluido
    subido = st.file_uploader("Subir otro Excel (opcional)", type=["xlsx"])
    # Nota con el nombre del Excel que se usa si no suben nada
    st.caption(f"Si no suben nada, se usa `data/insumos/{config.ENERANDES_EXCEL.name}`.")
    # Al hacer clic, se lee el Excel y se guarda en bronce
    if st.button("Cargar el Excel", type="primary"):
        # try/except: si el Excel no se puede leer, se muestra el error
        try:
            # Lee el Excel subido (o el incluido si 'subido' esta vacio) y lo guarda
            tabla = extraer_enerandes(subido)
            st.success(f"✅ `bronze/enerandes_ventas.parquet`: {len(tabla):,} filas")
            # Muestra las primeras 10 filas, con sus errores tal cual
            st.dataframe(tabla.head(10), hide_index=True)
        except Exception as error:
            st.error(f"No se pudo leer el Excel: {error}")

# Una linea horizontal para separar
st.divider()
# Recuadro azul que dice cual es la siguiente pagina
st.info("**Siguiente paso:** 🧹 *2 · Limpiar (plata)*, en el menú de la izquierda.")
