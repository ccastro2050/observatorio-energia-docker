-- DIMENSION mes: una fila por cada mes de las ventas.
select distinct
    -- '2023-04' -> 202304: la llave
    cast(replace(periodo, '-', '') as integer)   as mes_id,
    periodo,
    cast(left(periodo, 4) as integer)            as anio,
    cast(right(periodo, 2) as integer)           as mes
from {{ ref('stg_ventas') }}
