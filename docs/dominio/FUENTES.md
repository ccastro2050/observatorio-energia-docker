# Las fuentes de datos

> **Qué es este documento.** De dónde sale cada dato, cómo se pide y qué trae.

| Fuente | Tipo | Qué trae | Archivo en bronce |
|---|---|---|---|
| **XM** | API REST (JSON, método POST) | Embalses, precio de bolsa y precio de contrato, por día | `xm_embalses`, `xm_precio_bolsa`, `xm_precio_contrato` |
| **NOAA** | Archivo de texto por URL | Índice ONI de El Niño, por trimestre | `noaa_oni` |
| **EnerAndes** | Excel interno | Ventas de 2023: mes, municipio, segmento, tipo de compra, kWh, $ | `enerandes_ventas` |

## 1. XM: el mercado eléctrico

- **Dirección:** `https://servapibi.xm.com.co/daily`
- **Cómo se pide:** un POST con este cuerpo JSON:

```json
{"MetricId": "PorcVoluUtilDiar", "Entity": "Sistema",
 "StartDate": "2023-01-01", "EndDate": "2023-01-30", "Filter": []}
```

- **Límite:** máximo **30 días** por consulta. Por eso el código pide el año en **pedazos de 30 días**.

| Métrica (`MetricId`) | Qué es | Unidad |
|---|---|---|
| `PorcVoluUtilDiar` | Volumen útil de los embalses | Fracción (0,75 = 75 %) |
| `PPPrecBolsNaci` | Precio de bolsa del día | COP/kWh |
| `PrecPromCont` | Precio promedio de los contratos | COP/kWh |

## 2. NOAA: El Niño

- **Dirección:** `https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt`
- **Qué trae:** el **ONI**, la diferencia de temperatura del mar en el Pacífico frente a lo normal.

| ONI | Fase |
|---|---|
| **+0,5 o más** | El Niño (menos lluvia en Colombia) |
| **-0,5 o menos** | La Niña (más lluvia) |
| En medio | Neutral |

## 3. EnerAndes: el Excel de ventas

- **Archivo:** `data/insumos/ventas_enerandes_2023.xlsx`
- **Viene con errores** (a propósito, como los archivos reales): municipios escritos de varias formas, segmentos abreviados, energía negativa, filas vacías, repetidas y una fila `TOTAL`. Los corrige la **capa plata**.

## Si una API falla

En `data/ejemplo/` hay una **copia de respaldo** de XM y NOAA. Si no hay internet, el pipeline (o el botón *Usar el respaldo*) la copia a bronce y todo funciona igual.

Siguiente: [MODELO_DE_DATOS.md](MODELO_DE_DATOS.md)
