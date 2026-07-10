# Riesgo de Inundación por Parroquia — Provincia de Los Ríos

Aplicación web (Flask + Leaflet) que muestra un mapa interactivo con la categoría de riesgo de inundación estimada por un modelo de Machine Learning para cada parroquia de la provincia de Los Ríos, Ecuador.

Proyecto del Segundo Parcial — Ciencia de Datos e Inteligencia Artificial.

URL pública: https://andresvl.pythonanywhere.com/

## Estructura

Proyecto2P_RiesgoInundacion_LosRios/
├── app.py                              # Backend Flask
├── wsgi.py                             # Punto de entrada WSGI (despliegue)
├── requirements.txt
├── Procfile
├── .gitignore
├── data/
│   ├── los_rios.geojson                # Polígonos de las parroquias
│   └── predicciones_parroquias.csv     # Predicciones del modelo
├── templates/
│   └── index.html                      # Mapa Leaflet
├── static/
└── Notebook/
    ├── Proyecto_LosRios_FINALII_(1).ipynb   # Notebook con el análisis y entrenamiento del modelo
    └── Informe y Presentacion/              # Informe y presentación del proyecto

## Cómo funciona

`app.py` combina el GeoJSON con el CSV de predicciones, emparejando por código de parroquia (DPA_PARROQ - codigo_parroquia).

El mapa muestra, al pasar el cursor, el nombre/cantón/provincia, y al hacer clic, la categoría de riesgo y el score del modelo.

Las predicciones se generaron con **Regresión Logística**, el modelo con mejor Recall (0.77) entre los cuatro evaluados (ver notebook e informe del proyecto en `Notebook/`). `app.py` solo lee el CSV ya calculado, no ejecuta el modelo en cada petición.

## Ejecutar en local

```bash
pip install -r requirements.txt
python app.py
```

Abrir http://127.0.0.1:5000.

## Despliegue

Alojado en PythonAnywhere. El backend está en Flask y las visualizaciones geográficas en Leaflet, cargando `los_rios.geojson` y `predicciones_parroquias.csv` desde la carpeta `data/`.
