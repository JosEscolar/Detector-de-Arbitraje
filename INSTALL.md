# FlipRadar — Guía de instalación paso a paso

Tiempo estimado: **30-45 minutos**. No necesitas saber programar.

---

## PASO 1 — Crear cuenta en GitHub (5 min)

1. Ve a **https://github.com** y haz clic en "Sign up"
2. Elige un nombre de usuario, correo y contraseña
3. Completa la verificación y confirma tu email

---

## PASO 2 — Crear tu repositorio en GitHub (5 min)

1. Una vez dentro de GitHub, haz clic en el botón verde **"New"** (arriba a la izquierda)
2. En "Repository name" escribe: `flipradar`
3. Asegúrate de que esté marcado como **Public** (necesario para GitHub Pages gratis)
4. Marca la casilla **"Add a README file"**
5. Haz clic en **"Create repository"**

---

## PASO 3 — Subir los archivos del proyecto (10 min)

Necesitas subir estos 4 archivos/carpetas a tu repositorio:

### Opción A — Subida manual (recomendada para principiantes)

1. En tu repositorio, haz clic en **"Add file" → "Upload files"**
2. Sube estos archivos de uno en uno:
   - `index.html`
   - `scraper.py`
3. Para la carpeta `.github/workflows/scrape.yml`:
   - Haz clic en **"Add file" → "Create new file"**
   - En el nombre escribe exactamente: `.github/workflows/scrape.yml`
   - Copia y pega el contenido del archivo `scrape.yml`
   - Haz clic en **"Commit changes"**
4. Crea el archivo de datos inicial:
   - Haz clic en **"Add file" → "Create new file"**
   - Nombre: `data/opportunities.json`
   - Contenido: `{"lastUpdated":"2025-01-01T00:00:00","totalFound":0,"newCount":0,"minProfitPct":30,"opportunities":[]}`
   - Haz clic en **"Commit changes"**

---

## PASO 4 — Obtener credenciales de eBay (10 min)

1. Ve a **https://developer.ebay.com** y haz clic en **"Register"**
2. Crea una cuenta de desarrollador (es gratis)
3. Una vez dentro, ve a **"My Account" → "Application Keys"**
4. Haz clic en **"Create an App Key Set"**
5. Pon cualquier nombre (por ejemplo: "flipradar")
6. Elige **"Production"** (no Sandbox)
7. Copia el **"App ID (Client ID)"** — lo necesitarás en el paso 5
8. Haz clic en **"Get a Token"** y copia también el **"Client Secret"**

> Si te pide verificar una aplicación, selecciona "Personal use" y acepta los términos.

---

## PASO 5 — Configurar las credenciales en GitHub (5 min)

Los datos sensibles (contraseñas, claves) se guardan como "Secrets" en GitHub,
no en el código. Así nadie puede verlos.

1. En tu repositorio de GitHub, haz clic en **"Settings"** (pestaña superior)
2. En el menú izquierdo, haz clic en **"Secrets and variables" → "Actions"**
3. Haz clic en **"New repository secret"** y añade estos uno a uno:

| Nombre del Secret   | Valor                                      |
|---------------------|--------------------------------------------|
| `EBAY_CLIENT_ID`    | El App ID que copiaste de eBay             |
| `EBAY_CLIENT_SECRET`| El Client Secret que copiaste de eBay      |
| `GMAIL_USER`        | Tu dirección de Gmail (p.ej. tu@gmail.com) |
| `GMAIL_APP_PASSWORD`| La contraseña de aplicación de Gmail (ver abajo) |
| `ALERT_EMAIL`       | El email donde quieres recibir alertas     |
| `MIN_PROFIT_PCT`    | El porcentaje mínimo de ganancia (ej: 30)  |

### Cómo obtener la contraseña de aplicación de Gmail:

1. Ve a **https://myaccount.google.com/security**
2. Activa la **verificación en dos pasos** si no la tienes
3. Busca **"Contraseñas de aplicaciones"** (puede estar en "Cómo inicias sesión en Google")
4. Selecciona "Correo" y "Ordenador Windows"
5. Haz clic en **"Generar"** — copia la contraseña de 16 caracteres que aparece
6. Esa contraseña es tu `GMAIL_APP_PASSWORD`

---

## PASO 6 — Activar GitHub Pages (tu web gratis) (3 min)

1. En tu repositorio, ve a **"Settings"**
2. En el menú izquierdo, haz clic en **"Pages"**
3. En "Source" selecciona **"Deploy from a branch"**
4. En "Branch" selecciona **"main"** y la carpeta **"/ (root)"**
5. Haz clic en **"Save"**
6. Espera 2-3 minutos y tu web estará en: `https://TU_USUARIO.github.io/flipradar`

---

## PASO 7 — Ejecutar el primer rastreo (2 min)

El rastreo automático se ejecutará cada hora, pero puedes lanzarlo ahora mismo:

1. En tu repositorio, haz clic en la pestaña **"Actions"**
2. Verás "FlipRadar — Rastreo automático" en la lista
3. Haz clic en él y luego en **"Run workflow" → "Run workflow"**
4. Espera 1-2 minutos mientras trabaja
5. Si aparece una palomita verde ✅, todo fue bien
6. Ve a tu web y verás las primeras oportunidades

---

## ¿Algo salió mal?

- **El workflow falla (X roja):** Haz clic en el fallo para ver el error.
  El más común es credenciales mal copiadas en los Secrets.
- **La web carga pero no hay oportunidades:** Espera al menos una ejecución
  exitosa del workflow.
- **No llegan emails:** Comprueba que la contraseña de aplicación de Gmail
  sea correcta y que la verificación en dos pasos esté activa.

---

## Personalizar el rastreo

Para añadir o quitar productos que rastrea, edita el archivo `scraper.py`
en GitHub (haz clic en el archivo → icono del lápiz) y modifica la lista
`SEARCH_TERMS` al principio del archivo.

---

*FlipRadar — Los precios de compra son estimaciones. Verifica siempre antes de comprar.*
