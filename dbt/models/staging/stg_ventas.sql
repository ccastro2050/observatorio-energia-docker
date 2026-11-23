-- STAGING: las ventas limpias de la capa plata, sin cambios.
-- dbt cambia source('plata', 'enerandes_ventas') por data/silver/enerandes_ventas.parquet
select *
from {{ source('plata', 'enerandes_ventas') }}
