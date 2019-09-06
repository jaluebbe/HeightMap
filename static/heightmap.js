var map = L.map('map').setView([50.0, 8.0], 5);
map.attributionControl.addAttribution(
    '<a href="https://github.com/jaluebbe/HeightMap">Source on GitHub</a>');
var wmsLayer = L.tileLayer.wms('https://sgx.geodatenzentrum.de/wms_topplus_open', {
    layers: 'web',
    format: 'image/png',
    transparent: true,
    minZoom: 1,
    attribution: '&copy <a href="https://www.bkg.bund.de">BKG</a> 2019, ' +
        '<a href= "http://sg.geodatenzentrum.de/web_public/Datenquellen_TopPlus_Open.pdf" >data sources</a> '
}).addTo(map);
L.control.scale({
    'imperial': false
}).addTo(map);
var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});
var otmLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    maxZoom: 15,
    attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
        'contributors, SRTM | Map style: &copy; ' +
        '<a href="https://opentopomap.org">OpenTopoMap</a> ' +
        '(<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
});
esriOceans = L.layerGroup([
    L.esri.basemapLayer('Oceans'),
    L.esri.basemapLayer('OceansLabels')
]);
esriImagery = L.layerGroup([
    L.esri.basemapLayer('Imagery'),
    L.esri.basemapLayer('ImageryLabels')
]);
baseLayers = {
    "TopPlusOpen": wmsLayer,
    "OpenTopoMap": otmLayer,
    "OpenStreetMap": osmLayer,
    "Esri Oceans": esriOceans,
    "Esri Imagery": esriImagery
};
if (typeof mapboxAccessToken !== 'undefined') {
    var mapbox_streets = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=' +
        mapboxAccessToken, {
            maxZoom: 19,
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery &copy; ' +
                '<a href="https://www.mapbox.com/">Mapbox</a>',
            id: 'mapbox.streets'
        });
    var mapbox_streets_satellite = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=' +
        mapboxAccessToken, {
            maxZoom: 19,
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery &copy; ' +
                '<a href="https://www.mapbox.com/">Mapbox</a>',
            id: 'mapbox.streets-satellite'
        });
    Object.assign(baseLayers, {
        "Mapbox Streets": mapbox_streets,
        "MapBox Satellite Streets": mapbox_streets_satellite
    });
}
var sevenSummits = L.geoJSON(null, {
    onEachFeature: function(feature, layer) {
        var tooltipContent =
            '' + feature.properties.name + "<br>" +
            feature.properties.elevation_m + "&nbsp;m";
        layer.bindTooltip(tooltipContent, {
            direction: "top"
        });

    },
    pointToLayer: function(feature, latlng) {
        return L.circleMarker(latlng, {
            color: 'green',
            fillColor: 'green'
        });
    }
});
var lowLocations = L.geoJSON(null, {
    onEachFeature: function(feature, layer) {
        var tooltipContent =
            '' + feature.properties.name + "<br>" +
            feature.properties.elevation_m + "&nbsp;m";
        layer.bindTooltip(tooltipContent, {
            direction: "top"
        });

    },
    pointToLayer: function(feature, latlng) {
        return L.circleMarker(latlng, {
            color: 'red',
            fillColor: 'red'
        });
    }
});
var openSeaMap = L.tileLayer('http://tiles.openseamap.org/seamark/{z}/{x}/{y}.png', {
    attribution: 'Map data: &copy; <a href="http://www.openseamap.org">OpenSeaMap</a> contributors'
});

var other_layers = {
    'OpenSeaMap': openSeaMap,
    'Seven Summits': sevenSummits,
    'impressive low locations': lowLocations
};
var layerControl = L.control.layers(baseLayers, other_layers, {
    collapsed: L.Browser.mobile, // hide on mobile devices
    position: 'topright'
}).addTo(map);
var info = L.control({position: 'bottomright'});
info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.showText('Click on the map to place a marker!<br>You can drag that marker.');
    return this._div;
};
info.showText = function(infoText) {
    this._div.innerHTML = infoText;
};
info.updateElevation = function(altitude_m, source) {
    this._div.innerHTML = "<div style='text-align: right;'><b>"
        + altitude_m + "&nbsp;m</b></div>" + source;
};
info.addTo(map);
var myMarker = L.marker([50, 8.6], {
    draggable: true,
    zIndexOffset: 1000
});
var myCircle = L.circle(myMarker.getLatLng(), {
    radius: 0
});
myMarker.bindTooltip("", {
    direction: 'top'
});

function requestHeight(e) {
    var xhr = new XMLHttpRequest();
    var latlng = e.latlng.wrap();
    xhr.open('GET', './api/get_height' + '?lat=' + latlng.lat + '&lon=' + latlng.lng);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            var height_info = JSON.parse(xhr.responseText);
            if (e.type == 'click') {
                myMarker.setLatLng(latlng);
                if (!map.hasLayer(myMarker)) {
                    myMarker.addTo(map);
                    myCircle.addTo(map);
                }
                if (!map.getBounds().contains(myMarker.getLatLng())) {
                    map.panInside(myMarker.getLatLng());
                }
            }
            myMarker._tooltip.setContent("<div style='text-align: right;'><b>"
                + height_info.altitude_m + "&nbsp;m</b></div>" + height_info.source);
            myCircle.setLatLng([height_info.latitude, height_info.longitude]);
            myCircle.setRadius(height_info.distance_m);
	    info.updateElevation(height_info.altitude_m, height_info.source);
            map.attributionControl.addAttribution(height_info.attribution);
        }
    };
    xhr.send();
}

function loadSevenSummits() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './static/seven_summits.json');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            sevenSummits.addData(JSON.parse(xhr.responseText));
        }
    };
    xhr.send();
}
function loadLowLocations() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './static/low_locations.json');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            lowLocations.addData(JSON.parse(xhr.responseText));
        }
    };
    xhr.send();
}

myMarker.on('move', requestHeight);
map.on('click', requestHeight);
loadSevenSummits();
loadLowLocations();
