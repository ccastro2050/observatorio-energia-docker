# El pipeline

> **En una frase:** un **pipeline** (tubería) es un programa que ejecuta los pasos del dato **en orden y sin intervención**: traer → limpiar → modelar.

```text
python -m src.pipeline
   1. BRONCE   src/bronce/extraer.py    XM, NOAA y el Excel  ->  data/bronze/
   2. PLATA    src/plata/limpiar.py     reglas de limpieza    ->  data/silver/
   3. ORO      src/oro/construir.py     dbt build + exportar  ->  data/gold/
```

| Concepto | Qué es | Dónde está |
|---|---|---|
| **Extraer** (E) | Traer los datos de la fuente | `extraer.py` |
| **Transformar** (T) | Limpiar y modelar | `limpiar.py` y dbt |
| **Cargar** (L) | Guardar donde se va a usar | `data/gold/` |
| **Reintentos** | Si la API no responde, esperar y volver a pedir (2, 4, 8 segundos) | `utils.py` · `pedir()` |
| **Ventanas** | Pedir el año en pedazos de 30 días, porque XM no acepta más | `utils.py` · `ventanas()` |
| **Respaldo** | Si una API falla, usar la copia de `data/ejemplo/` | `extraer.py` · `usar_respaldo()` |

## Pipeline o aplicativo: las dos formas de correrlo

| Forma | Cuándo |
|---|---|
| `python -m src.pipeline` (o el contenedor `pipeline`) | Automático: todo de una vez, sin clics |
| Páginas 1, 2 y 3 del aplicativo | Paso a paso, para **ver** qué hace cada capa, cambiar fechas o subir otro Excel |

Las dos usan **las mismas funciones**: el aplicativo no repite código, solo pone botones encima.
