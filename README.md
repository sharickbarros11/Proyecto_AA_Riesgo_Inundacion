# Riesgo de Inundación por Parroquia — Provincia de Los Ríos

Aplicación web (Flask + Leaflet) que muestra un mapa interactivo con la
categoría de riesgo de inundación estimada por el modelo de Machine Learning
para cada parroquia de la provincia de Los Ríos, Ecuador.

Proyecto del Segundo Parcial — Ciencia de Datos e Inteligencia Artificial.

## Estructura del proyecto

```
floodapp/
├── app.py                     # Backend Flask
├── requirements.txt
├── wsgi.py                    # Punto de entrada para PythonAnywhere
├── data/
│   ├── los_rios.geojson           # ⚠️ debes copiarlo desde tu notebook (Pareja A)
│   └── predicciones_parroquias.csv  # ya incluido (salida real de la Pareja B)
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/map.js
```

## 1. Antes de correr nada: copia el GeoJSON

El notebook (Pareja A, celda 6) genera el archivo `los_rios.geojson` con los
polígonos de las 30 parroquias. Ese archivo se guarda dentro de la sesión de
Colab, así que tienes que descargarlo manualmente:

1. En Colab, abre el panel de archivos (ícono de carpeta, a la izquierda).
2. Busca `los_rios.geojson` (se genera al correr la celda 6).
3. Clic derecho → **Descargar**.
4. Copia el archivo descargado dentro de `floodapp/data/los_rios.geojson`.

> Si ya regeneraste `predicciones_parroquias.csv` con resultados nuevos del
> notebook corregido, reemplaza también `floodapp/data/predicciones_parroquias.csv`
> por esa versión (el que está incluido en este proyecto ya es el real, generado
> después de corregir el data leakage).

## 2. Ejecutar en local

```bash
cd floodapp
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abre `http://127.0.0.1:5000` en el navegador. Deberías ver el mapa con las
30 parroquias coloreadas por nivel de riesgo.

**Si ves un error `FileNotFoundError`:** significa que falta `los_rios.geojson`
o `predicciones_parroquias.csv` dentro de `data/` — revisa el paso 1.

## 3. Despliegue en PythonAnywhere (recomendado por el enunciado)

1. Crea una cuenta gratuita en https://www.pythonanywhere.com
2. Ve a la pestaña **Files** y sube la carpeta `floodapp` completa (puedes
   subir un .zip y luego descomprimirlo con una consola Bash desde la pestaña
   **Consoles**: `unzip floodapp.zip`).
3. Abre una consola **Bash** y crea un entorno virtual:
   ```bash
   cd floodapp
   mkvirtualenv --python=python3.10 floodapp-env
   pip install -r requirements.txt
   ```
4. Ve a la pestaña **Web** → **Add a new web app** → elige **Manual configuration**
   (no "Flask", para tener control total) → Python 3.10.
5. En **Virtualenv**, pon la ruta del entorno que creaste, por ejemplo:
   `/home/tu_usuario/.virtualenvs/floodapp-env`
6. En **Code → WSGI configuration file**, abre el archivo que te da PythonAnywhere
   y reemplaza su contenido por esto (ajusta la ruta a tu usuario):
   ```python
   import sys
   path = '/home/tu_usuario/floodapp'
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import app as application
   ```
7. En **Code → Source code / Working directory**, apunta ambos a
   `/home/tu_usuario/floodapp`.
8. Clic en **Reload**. Tu app queda pública en `https://tu_usuario.pythonanywhere.com`.

> El enunciado prohíbe correr en modo debug — `app.py` ya tiene `debug=False`,
> y PythonAnywhere de por sí no usa el modo debug de Flask en producción.

## 4. Alternativa: Render o Railway

Ambos detectan automáticamente `requirements.txt`. Solo necesitas definir el
comando de arranque (Start Command):

```
gunicorn app:app
```

Sube el repositorio a GitHub primero (ver sección siguiente) y conecta ese
repo desde el panel de Render/Railway. Asegúrate de que `data/los_rios.geojson`
y `data/predicciones_parroquias.csv` estén incluidos en el repositorio (no los
excluyas en `.gitignore`).

## 5. Repositorio GitHub (entregable obligatorio)

```bash
cd floodapp
git init
git add .
git commit -m "App Flask - riesgo de inundación Los Ríos"
git branch -M main
git remote add origin https://github.com/landavereaandres-alt/TU_REPO.git
git push -u origin main
```

Recuerda que el enunciado exige que el repo incluya: código Flask,
`requirements.txt` y este `README.md` — los tres ya están aquí.

## Cómo funciona el emparejamiento geometría ↔ predicción

`app.py` une los dos archivos por **código de parroquia**
(`DPA_PARROQ` en el GeoJSON ↔ `codigo_parroquia` en el CSV), que es el método
preferente según el enunciado. Si alguna parroquia del GeoJSON no encuentra
predicción asociada, se pinta en gris ("sin dato") y se registra una
advertencia en el log del servidor — así nunca falla la app, pero queda
documentado el problema.

## Funcionalidades del mapa

- **Hover** sobre una parroquia → nombre, cantón y provincia.
- **Clic** sobre una parroquia → categoría de riesgo y probabilidades del
  modelo (alto/medio/bajo), además del score de confianza.
- **Leyenda** fija con los 4 colores (alto / medio / bajo / sin dato).
- Estilos y colores diferenciados por nivel de riesgo en cada polígono.
