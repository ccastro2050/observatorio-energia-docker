-- HECHOS del mercado y el clima: UN MES por fila.
-- Une XM (embalses y precios, promedio del mes) con NOAA (ONI del mes).

with mensual as (
    -- date_trunc('month', fecha): el primer dia del mes -> asi se agrupa por mes
    select date_trunc('month', fecha)       as mes,
           avg(embalses_pct)                as embalses_pct,
           avg(precio_bolsa_cop_kwh)        as precio_bolsa_cop_kwh,
           avg(precio_contrato_cop_kwh)     as precio_contrato_cop_kwh
    from {{ ref('stg_mercado_diario') }}
    group by 1
)

select
    -- 2023-04-01 -> 202304: la misma llave de dim_mes
    cast(strftime(m.mes, '%Y%m') as integer)  as mes_id,
    cast(m.mes as date)                       as mes,
    round(m.embalses_pct, 1)                  as embalses_pct,
    round(m.precio_bolsa_cop_kwh, 1)          as precio_bolsa_cop_kwh,
    round(m.precio_contrato_cop_kwh, 1)       as precio_contrato_cop_kwh,
    o.oni,
    o.fase_enso
from mensual as m
left join {{ ref('stg_oni') }} as o on m.mes = o.mes
