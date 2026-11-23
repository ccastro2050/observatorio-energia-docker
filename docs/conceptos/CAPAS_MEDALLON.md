# Las capas: bronce, plata y oro

> **En una frase:** los datos pasan por **tres capas**, y cada una tiene **una sola tarea**: traer, limpiar, modelar.

| Capa | Pregunta que responde | Regla de oro | Ejemplo en este proyecto |
|---|---|---|---|
| 🥉 **Bronce** | ¿Qué llegó? | Guardar **tal cual**, sin corregir nada | `Municipio = 'MEDELLIN'`, `'Medellín D.E.'`, `'medellin'`: los tres, como vinieron |
| 🥈 **Plata** | ¿Qué es correcto? | Corregir con **reglas**; descartar lo que no se puede arreglar | Los tres se vuelven `Medellín` con código `05001` |
| 🥇 **Oro** | ¿Qué necesita el negocio? | Tablas **listas para analizar** y **probadas** | `fact_ventas` con `municipio_id = 05001`, unida a `dim_municipio` |

## ¿Por qué no limpiar de una vez?

| Si se limpia al traer | Con capas |
|---|---|
| Si una regla estaba mal, el dato original **se perdió** | Bronce lo guarda: se corrige la regla y se vuelve a correr plata |
| No se sabe qué cambió | Se compara bronce con plata (página *Explorar capas*) |
| Un error de la API daña todo | Cada capa se puede repetir sola |

> Este patrón se llama **arquitectura medallón** (por las medallas de bronce, plata y oro).
