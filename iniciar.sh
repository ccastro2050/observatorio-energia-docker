#!/bin/sh
# Arranque del contenedor cuando corre SOLO (por ejemplo, en Render).
# En el PC, docker-compose.yml usa dos contenedores y no necesita este archivo.

# 1. El pipeline: bronce -> plata -> oro. Si XM o NOAA fallan, usa el respaldo.
#    '|| echo' = si el pipeline falla, avisa pero sigue: el aplicativo igual se prende
python -m src.pipeline || echo "El pipeline fallo: el aplicativo arranca igual (paginas 1 a 3)"

# 2. El aplicativo. Render dice en que puerto escuchar con la variable PORT;
#    en el PC no existe PORT, y se usa 8501.
#    exec: Streamlit reemplaza a este script (asi Render lo puede apagar bien)
exec streamlit run app/inicio.py \
    --server.port "${PORT:-8501}" \
    --server.address 0.0.0.0 \
    --server.headless true
