/*
 * Ben's old `file.py` file created around November 2023.
 * This file is for reference.
 */

//Initiate Map

var map = L.map('map', {
  'center': [23.51, 80.33],
  'zoom': 5,
  'layers': [
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      'attribution': 'Map data &copy; OpenStreetMap contributors'
    })
  ]
});

var home = {
  lat: 23.51,
  lng: 80.33,
  zoom: 5
};

//L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png', {
//  attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
//}).addTo(map);

//L.Control.geocoder().addTo(map);

L.easyButton('<img src="512.png" style="width:16px">',function(btn,map){
  map.setView([home.lat, home.lng], home.zoom);
},'Zoom To Home').addTo(map);

//Initiate geocoder and setup polygon select for search area found
var geocoder = L.Control.geocoder({
        position:'topleft',
	defaultMarkGeocode: false
})
   .on('markgeocode', (e) => {
    var bbox = e.geocode.bbox;
    var poly = L.polygon([
      bbox.getSouthEast(),
      bbox.getNorthEast(),
      bbox.getNorthWest(),
      bbox.getSouthWest()
    ])//.addTo(map);
    map.fitBounds(poly.getBounds());
  })
  .addTo(map);


//Add geojson control layers for viewing on map
var controlLayers = L.control.layers(null, null,{collapsed: false}).addTo(map);


var file = 'json/Chattri.json';
var file2 = 'json/bihar.json';
var file3 = 'json/harjana.json';
var file4 = 'json/Andhra.json';
var file5 = 'json/karna.json';
var file6 = 'json/kerala.json';
var file7 = 'json/Madhya.json';
var file8 = 'json/telangana.json';


$.getJSON(file, function (geojson) {
  var geojsonLayer = L.geoJson(geojson, {
    style: function (feature) {
      return {
        'weight': 0,
        'fillColor': 'orange',
        'fillOpacity': 0.40
      }
    }
  });
  controlLayers.addOverlay(geojsonLayer, 'WH Orange');

});

$.getJSON(file2, function (geojson) {
  var geojsonLayer = L.geoJson(geojson, {
    style: function (feature) {
      return {
        'weight': 0,
        'fillColor': 'red',
        'fillOpacity': 0.40
      }
    }
  });
  controlLayers.addOverlay(geojsonLayer, 'WH Red');
});

$.getJSON(file3, function (geojson) {
  var geojsonLayer = L.geoJson(geojson, {
    style: function (feature) {
      return {
        'weight': 0,
        'fillColor': 'blue',
        'fillOpacity': 0.40
      }
    }
  });
  controlLayers.addOverlay(geojsonLayer, 'WH Blue');
});

$.getJSON(file4, function (geojson) {
  var geojsonLayer = L.geoJson(geojson, {
    style: function (feature) {
      return {
        'weight': 0,
        'fillColor': 'yellow',
        'fillOpacity': 0.40
      }
    }
  });3
  controlLayers.addOverlay(geojsonLayer, 'WH Yellow');
});

$.getJSON(file5, function (geojson) {
  var geojsonLayer = L.geoJson(geojson, {
    style: function (feature) {
      return {
        'weight': 0,
        'fillColor': 'pink',
        'fillOpacity': 0.40
      }
    }
  });
  controlLayers.addOverlay(geojsonLayer, 'WH Pink');
});

$.getJSON(file6, function (geojson) {
  var geojsonLayer = L.geoJson(geojson, {
    style: function (feature) {
      return {
        'weight': 0,
        'fillColor': 'green',
        'fillOpacity': 0.40
      }
    }
  });
  controlLayers.addOverlay(geojsonLayer, 'WH Green');
});

$.getJSON(file7, function (geojson) {
  var geojsonLayer = L.geoJson(geojson, {
    style: function (feature) {
      return {
        'weight': 0,
        'fillColor': 'purple',
        'fillOpacity': 0.40
      }
    }
  });
  controlLayers.addOverlay(geojsonLayer, 'WH Purple');
});

$.getJSON(file8, function (geojson) {
  var geojsonLayer = L.geoJson(geojson, {
    style: function (feature) {
      return {
        'weight': 0,
        'fillColor': 'black',
        'fillOpacity': 0.40
      }
    }
  });
  controlLayers.addOverlay(geojsonLayer, 'WH Black');
});

