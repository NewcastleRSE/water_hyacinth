var map = L.map('map', {
  'center': [23.51, 80.33],
  'zoom': 5,
  'layers': [
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      'attribution': 'Map data &copy; OpenStreetMap contributors'
    })
  ]
});


var controlLayers = L.control.layers().addTo(map);

var file = 'json/mergebig.json';

$.getJSON(file, function (geojson) {
  var geojsonLayer = L.geoJson(geojson, {
    style: function (feature) {
      return {
        'weight': 0,
        'fillColor': 'yellow',
        'fillOpacity': 0.30
      }
    }
  }).addTo(map);
  controlLayers.addOverlay(geojsonLayer, 'Water Hyacincth Extent');
});

$.getJSON(file, function (geojson) {
  var geojsonLayer = L.geoJson(geojson, {
    style: function (feature) {
      return {
        'weight': 1,
        'color': 'red',
        'fillOpacity': 0
      }
    }
  }).addTo(map);
  controlLayers.addOverlay(geojsonLayer, 'Water Hyacinth Border');
});


L.Control.geocoder({
  defaultMarkGeocode: false,
  placeholder: "Search aDDRESess..."
}).on('markgeocode', function(e) {
    var bbox = e.geocode.bbox;
    var poly = L.polygon([
      bbox.getSouthEast(),
      bbox.getNorthEast(),
      bbox.getNorthWest(),
      bbox.getSouthWest()
    ]).addTo(myMap);
    myMap.fitBounds(poly.getBounds());
  })
  .addTo(map);


