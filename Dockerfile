# La IMAGEN del proyecto: un Linux pequeno con Python y las librerias.
# La usan los dos contenedores (pipeline y dashboard); cada uno corre un comando distinto.

# Punto de partida: Python 3.13 en su version liviana (slim)
FROM python:3.13-slim

# Dentro del contenedor, todo vive en /app
WORKDIR /app

# Primero solo requirements.txt: si no cambia, Docker reutiliza esta capa y no reinstala
COPY requirements.txt .
# Instalar las librerias. --no-cache-dir: no guardar copias, la imagen pesa menos
RUN pip install --no-cache-dir -r requirements.txt

# Luego el resto del codigo del proyecto
COPY . .
# Por si el script llego con finales de linea de Windows (\r): se los quita
RUN sed -i 's/\r$//' iniciar.sh

# Streamlit escucha en el puerto 8501 (en Render, en el que diga la variable PORT)
EXPOSE 8501

# Lo que corre si el contenedor arranca SOLO (Render): el pipeline y luego el aplicativo.
# En el PC, docker-compose.yml cambia este comando en cada contenedor.
CMD ["sh", "iniciar.sh"]
