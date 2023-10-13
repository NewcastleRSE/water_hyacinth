var map = L.map('map', {
  'center': [23.51, 80.33],
  'zoom': 5,
  'layers': [
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      'attribution': 'Map data &copy; OpenStreetMap contributors'
    })
  ]
});


//L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png', {
//  attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
//}).addTo(map);

//L.Control.geocoder().addTo(map);


var geocoder = L.Control.geocoder({
        position:'topleft',
	defaultMarkGeocode: false
})
  .on('markgeocode', function(e) {
    var bbox = e.geocode.bbox;
    var poly = L.polygon([
      bbox.getSouthEast(),
      bbox.getNorthEast(),
      bbox.getNorthWest(),
      bbox.getSouthWest()
    ]).addTo(map);
    map.fitBounds(poly.getBounds());
  })
  .addTo(map);

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
  });
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
  });
  controlLayers.addOverlay(geojsonLayer, 'Water Hyacinth Border');
});



  //-- Searchbox
//  var markersLayer = new L.LayerGroup();  //layer contain searched elements

//  map.addLayer(markersLayer);

//  var controlSearch = new L.Control.Search({
//      position:'topleft',
//      layer: markersLayer,
//      initial: false,
//      zoom: 15,
//      marker: false,
//      clickable: true
//  });

  //- Show popup (info window) if found
//  controlSearch.on("search:locationfound", function (e) {
//    if (e.layer._popup) e.layer.openPopup();
//  });

//  map.addControl(controlSearch);