var editableLayers = new L.FeatureGroup();
map.addLayer(editableLayers);

var drawControl = new L.Control.Draw({
  position: 'topright',
  draw: {
    polyline: false,
    polygon: {
      allowIntersection: false, // Restricts shapes to simple polygons
      drawError: {
        color: '#e1e100', // Color the shape will turn when intersects
        message: '<strong>Oh snap!<strong> you can\'t draw that!' // Message that will show when intersect
      }
    },
    circle: false, // Turns off this drawing tool
    rectangle: true,
    marker: false
  },
  edit: {
    featureGroup: editableLayers, //REQUIRED!!
    remove: true
  }
});

map.addControl(drawControl);

map.on(L.Draw.Event.CREATED, function(e) {
  var type = e.layerType,
    layer = e.layer;

  if (type === 'marker') {
    layer.bindPopup('LatLng: ' + layer.getLatLng().lat + ',' + layer.getLatLng().lng).openPopup();
  }

  editableLayers.addLayer(layer);
  layerGeoJSON = editableLayers.toGeoJSON();
  //alert("GEOJSON FORMAT\r\n" + JSON.stringify(layerGeoJSON));

  var wkt_options = {};
  var geojson_format = new OpenLayers.Format.GeoJSON();
  var testFeature = geojson_format.read(layerGeoJSON);
  var wkt = new OpenLayers.Format.WKT(wkt_options);
  var out = wkt.write(testFeature);

  alert("WKT FORMAT\r\n" + out);
});

//On Draw Edit Event
map.on(L.Draw.Event.EDITED, function(e) {
  var type = e.layerType,
    layer = e.layer;

  layerGeoJSON = editableLayers.toGeoJSON();
  //alert("GEOJSON FORMAT\r\n" + JSON.stringify(layerGeoJSON));

  var wkt_options = {};
  var geojson_format = new OpenLayers.Format.GeoJSON();
  var testFeature = geojson_format.read(layerGeoJSON);
  var wkt = new OpenLayers.Format.WKT(wkt_options);
  var out = wkt.write(testFeature);

  alert("WKT FORMAT\r\n" + out);
});

//On Draw Delete Event
map.on(L.Draw.Event.DELETED, function(e) {
  var type = e.layerType,
    layer = e.layer;

  layerGeoJSON = editableLayers.toGeoJSON();
 // alert("GEOJSON FORMAT\r\n" + JSON.stringify(layerGeoJSON));
  var wkt_options = {};
  var geojson_format = new OpenLayers.Format.GeoJSON();
  var testFeature = geojson_format.read(layerGeoJSON);
  var wkt = new OpenLayers.Format.WKT(wkt_options);
  var out = wkt.write(testFeature);

  //alert("WKT FORMAT\r\n" + out);
});



//map.on('click', function(e) {
//        var popLocation= e.latlng;
//        var popup = L.popup()
//        .setLatLng(popLocation)
//        .setContent('<p>Hello world!<br />This is a nice popup.</p>')
//        .openOn(map);
//    });


//var popup = L.popup();

//function onMapClick(e) {
//popup
//    .setLatLng(e.latlng)
//    .setContent(e.latlng.toString() + '<br><a href="https://wktmap.com">Create Polygon here and paste WKT string...</a>"')
//    .openOn(map);
//}

//map.on('click', onMapClick);


//$.getJSON(file, function (geojson) {
//  var geojsonLayer = L.geoJson(geojson, {
//    style: function (feature) {
//      return {
//        'weight': 1,
//        'color': 'red',
//        'fillOpacity': 0
//      }
//    }
//  });
//  controlLayers.addOverlay(geojsonLayer, 'Water Hyacinth Border');
//});


//Add Basemaps
var osm = L.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
    googleSat = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',{
        maxZoom: 20,
        subdomains:['mt0','mt1','mt2','mt3']
});

var baseMaps = {
    "OpenStreetMap": osm,
    "Satellite": googleSat
};

var overlays =  {//add any overlays here

    };

L.control.layers(baseMaps,overlays, {position: 'bottomleft'}).addTo(map);

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