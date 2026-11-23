-- HECHOS de ventas: un mes, un municipio, un segmento y un tipo de compra.
select
    cast(replace(periodo, '-', '') as integer)   as mes_id,       -- llave a dim_mes
    municipio_id,                                                 -- llave a dim_municipio
    segmento,                                                     -- Residencial, Comercial, Industrial
    tipo_compra,                                                  -- Bolsa o Contrato
    -- Las MEDIDAS: los numeros que se suman
    energia_kwh,
    valor_cop,
    clientes
from {{ ref('stg_ventas') }}
