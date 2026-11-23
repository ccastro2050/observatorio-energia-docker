"""
Pagina 4 · DASHBOARD (el "comedor").

Responde 3 preguntas de negocio con las tablas de la capa oro, y trae un
SIMULADOR para que la gerencia pruebe decisiones ("que pasa si...").
Los calculos estan en app/datos.py (la "cocina").
"""
# streamlit: convierte este programa de Python en una pagina web
import streamlit as st

# Las funciones de la cocina (app/datos.py)
from datos import CARPETA_ORO, cargar, costos_de_compra, precio_por_fase, ventas_con_nombres

# Los nombres de los meses, para mostrarlos en espanol
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# Si todavia no hay capa oro, se avisa...
if not (CARPETA_ORO / "fact_mercado.parquet").exists():
    st.warning("Todavía no hay capa oro. Ejecuten las páginas 1, 2 y 3 (o el pipeline).")
    # ...y st.stop() detiene la pagina aqui: no se dibuja nada mas
    st.stop()


# @st.cache_data: lee los archivos UNA sola vez (no con cada clic).
# 'version' es la hora del archivo: si la pagina 3 reconstruye el oro, cambia y se vuelve a leer
@st.cache_data
def leer_todo(version: float):
    # La tabla del mercado, ordenada por mes
    mercado = cargar("fact_mercado").sort_values("mes")
    # Solo los meses que tienen ventas (los de dim_mes)
    mercado = mercado[mercado["mes_id"].isin(cargar("dim_mes")["mes_id"])]
    # El nombre corto del mes: 'Ene', 'Feb'... (para los ejes y el filtro)
    mercado["mes_nombre"] = mercado["mes"].dt.month.map(lambda m: MESES[m - 1])
    # Devuelve las dos tablas: el mercado y las ventas con el nombre del municipio
    return mercado, ventas_con_nombres()


# Se leen las dos tablas (la 'version' es la hora en que se creo el archivo)
mercado, ventas = leer_todo((CARPETA_ORO / "fact_mercado.parquet").stat().st_mtime)

# --- Encabezado -------------------------------------------------------------
# El titulo grande de la pagina
st.title("⚡ Observatorio Energía y Clima · EnerAndes 2023")
# La nota gris: de donde vienen los datos
st.caption("Datos de XM (mercado eléctrico), NOAA (El Niño) y EnerAndes (ventas). "
           "Pipeline: bronce → plata → oro (dbt) → este dashboard.")

# --- FILTROS, en la barra de la izquierda: mueven TODO el dashboard ---------
# El titulo de la barra de la izquierda
st.sidebar.header("🎛️ Filtros")
# Rango de meses: un slider con dos puntas (de enero a diciembre). Devuelve las dos puntas
desde, hasta = st.sidebar.select_slider("Meses", options=MESES, value=("Ene", "Dic"))
# Los meses que quedan entre las dos puntas: de 'desde' hasta 'hasta'
meses_elegidos = MESES[MESES.index(desde):MESES.index(hasta) + 1]
# Fases de El Nino: lista para marcar varias. Por defecto, las tres
fases = st.sidebar.multiselect("Fase ENSO", ["La Niña", "Neutral", "El Niño"],
                               default=["La Niña", "Neutral", "El Niño"])
# Filtro de municipio: la lista sale de los datos. Vacio = todos
municipios = st.sidebar.multiselect("Municipio", sorted(ventas["municipio"].unique()),
                                    placeholder="Todos")
# Filtro de segmento: Residencial, Comercial, Industrial. Vacio = todos
segmentos = st.sidebar.multiselect("Segmento", sorted(ventas["segmento"].unique()),
                                   placeholder="Todos")
# Una nota para el usuario
st.sidebar.caption("Muevan cualquier filtro: todas las pestañas se recalculan.")

# Se aplican los filtros al mercado: los meses elegidos Y las fases elegidas
m = mercado[mercado["mes_nombre"].isin(meses_elegidos) & mercado["fase_enso"].isin(fases)]
# Las ventas de esos mismos meses
v = ventas[ventas["mes_id"].isin(m["mes_id"])]
# Si eligio municipios, se dejan solo esos
if municipios:
    v = v[v["municipio"].isin(municipios)]
# Si eligio segmentos, se dejan solo esos
if segmentos:
    v = v[v["segmento"].isin(segmentos)]

# Si los filtros dejan todo vacio, se avisa y no se dibuja nada mas
if m.empty or v.empty:
    st.warning("Con esos filtros no quedan datos. Amplíen los meses o las fases.")
    st.stop()

