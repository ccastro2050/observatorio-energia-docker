# dbt: el modelo y sus pruebas

> **En una frase:** **dbt** convierte archivos `.sql` en tablas, **en el orden correcto**, y **prueba** que los datos estén bien.

```text
dbt/
├── dbt_project.yml          ← el proyecto: staging = vistas, marts = tablas
├── profiles.yml             ← la conexion: el archivo data/observatorio.duckdb
└── models/
    ├── staging/             ← PASO 1: ordenar lo que llega (vistas)
    │   ├── sources.yml      ← de donde lee: los .parquet de bronce y plata
    │   ├── stg_ventas.sql
    │   ├── stg_mercado_diario.sql
    │   └── stg_oni.sql
    └── marts/               ← PASO 2: el modelo estrella (tablas)
        ├── dim_mes.sql
        ├── dim_municipio.sql
        ├── fact_ventas.sql
        ├── fact_mercado.sql
        └── schema.yml       ← las 10 pruebas de calidad
```

| Concepto | Qué es | Ejemplo |
|---|---|---|
| **Modelo** | Un `SELECT` en un archivo `.sql`. dbt lo convierte en vista o tabla | `fact_mercado.sql` |
| **`source()`** | Leer un archivo de **afuera** de dbt (bronce o plata) | `{{ source('bronce', 'noaa_oni') }}` |
| **`ref()`** | Leer **otro modelo**. Así dbt sabe el orden: primero `stg_oni`, luego `fact_mercado` | `{{ ref('stg_oni') }}` |
| **Staging** | Ordenar lo que llega: texto → número, una fila por día o por mes | `stg_mercado_diario` |
| **Marts** | Las tablas finales del negocio | `fact_ventas` |
| **Prueba** (*test*) | Una regla que los datos deben cumplir | `unique`, `not_null`, `relationships` |
| **DuckDB** | La base de datos: **un solo archivo**, sin servidor | `data/observatorio.duckdb` |

## El comando

```powershell
dbt build --project-dir dbt --profiles-dir dbt
```

`build` = crear todos los modelos **y** correr todas las pruebas. Al final dice `PASS=17` (7 modelos + 10 pruebas).

## ¿Y por qué exportar a `.parquet`?

dbt deja las tablas **dentro** de `observatorio.duckdb`. `src/oro/construir.py` las **copia** a `data/gold/*.parquet` (`COPY tabla TO 'archivo' (FORMAT parquet)`) para que el aplicativo, Power BI o Excel las lean **sin abrir la base**.
