var map = L.map('map').setView([50.0, 8.0], 5);
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
baseLayers = {
    "TopPlusOpen": wmsLayer,
    "OpenTopoMap": otmLayer,
    "OpenStreetMap": osmLayer
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
}).addTo(map);
var other_layers = {
    'Seven Summits': sevenSummits
};
var layerControl = L.control.layers(baseLayers, other_layers, {
    collapsed: L.Browser.mobile, // hide on mobile devices
    position: 'topright'
}).addTo(map);
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
                + height_info.altitude_m + "&nbsp;m</b></div>"+ height_info.source);
            myCircle.setLatLng([height_info.latitude, height_info.longitude]);
            myCircle.setRadius(height_info.distance_m);
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

myMarker.on('move', requestHeight);
map.on('click', requestHeight);
loadSevenSummits();
