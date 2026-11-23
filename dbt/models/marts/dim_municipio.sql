-- DIMENSION municipio: una fila por municipio, con su codigo DIVIPOLA.
select distinct
    municipio_id,
    municipio
from {{ ref('stg_ventas') }}