# --- KPIs: los numeros grandes de arriba (cambian con los filtros) ----------
# Lo que cuesta cada venta en bolsa y por contrato (la funcion de la cocina)
costos = costos_de_compra(v, m)
# Cuatro columnas, una por KPI
k1, k2, k3, k4 = st.columns(4)
# KPI 1: el promedio de los embalses en los meses filtrados
k1.metric("Embalses (promedio)", f"{m['embalses_pct'].mean():.1f} %")
# KPI 2: el precio de bolsa promedio; el delta (abajo) dice cuanto mas caro que el contrato
k2.metric("Precio de bolsa (promedio)", f"{m['precio_bolsa_cop_kwh'].mean():,.0f} COP/kWh",
          f"{m['precio_bolsa_cop_kwh'].mean() - m['precio_contrato_cop_kwh'].mean():+,.0f} vs. contrato",
          # inverse: si sube, se pinta en rojo (mas caro es malo)
          delta_color="inverse")
# KPI 3: la energia vendida, en GWh (1 GWh = 1.000.000 kWh)
k3.metric("Energía vendida", f"{v['energia_kwh'].sum() / 1e6:,.1f} GWh")
# KPI 4: que parte de la energia se compro en bolsa
k4.metric("Comprada en bolsa",
          f"{v.loc[v['tipo_compra'] == 'Bolsa', 'energia_kwh'].sum() / v['energia_kwh'].sum():.0%}")

# --- Una pestana por pregunta, y el simulador -------------------------------
p1, p2, p3, p4 = st.tabs(["💧 1 · Riesgo hídrico", "🌡️ 2 · Clima → precio",
                          "💰 3 · Impacto en el negocio", "🧮 Simulador"])

# Pestana 1: todo lo indentado debajo se dibuja dentro de ella
with p1:
    # La pregunta de negocio
    st.subheader("¿Cómo estuvieron los embalses y el precio mes a mes?")
    # El usuario elige que ver: botones de opcion en una fila
    ver = st.radio("Ver", ["Embalses (%)", "Precio de bolsa (COP/kWh)", "Los dos"], horizontal=True)
    # Embalses y precio tienen escalas muy distintas (60-80 % frente a 200-1.000 COP/kWh):
    # por eso "Los dos" muestra DOS graficos lado a lado, cada uno con su propio eje
    if ver == "Los dos":
        c1, c2 = st.columns(2)
        c1.line_chart(m, x="mes", y="embalses_pct", x_label="Mes", y_label="Embalses (%)")
        c2.line_chart(m, x="mes", y="precio_bolsa_cop_kwh", x_label="Mes",
                      y_label="Precio de bolsa (COP/kWh)", color="#d62728")
    # Si eligio solo uno: un grafico; y_label = el nombre que el usuario eligio
    else:
        columna = "embalses_pct" if ver == "Embalses (%)" else "precio_bolsa_cop_kwh"
        st.line_chart(m, x="mes", y=columna, x_label="Mes", y_label=ver)
    # El mes con los embalses mas bajos (idxmin = la fila del minimo)
    minimo = m.loc[m["embalses_pct"].idxmin()]
    # El mes con el precio mas alto (idxmax = la fila del maximo)
    maximo = m.loc[m["precio_bolsa_cop_kwh"].idxmax()]
    # La conclusion, con los numeros calculados
    st.info(f"Embalses más bajos: {minimo['embalses_pct']:.1f} % en {minimo['mes_nombre']}. "
            f"Precio más alto: {maximo['precio_bolsa_cop_kwh']:,.0f} COP/kWh en {maximo['mes_nombre']}. "
            f"Con poca agua, el sistema usa más térmicas, que son más caras.")
    # Una seccion que se abre con clic: la tabla del detalle (se ordena con clic en el encabezado)
    with st.expander("Ver la tabla mes a mes"):
        st.dataframe(m[["mes_nombre", "embalses_pct", "precio_bolsa_cop_kwh",
                        "precio_contrato_cop_kwh", "oni", "fase_enso"]], hide_index=True)

# Pestana 2
with p2:
    st.subheader("¿El Niño sube el precio de la energía?")
    # Dos graficos lado a lado: el ONI y los precios
    c1, c2 = st.columns(2)
    c1.line_chart(m, x="mes", y="oni", x_label="Mes", y_label="ONI (El Niño si ≥ 0,5)")
    # Nombres claros para la leyenda: Bolsa y Contrato (en vez de los nombres de columna)
    precios = m.rename(columns={"precio_bolsa_cop_kwh": "Bolsa", "precio_contrato_cop_kwh": "Contrato"})
    c2.line_chart(precios, x="mes", y=["Bolsa", "Contrato"], x_label="Mes", y_label="Precio (COP/kWh)")
    # Dispersion: cada punto es un mes (ONI contra precio), con color segun la fase
    st.scatter_chart(m, x="oni", y="precio_bolsa_cop_kwh", color="fase_enso", size=200,
                     x_label="ONI", y_label="Precio de bolsa (COP/kWh)")
    # El precio promedio en cada fase (la funcion de la cocina)
    por_fase = precio_por_fase(m)
    # Barras: una por fase
    st.bar_chart(por_fase, x="fase_enso", y="precio_bolsa_cop_kwh",
                 x_label="Fase ENSO", y_label="Precio de bolsa promedio (COP/kWh)")
    # La conclusion solo si quedaron las dos fases a comparar (los filtros pueden quitar una)
    if {"El Niño", "Neutral"} <= set(por_fase["fase_enso"]):
        # El precio promedio de cada fase
        nino = por_fase.set_index("fase_enso").loc["El Niño", "precio_bolsa_cop_kwh"]
        neutral = por_fase.set_index("fase_enso").loc["Neutral", "precio_bolsa_cop_kwh"]
        st.info(f"En El Niño la bolsa costó en promedio {nino:,.0f} COP/kWh, frente a "
                f"{neutral:,.0f} en los meses neutrales: {nino / neutral:.1f} veces más. "
                f"El precio de contrato casi no cambia: el contrato protege.")

