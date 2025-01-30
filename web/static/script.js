// Initialize map
const map = L.map('map', {
  'center': [23.51, 80.33],
  'zoom': 5,
  'layers': [
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      'attribution': 'Map data &copy; OpenStreetMap contributors'
    })
  ]
});

const home = {
  lat: 23.51,
  lng: 80.33,
  zoom: 5
};

// Add home button
L.easyButton('<img src="../assets/512.png" style="width:16px">', function(btn, map) {
  map.setView([home.lat, home.lng], home.zoom);
}, 'Zoom To Home').addTo(map);

// Initialize geocoder
const geocoder = L.Control.geocoder({
  position: 'topleft',
  defaultMarkGeocode: false
})
.on('markgeocode', (e) => {
  const bbox = e.geocode.bbox;
  const poly = L.polygon([
    bbox.getSouthEast(),
    bbox.getNorthEast(),
    bbox.getNorthWest(),
    bbox.getSouthWest()
  ]);
  map.fitBounds(poly.getBounds());
})
.addTo(map);

// Initialize layer controls
const controlLayers = L.control.layers(null, null, {collapsed: false}).addTo(map);

// GeoJSON files
const geoJsonFiles = {
  'Chattri': { color: 'orange', label: 'WH Orange' },
  'bihar': { color: 'red', label: 'WH Red' },
  'harjana': { color: 'blue', label: 'WH Blue' },
  'Andhra': { color: 'yellow', label: 'WH Yellow' },
  'karna': { color: 'pink', label: 'WH Pink' },
  'kerala': { color: 'green', label: 'WH Green' },
  'Madhya': { color: 'purple', label: 'WH Purple' },
  'telangana': { color: 'black', label: 'WH Black' }
};

// Load GeoJSON layers
Object.entries(geoJsonFiles).forEach(([name, config]) => {
  $.getJSON(`json/${name}.json`, function(geojson) {
    const geojsonLayer = L.geoJson(geojson, {
      style: function(feature) {
        return {
          'weight': 0,
          'fillColor': config.color,
          'fillOpacity': 0.40
        };
      }
    });
    controlLayers.addOverlay(geojsonLayer, config.label);
  });
});

// Initialize editable layers
const editableLayers = new L.FeatureGroup();
map.addLayer(editableLayers);

// Drawing controls
const drawControl = new L.Control.Draw({
  position: 'topright',
  draw: {
    polyline: false,
    polygon: {
      allowIntersection: false,
      drawError: {
        color: '#e1e100',
        message: '<strong>Oh snap!</strong> you can\'t draw that!'
      }
    },
    circle: false,
    rectangle: true,
    marker: false
  },
  edit: {
    featureGroup: editableLayers,
    remove: true
  }
});

map.addControl(drawControl);

// Drawing event handlers
map.on(L.Draw.Event.CREATED, function(e) {
  const layer = e.layer;
  
  if (e.layerType === 'marker') {
    layer.bindPopup(`LatLng: ${layer.getLatLng().lat},${layer.getLatLng().lng}`).openPopup();
  }

  editableLayers.addLayer(layer);
  const layerGeoJSON = editableLayers.toGeoJSON();

  const wkt_options = {};
  const geojson_format = new OpenLayers.Format.GeoJSON();
  const testFeature = geojson_format.read(layerGeoJSON);
  const wkt = new OpenLayers.Format.WKT(wkt_options);
  const out = wkt.write(testFeature);

  alert("WKT FORMAT\r\n" + out);
});

map.on(L.Draw.Event.EDITED, function(e) {
  const layerGeoJSON = editableLayers.toGeoJSON();
  const wkt_options = {};
  const geojson_format = new OpenLayers.Format.GeoJSON();
  const testFeature = geojson_format.read(layerGeoJSON);
  const wkt = new OpenLayers.Format.WKT(wkt_options);
  const out = wkt.write(testFeature);

  alert("WKT FORMAT\r\n" + out);
});

map.on(L.Draw.Event.DELETED, function(e) {
  const layerGeoJSON = editableLayers.toGeoJSON();
  const wkt_options = {};
  const geojson_format = new OpenLayers.Format.GeoJSON();
  const testFeature = geojson_format.read(layerGeoJSON);
  const wkt = new OpenLayers.Format.WKT(wkt_options);
});

// Add base maps
const osm = L.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png");
const googleSat = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
});

const baseMaps = {
  "OpenStreetMap": osm,
  "Satellite": googleSat
};

L.control.layers(baseMaps, {}, {position: 'bottomleft'}).addTo(map);

// Search functionality
// ... inside script.js

async function handleSearch(event) {
  event.preventDefault();

  const startDate = document.getElementById('start-date').value;
  const endDate = document.getElementById('end-date').value;
  const latitude = document.getElementById('latitude').value;
  const longitude = document.getElementById('longitude').value;

  const searchStatus = document.getElementById('search-status');
  const form = document.getElementById('search-form');

  // Show loading spinner
  searchStatus.style.display = 'block';
  form.querySelector('button').disabled = true;

  try {
    const response = await fetch('http://localhost:63342/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        start_date: startDate,
        end_date: endDate,
        coordinates: `POINT(${longitude} ${latitude})`
      })
    });

    const result = await response.json();

    // We can display logs on the page in a <div> or <pre>:
    const logContainer = document.getElementById('log-container');
    if (!logContainer) {
      console.warn("No element with id='log-container' found in HTML.");
    }

    if (result.status === 'success') {
      alert('Data downloaded successfully!');
      if (logContainer && result.logs) {
        logContainer.innerText = result.logs.join('\n');
      }
    } else {
      alert(`Error: ${result.message}`);
      if (logContainer && result.logs) {
        logContainer.innerText = result.logs.join('\n');
      }
    }
  } catch (error) {
    alert('Error connecting to server');
    console.error('Error:', error);
  } finally {
    // Hide loading spinner
    searchStatus.style.display = 'none';
    form.querySelector('button').disabled = false;
  }
}
