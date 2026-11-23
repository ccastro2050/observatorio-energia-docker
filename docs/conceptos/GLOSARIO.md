# Glosario

| Término | Qué significa |
|---|---|
| **API REST** | Una dirección web que responde datos (normalmente en JSON) cuando se le pide con GET o POST |
| **Bolsa de energía** | El mercado donde la energía se compra al precio del día. Lo administra **XM** |
| **Capa (bronce, plata, oro)** | Cada etapa del dato: tal cual llega, limpio, listo para el negocio |
| **Comercializadora** | La empresa que compra energía al mercado y la vende a los usuarios (EnerAndes) |
| **Contenedor** | Un programa empacado con todo lo que necesita, corriendo en Docker |
| **Contrato (de energía)** | Compra a precio fijo pactado por adelantado |
| **DataFrame** | Una tabla en memoria de pandas |
| **dbt** | Herramienta que convierte `SELECT` en tablas, en orden, y las prueba |
| **Dimensión** | Tabla con descripciones para filtrar y agrupar (`dim_municipio`) |
| **DIVIPOLA** | El código oficial de cada municipio en Colombia (Medellín = `05001`) |
| **DuckDB** | Base de datos de **un solo archivo**, muy rápida para análisis |
| **El Niño / La Niña** | Calentamiento / enfriamiento del Pacífico. El Niño = menos lluvia en Colombia |
| **ENSO** | El ciclo El Niño – Neutral – La Niña |
| **Embalse** | El lago de una hidroeléctrica. `embalses_pct` = qué tan lleno está |
| **Hechos** | Tabla con los eventos y sus números (`fact_ventas`) |
| **JSON** | Formato de texto para datos: `{"clave": "valor"}` |
| **KPI** | Indicador clave: el número que mira primero la gerencia |
| **Llave** | Columna que une dos tablas (`mes_id`) |
| **ONI** | Índice de El Niño de NOAA. +0,5 o más = El Niño |
| **Parquet** | Formato de archivo para tablas: guarda los tipos, pesa poco y se lee rápido |
| **Pipeline** | Programa que ejecuta los pasos del dato en orden, sin intervención |
| **Prueba de calidad** | Regla que los datos deben cumplir (`not_null`, `unique`...) |
| **Respaldo** | Copia de los datos (`data/ejemplo/`) para cuando una API falla |
| **Staging** | Primer paso de dbt: ordenar lo que llega |
| **Streamlit** | Librería que convierte Python en una página web |
| **Volumen** | Carpeta compartida entre un contenedor y el PC |
| **XM** | La empresa que opera el sistema eléctrico y el mercado de energía de Colombia |
