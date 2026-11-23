-- STAGING: embalses, precio de bolsa y precio de contrato, UNA FILA POR DIA.
-- En bronce todo es texto: aqui se convierte a fecha y a numero.

select
    cast(e."Date" as date)                  as fecha,
    -- XM da el volumen como fraccion (0.75): x 100 -> porcentaje (75.0)
    try_cast(e."Value" as double) * 100     as embalses_pct,
    -- Lo que cuesta la energia en BOLSA ese dia (COP/kWh)
    try_cast(b."Value" as double)           as precio_bolsa_cop_kwh,
    -- Lo que cuesta por CONTRATO ese dia (COP/kWh)
    try_cast(c."Value" as double)           as precio_contrato_cop_kwh
from {{ source('bronce', 'xm_embalses') }} as e
-- left join: une por la fecha; si un dia falta en una tabla, queda vacio (NULL)
left join {{ source('bronce', 'xm_precio_bolsa') }} as b on e."Date" = b."Date"
left join {{ source('bronce', 'xm_precio_contrato') }} as c on e."Date" = c."Date"
