// Mapa interactivo de riesgo de inundación — Provincia de Los Ríos
// Consume /api/parroquias (GeoJSON ya combinado con las predicciones del modelo)

const COLOR_RIESGO = {
  alto: "#e74c3c",
  medio: "#f5a623",
  bajo: "#2ecc71",
  sin_dato: "#9aa5b1",
};

const ETIQUETA_RIESGO = {
  alto: "Riesgo alto",
  medio: "Riesgo medio",
  bajo: "Riesgo bajo",
  sin_dato: "Sin dato",
};

const map = L.map("map", {
  zoomControl: true,
  attributionControl: true,
}).setView([-1.35, -79.45], 9);

L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
  attribution: '&copy; OpenStreetMap, &copy; CARTO',
  maxZoom: 18,
}).addTo(map);

function estiloParroquia(feature) {
  const riesgo = feature.properties.riesgo_pred || "sin_dato";
  return {
    fillColor: COLOR_RIESGO[riesgo] || COLOR_RIESGO.sin_dato,
    fillOpacity: 0.65,
    color: "#0e1b2b",
    weight: 1,
  };
}

function resaltar(e) {
  const layer = e.target;
  layer.setStyle({ weight: 2.5, fillOpacity: 0.8 });
  layer.bringToFront();
}

function quitarResaltado(layer) {
  return function (e) {
    layer.resetStyle(e.target);
  };
}

function formatoPct(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return (v * 100).toFixed(0) + "%";
}

function mostrarPanelSeleccion(props) {
  const panel = document.getElementById("info-parroquia");
  const riesgo = props.riesgo_pred || "sin_dato";

  document.getElementById("sel-nombre").textContent = props.nombre_parroquia;
  document.getElementById("sel-canton").textContent =
    `Cantón ${props.canton} · ${props.provincia}`;

  const badge = document.getElementById("sel-badge");
  badge.textContent = ETIQUETA_RIESGO[riesgo];
  badge.className = "badge badge--" + riesgo;

  document.getElementById("sel-score").textContent =
    props.score != null ? `Confianza del modelo: ${formatoPct(props.score)}` : "";

  panel.hidden = false;
}

function popupHTML(props) {
  const riesgo = props.riesgo_pred || "sin_dato";
  return `
    <div class="popup-riesgo">
      <h3>${props.nombre_parroquia}</h3>
      <span class="badge badge--${riesgo}">${ETIQUETA_RIESGO[riesgo]}</span>
      <table>
        <tr><td>Prob. alto</td><td>${formatoPct(props.prob_alto)}</td></tr>
        <tr><td>Prob. medio</td><td>${formatoPct(props.prob_medio)}</td></tr>
        <tr><td>Prob. bajo</td><td>${formatoPct(props.prob_bajo)}</td></tr>
      </table>
    </div>
  `;
}

let capaParroquias;

function onEachFeature(feature, layer) {
  const props = feature.properties;

  // Hover -> tooltip con nombre, cantón y provincia (requisito del proyecto)
  layer.bindTooltip(
    `<strong>${props.nombre_parroquia}</strong><br>Cantón: ${props.canton}<br>Provincia: ${props.provincia}`,
    { sticky: true, className: "leaflet-tooltip-parroquia" }
  );

  // Click -> popup con categoría de riesgo + score del modelo (requisito del proyecto)
  layer.bindPopup(popupHTML(props));

  layer.on({
    mouseover: resaltar,
    mouseout: quitarResaltado(capaParroquias),
    click: (e) => mostrarPanelSeleccion(e.target.feature.properties),
  });
}

fetch("/api/parroquias")
  .then((res) => {
    if (!res.ok) throw new Error("No se pudo cargar /api/parroquias");
    return res.json();
  })
  .then((geojson) => {
    capaParroquias = L.geoJSON(geojson, {
      style: estiloParroquia,
      onEachFeature: onEachFeature,
    }).addTo(map);

    map.fitBounds(capaParroquias.getBounds(), { padding: [16, 16] });

    document.getElementById("contador-parroquias").textContent =
      `${geojson.features.length} parroquias`;
  })
  .catch((err) => {
    console.error(err);
    document.getElementById("map").innerHTML =
      '<p style="padding:24px;font-family:sans-serif;color:#900">' +
      "No se pudieron cargar los datos del mapa. Revisa que " +
      "data/los_rios.geojson y data/predicciones_parroquias.csv existan " +
      "en el servidor.</p>";
  });