# Pestana 3
with p3:
    st.subheader("¿Cuánto habría costado comprar en bolsa lo que se compró por contrato?")
    # Solo la energia que se compro por contrato
    contrato = costos[costos["tipo_compra"] == "Contrato"]
    # Sumada por mes: lo que costo por contrato y lo que habria costado en bolsa
    por_mes = contrato.groupby("mes_id", as_index=False)[["costo_contrato", "costo_bolsa"]].sum()
    # Nombres claros para la leyenda del grafico
    por_mes = por_mes.rename(columns={"costo_contrato": "Por contrato", "costo_bolsa": "En bolsa"})
    # En millones de pesos (1e6 = 1.000.000)
    por_mes[["Por contrato", "En bolsa"]] = (por_mes[["Por contrato", "En bolsa"]] / 1e6).round(0)
    # El nombre del mes: 202304 -> 202304 % 100 = 4 -> 'Abr'
    por_mes["mes"] = por_mes["mes_id"].map(lambda x: MESES[x % 100 - 1])
    # Barras lado a lado (stack=False), en el orden de los meses (sort=False)
    st.bar_chart(por_mes, x="mes", y=["Por contrato", "En bolsa"], stack=False, sort=False,
                 x_label="Mes", y_label="Millones de pesos")
    # Cuanto mas habria costado en total, en millones
    total = contrato["sobrecosto"].sum() / 1e6
    st.info(f"Comprar en bolsa la energía que se compró por contrato habría costado "
            f"{abs(total):,.0f} millones de pesos {'más' if total > 0 else 'menos'}.")
    # Donde esta el riesgo: el usuario elige si agrupar por municipio o por segmento
    agrupar = st.selectbox("Dónde está el riesgo, por", ["municipio", "segmento"])
    # La energia que SI se compro en bolsa: cuanto costo de mas, por municipio o segmento
    riesgo = (costos[costos["tipo_compra"] == "Bolsa"]
              .groupby(agrupar, as_index=False)["sobrecosto"].sum())
    riesgo["Sobrecosto (millones)"] = (riesgo["sobrecosto"] / 1e6).round(1)
    # De mayor a menor
    riesgo = riesgo.sort_values("Sobrecosto (millones)", ascending=False)
    # Barras horizontales, en ese orden
    st.bar_chart(riesgo, x=agrupar, y="Sobrecosto (millones)", horizontal=True, sort=False)

# Pestana 4: el simulador
with p4:
    st.subheader("🧮 ¿Qué pasa si EnerAndes cambia cuánto compra en bolsa?")
    st.write("Muevan el control: el simulador recalcula con los **precios reales de XM** "
             "y la **energía vendida** en los meses y municipios filtrados.")
    # El control deslizante: de 0 a 100 %, empieza en 22 % (lo que compro de verdad), de 5 en 5
    porcentaje = st.slider("Energía comprada en bolsa (%)", 0, 100, 22, step=5)
    # Para cada mes: la energia vendida y los dos precios de ese mes
    energia_mes = v.groupby("mes_id", as_index=False)["energia_kwh"].sum().merge(
        m[["mes_id", "precio_bolsa_cop_kwh", "precio_contrato_cop_kwh"]], on="mes_id")
    # El porcentaje como fraccion: 22 % -> 0.22
    p = porcentaje / 100
    # Costo = energia x (parte en bolsa x precio bolsa + parte en contrato x precio contrato)
    costo = (energia_mes["energia_kwh"] * (p * energia_mes["precio_bolsa_cop_kwh"]
             + (1 - p) * energia_mes["precio_contrato_cop_kwh"])).sum()
    # Lo que costaria comprar TODO por contrato, para comparar
    todo_contrato = (energia_mes["energia_kwh"] * energia_mes["precio_contrato_cop_kwh"]).sum()
    # Los dos resultados, lado a lado
    s1, s2 = st.columns(2)
    s1.metric("Costo de compra con ese reparto", f"{costo / 1e6:,.0f} millones")
    s2.metric("Frente a comprar todo por contrato", f"{(costo - todo_contrato) / 1e6:+,.0f} millones",
              delta_color="off")
    st.info("En un año con El Niño, cada punto de energía que se pasa a bolsa sube el costo. "
            "La lección: **asegurar contratos antes de que llegue El Niño**.")
