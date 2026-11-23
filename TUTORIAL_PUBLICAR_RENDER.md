# Tutorial: publicar el aplicativo en Render

> **Qué se logra.** Que el aplicativo quede en internet, en una dirección como
> `https://observatorio-energia.onrender.com`, para mostrarlo desde cualquier computador o celular.
>
> **Qué se necesita:** el repositorio en GitHub (público) y una cuenta gratuita en Render.
> No se instala nada: **Render construye la imagen con el mismo `Dockerfile`** del proyecto.

---

## 0. Cómo arranca el proyecto en Render (antes de empezar)

En el PC hay **dos** contenedores (`pipeline` y `app`). Render corre **uno solo**. Por eso el `Dockerfile` termina con:

```dockerfile
CMD ["sh", "iniciar.sh"]
```

y `iniciar.sh` hace las dos cosas, en orden:

| Paso | Comando | Qué hace |
|---|---|---|
| 1 | `python -m src.pipeline` | Bronce → plata → oro. Si XM o NOAA no responden desde los servidores de Render, usa el **respaldo** de `data/ejemplo/` |
| 2 | `streamlit run app/inicio.py --server.port "${PORT:-8501}"` | Prende el aplicativo **en el puerto que Render diga** (variable `PORT`); en el PC, 8501 |

> **Nada de esto hay que cambiarlo.** Ya está en el repositorio: el mismo código corre en el PC y en Render.

---

## 1. Crear la cuenta en Render

1. Abran una **ventana de incógnito** (o InPrivate) y entren a **https://render.com**.
2. Clic en **Get Started** (o **Sign Up**) y regístrense con su correo o con **GitHub**.

> **¿Por qué incógnito?** Si el navegador tiene abierta otra cuenta de GitHub o de Render, Render se conecta con esa y no con la suya.
>
> ⚠️ **Si ya tuvo una cuenta de Render** con un pago pendiente o un servicio suspendido, cree una **cuenta nueva** con otro correo: la cuenta vieja no deja publicar (*Workspace suspended*).

---

## 2. Crear el servicio web

1. Arriba a la derecha: **+ New** → **Web Service**.
2. Elijan la pestaña **Public Git Repository** y peguen la dirección del repositorio:

```text
https://github.com/ccastro2050/observatorio-energia-docker
```

3. Clic en **Connect**.

| Opción | Cuándo usarla |
|---|---|
| **Public Git Repository** | ✅ La de este tutorial: el repositorio es público y Render lo clona sin pedir permisos |
| **Git Provider** | Si conectan su cuenta de GitHub: Render vuelve a publicar solo con cada `git push` |

---

## 3. Llenar el formulario

Render **detecta `Docker` solo**, porque encuentra el `Dockerfile` en la raíz.

| Campo | Qué poner | Por qué |
|---|---|---|
| **Name** | `observatorio-energia` (o el nombre de su equipo) | Queda en la dirección: `observatorio-energia.onrender.com`. Si ya existe, Render le agrega letras |
| **Language** | `Docker` (ya viene elegido) | Render va a usar el `Dockerfile` |
| **Branch** | `main` | La rama que se publica |
| **Region** | `Oregon (US West)` o la que salga | Cualquiera sirve |
| **Root Directory** | **Vacío** | El `Dockerfile` está en la raíz del repositorio |
| **Instance Type** | **Free** | 0 dólares. Ver las limitaciones en el paso 6 |

No hay que agregar variables de entorno: el proyecto no usa claves ni bases de datos externas.

Clic en **Deploy Web Service**.

---

## 4. Ver cómo se construye (los *logs*)

Render clona el repositorio, construye la imagen y la arranca. El registro va saliendo en pantalla; tarda de **3 a 6 minutos** la primera vez.

| Lo que aparece en el registro | Qué significa |
|---|---|
| `#... RUN pip install --no-cache-dir -r requirements.txt` | Instalando pandas, dbt, Streamlit... (lo más lento) |
| `==> Deploying...` | La imagen quedó lista; ahora la arranca |
| `=== PIPELINE: bronce -> plata -> oro ===` | Corre `iniciar.sh`: el pipeline |
| `! XM no respondio (...). Se usa el respaldo.` | **Normal en Render**: XM a veces no responde fuera de Colombia. Usa `data/ejemplo/` y sigue |
| `Done. PASS=17 WARN=0 ERROR=0` | dbt armó el modelo estrella y pasaron las 10 pruebas |
| `You can now view your Streamlit app in your browser.` | El aplicativo arrancó |
| `==> Your service is live 🎉` | **Listo** |
| `==> Available at your primary URL https://observatorio-energia.onrender.com` | La dirección pública |

---

## 5. Abrir el aplicativo

Clic en la dirección de arriba a la izquierda (`https://....onrender.com`). Debe abrir el **Dashboard**, con el menú de las 5 páginas a la izquierda.

---

## 6. Lo que hay que saber del plan gratuito

| Limitación | Qué pasa | Qué hacer |
|---|---|---|
| **Se duerme** a los 15 minutos sin visitas | La siguiente visita tarda **1 a 2 minutos** en despertar (corre otra vez el pipeline) | Abrirlo unos minutos antes de presentar |
| **El disco no es permanente** | Lo que se cargue o limpie desde las páginas 1 a 3 **se pierde** cuando se duerme o se vuelve a publicar | Es solo para mostrar. El trabajo real se hace en el PC |
| **512 MB de memoria** | Alcanza para este proyecto | Si sale `Out of memory`, no carguen rangos de fechas muy largos desde la página 1 |
| **750 horas al mes** | Alcanza para un servicio prendido todo el mes | — |

---

## 7. Publicar una versión nueva

1. En el PC: `git add .` · `git commit -m "..."` · `git push`.
2. En Render, en el servicio: **Manual Deploy** → **Deploy latest commit**.

> Con **Public Git Repository**, Render **no** se entera solo de los `push`: hay que darle **Manual Deploy**. Con **Git Provider** sí publica solo.

---

## 8. Si algo falla

| Si sale | Por qué | Qué hacer |
|---|---|---|
| `sh: iniciar.sh: not found` o `$'\r': command not found` | El script quedó con finales de línea de Windows | Ya está resuelto con `.gitattributes` y el `sed` del `Dockerfile`. Si pasa, revisen que esos dos archivos estén en el repositorio |
| `No open ports detected` | Streamlit no escuchó en el puerto de Render | Revisen que `iniciar.sh` use `--server.port "${PORT:-8501}"` |
| `dbt build fallo` | Una prueba de calidad no pasó | Lean el mensaje de dbt en el registro: dice qué prueba y qué tabla |
| La página dice *"Todavía no hay capa oro"* | El pipeline falló al arrancar | Corran las páginas 1, 2 y 3 desde el aplicativo, o revisen el registro |
| `Workspace suspended` | La cuenta de Render tiene un problema de pago | Cuenta nueva, con otro correo (paso 1) |
