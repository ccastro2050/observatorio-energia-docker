"""
Pruebas del proceso: la limpieza de la capa plata y los calculos del dashboard (app/datos.py).
    pytest -v
Usan tablas pequenas inventadas: no necesitan internet ni la capa oro.
"""
# sys y Path: para que pytest encuentre la carpeta dashboard/
import sys
from pathlib import Path

# pandas: para armar las tablas de prueba
import pandas as pd

# Agrega la carpeta app/ a la lista donde Python busca los import (para importar datos.py)
# La raiz del proyecto (para importar src/) y la carpeta app/ (para importar datos.py)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

# Lo que se prueba
from datos import costos_de_compra, precio_por_fase          # noqa: E402
from src.plata.limpiar import limpiar, normalizar            # noqa: E402


# Cada funcion que empieza con 'test_' es una prueba que pytest encuentra y ejecuta solo
def test_normalizar_quita_tildes_y_espacios():
    # assert: si la condicion es falsa, la prueba falla
    assert normalizar("  Medellín ") == "medellin"


# Prueba: la limpieza corrige los nombres y descarta las filas malas
def test_limpiar_corrige_y_descarta():
    # Una tabla pequena inventada, con errores como los del Excel real
    bronce = pd.DataFrame({
        "Fecha": ["2023-01", "2023-01", "2023-02", "TOTAL"],
        "Municipio": ["MEDELLIN", "Rio Negro", "Bello", None],
        "Segmento": ["RESID.", "IND", "Comercial", None],
        "Tipo_Compra": ["bolsa", "CONTRATOS", "Bolsa", None],
        "Energia_kWh": ["100", "200", "-5", None],      # la tercera es negativa
        "Valor_COP": ["1000", "2000", "50", None],
        "Clientes": ["1", "2", "3", None],
    })
    # Se aplica la limpieza
    plata = limpiar(bronce)
    # Se quitan la fila TOTAL y la de energia negativa: quedan 2
    assert len(plata) == 2
    # Los municipios quedaron con su codigo DIVIPOLA (Medellin y Rionegro)
    assert list(plata["municipio_id"]) == ["05001", "05615"]
    # Los segmentos y tipos de compra quedaron estandar
    assert list(plata["segmento"]) == ["Residencial", "Industrial"]
    assert list(plata["tipo_compra"]) == ["Bolsa", "Contrato"]


# Prueba: el calculo de costos en bolsa y por contrato
def test_costos_de_compra():
    # Una venta de 1.000 kWh en enero de 2023
    ventas = pd.DataFrame({"mes_id": [202301], "energia_kwh": [1000.0]})
    # Los precios de ese mes: bolsa 500 y contrato 300
    mercado = pd.DataFrame({"mes_id": [202301], "precio_bolsa_cop_kwh": [500.0],
                            "precio_contrato_cop_kwh": [300.0]})
    # iloc[0]: toma la primera (y unica) fila del resultado
    fila = costos_de_compra(ventas, mercado).iloc[0]
    # 1.000 kWh x 500 = 500.000; x 300 = 300.000; diferencia 200.000
    assert fila["costo_bolsa"] == 500_000
    assert fila["costo_contrato"] == 300_000
    assert fila["sobrecosto"] == 200_000


# Prueba: el precio promedio por fase de El Nino
def test_precio_por_fase():
    # Dos meses de El Nino (800 y 1000) y uno Neutral (400)
    mercado = pd.DataFrame({"fase_enso": ["El Niño", "El Niño", "Neutral"],
                            "precio_bolsa_cop_kwh": [800.0, 1000.0, 400.0]})
    # set_index: usa la fase como indice para buscar el precio por su nombre
    resultado = precio_por_fase(mercado).set_index("fase_enso")["precio_bolsa_cop_kwh"]
    # El promedio de 800 y 1000 es 900
    assert resultado["El Niño"] == 900
    assert resultado["Neutral"] == 400


# Prueba: un Excel sin las columnas correctas se rechaza con un mensaje claro
def test_excel_subido_sin_columnas_se_rechaza():
    # io.BytesIO: un "archivo" en memoria, como el que entrega st.file_uploader
    import io

    import pytest

    from src.bronce.extraer import guardar_excel_subido
    # Un Excel con una sola columna que no sirve
    archivo = io.BytesIO()
    pd.DataFrame({"otra": [1]}).to_excel(archivo, index=False)
    # Debe lanzar ValueError diciendo que faltan columnas
    with pytest.raises(ValueError, match="faltan estas columnas"):
        guardar_excel_subido(io.BytesIO(archivo.getvalue()))
