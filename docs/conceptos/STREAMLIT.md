# Streamlit: el aplicativo

> **En una frase:** Streamlit convierte un programa de Python en una **página web**: **una línea de Python = un elemento en la página**. Sin HTML ni JavaScript.

## Cómo funciona

1. Lee el archivo **de arriba hacia abajo** y dibuja en ese orden.
2. Cada vez que el usuario **mueve un control** (filtro, botón, slider), **vuelve a ejecutar** el archivo con el valor nuevo.
3. Por eso todo lo que va después de un filtro **se recalcula solo**: eso lo hace interactivo.

## Las funciones que usa este proyecto

| Función | Qué dibuja | Dónde |
|---|---|---|
| `st.navigation` + `st.Page` | El **menú** de páginas a la izquierda | `app/inicio.py` |
| `st.title`, `st.subheader`, `st.write`, `st.caption` | Textos | Todas |
| `st.tabs` + `with` | Pestañas | Dashboard, Cargar |
| `st.columns` | Columnas lado a lado | Dashboard |
| `st.metric` | **KPI**: número grande con etiqueta | Dashboard |
| `st.sidebar.select_slider`, `st.sidebar.multiselect` | **Filtros** en la barra izquierda | Dashboard |
| `st.radio`, `st.selectbox`, `st.slider` | Controles para elegir | Dashboard, Explorar |
| `st.date_input`, `st.text_input`, `st.file_uploader` | Fechas, URL y **subir un archivo** | Cargar |
| `st.button` | Botón: ejecuta algo al hacer clic | Cargar, Limpiar, Oro |
| `st.status`, `st.spinner` | "Trabajando..." mientras descarga | Cargar, Oro |
| `st.line_chart`, `st.bar_chart`, `st.scatter_chart` | Gráficos (con zoom y datos al pasar el mouse) | Dashboard |
| `st.dataframe` | Tabla (se ordena con clic en el encabezado) | Todas |
| `st.info`, `st.success`, `st.warning`, `st.error` | Recuadros de color: conclusión, éxito, aviso, error | Todas |
| `@st.cache_data` | Leer los datos **una sola vez** (no con cada clic) | Dashboard |
| `st.stop()` | Detener la página (por ejemplo, si faltan datos) | Todas |

## La cocina y el comedor

| Archivo | Qué tiene |
|---|---|
| `app/datos.py` (la **cocina**) | Leer el oro y **calcular** con pandas. Sin Streamlit: se prueba con `pytest` |
| `app/paginas/*.py` (el **comedor**) | **Mostrar**: pide los cálculos a la cocina |

## Las tres reglas de un buen dashboard

1. **Una pestaña por pregunta**, con la pregunta escrita arriba (`st.subheader`).
2. **Cada gráfico con su conclusión** (`st.info`), con números **calculados**, no escritos a mano.
3. **Los cálculos en `datos.py`**: la página solo muestra.
