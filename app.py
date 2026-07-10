"""
Aplicación Flask — Clasificación del Riesgo de Inundación por Parroquia
Provincia de Los Ríos, Ecuador

Sirve un mapa interactivo (Leaflet) que combina:
  - data/los_rios.geojson           -> polígonos de parroquias (INEC / ArcGIS)
  - data/predicciones_parroquias.csv -> salida del modelo (Pareja B)

El emparejamiento entre geometría y predicción se hace por
"codigo_parroquia" (campo DPA_PARROQ en el GeoJSON), tal como exige el
enunciado del proyecto (código de parroquia = método preferente).
"""

import json
import os

import pandas as pd
from flask import Flask, jsonify, render_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEOJSON_PATH = os.path.join(BASE_DIR, "data", "los_rios.geojson")
CSV_PATH = os.path.join(BASE_DIR, "data", "predicciones_parroquias.csv")

app = Flask(__name__)

# Colores por categoría de riesgo (se usan también en el frontend / leyenda)
COLOR_RIESGO = {
    "alto": "#e74c3c",
    "medio": "#f5a623",
    "bajo": "#2ecc71",
    "sin_dato": "#9aa5b1",
}


def cargar_geojson_con_predicciones():
    """
    Carga el GeoJSON de parroquias y el CSV de predicciones, y devuelve un
    único FeatureCollection con las propiedades del modelo ya incorporadas
    a cada polígono (nombre, cantón, provincia, riesgo, score, color, etc).
    """
    if not os.path.exists(GEOJSON_PATH):
        raise FileNotFoundError(
            f"No se encontró '{GEOJSON_PATH}'. Copia el archivo "
            "'los_rios.geojson' generado en el notebook (Pareja A, celda 6) "
            "dentro de la carpeta data/ de este proyecto."
        )
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"No se encontró '{CSV_PATH}'. Copia el archivo "
            "'predicciones_parroquias.csv' generado en el notebook "
            "(Pareja B, celda final) dentro de la carpeta data/ de este proyecto."
        )

    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    df_pred = pd.read_csv(CSV_PATH, dtype={"codigo_parroquia": str})
    df_pred["codigo_parroquia"] = df_pred["codigo_parroquia"].str.strip()
    pred_por_codigo = df_pred.set_index("codigo_parroquia").to_dict(orient="index")

    sin_match = []
    for feature in geojson["features"]:
        props = feature["properties"]
        # DPA_PARROQ es el código de parroquia del INEC/ArcGIS
        codigo = str(props.get("DPA_PARROQ", "")).strip()
        pred = pred_por_codigo.get(codigo)

        if pred is None:
            sin_match.append(codigo)
            props["riesgo_pred"] = "sin_dato"
            props["score"] = None
            props["prob_alto"] = None
            props["prob_medio"] = None
            props["prob_bajo"] = None
            props["color"] = COLOR_RIESGO["sin_dato"]
        else:
            props["riesgo_pred"] = pred["riesgo_pred"]
            props["score"] = pred["score"]
            props["prob_alto"] = pred["prob_alto"]
            props["prob_medio"] = pred["prob_medio"]
            props["prob_bajo"] = pred["prob_bajo"]
            props["color"] = COLOR_RIESGO.get(pred["riesgo_pred"], COLOR_RIESGO["sin_dato"])

        # Campos normalizados que usa el frontend para hover/popup
        props["nombre_parroquia"] = props.get("DPA_DESPAR", "—")
        props["canton"] = props.get("DPA_DESCAN", "—")
        props["provincia"] = props.get("DPA_DESPRO", "LOS RÍOS")

    if sin_match:
        app.logger.warning(
            "Parroquias del GeoJSON sin predicción asociada (%d): %s",
            len(sin_match), sin_match,
        )

    return geojson


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/parroquias")
def api_parroquias():
    """Devuelve el GeoJSON ya combinado con las predicciones del modelo."""
    geojson = cargar_geojson_con_predicciones()
    return jsonify(geojson)


if __name__ == "__main__":
    # Modo debug DESACTIVADO a propósito: el enunciado del proyecto prohíbe
    # ejecutar la app Flask en modo debug en producción.
    app.run(host="0.0.0.0", port=5000, debug=False)
