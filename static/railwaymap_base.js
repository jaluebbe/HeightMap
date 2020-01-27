var map = L.map('map').setView([-41, 172], 6);
map.attributionControl.addAttribution(
    '<a href="https://github.com/jaluebbe/HeightMap">Source on GitHub</a>');
// add link to an imprint and a privacy statement if the file is available.
function addPrivacyStatement() {
    var xhr = new XMLHttpRequest();
    xhr.open('HEAD', "./static/datenschutz.html");
    xhr.onload = function() {
        if (xhr.status === 200)
            map.attributionControl.addAttribution(
                '<a href="./static/datenschutz.html" target="_blank">Impressum & Datenschutzerkl&auml;rung</a>'
            );
    }
    xhr.send();
}
addPrivacyStatement();
var wmsLayer = L.tileLayer.wms('https://sgx.geodatenzentrum.de/wms_topplus_open', {
    layers: 'web',
    format: 'image/png',
    transparent: true,
    minZoom: 1,
    attribution: '&copy <a href="https://www.bkg.bund.de">BKG</a> 2019, ' +
        '<a href= "http://sg.geodatenzentrum.de/web_public/Datenquellen_TopPlus_Open.pdf" >data sources</a> '
});
L.control.scale({
    'imperial': false
}).addTo(map);
var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
var otmLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    maxZoom: 15,
    attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
        'contributors, SRTM | Map style: &copy; ' +
        '<a href="https://opentopomap.org">OpenTopoMap</a> ' +
        '(<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
});
esriImagery = L.layerGroup([
    L.esri.basemapLayer('Imagery'),
    L.esri.basemapLayer('ImageryLabels')
]);
baseLayers = {
    "TopPlusOpen": wmsLayer,
    "OpenTopoMap": otmLayer,
    "OpenStreetMap": osmLayer,
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
function trackClicked(eo) {}
var nzRailwayMap = L.geoJSON(null, {
    attribution: '&copy; <a href="https://catalogue.data.govt.nz/dataset/nz-railway-network">KiwiRail</a> (<a href="https://creativecommons.org/licenses/by/4.0/">CC-BY</a>)',
    onEachFeature: function(feature, layer) {
        layer.on('click', function(eo) {
            trackClicked(eo);
        });
        var tooltipContent =
            '' + feature.properties.LINESECTIO + "<br>" +
            'Line code: ' + feature.properties.LINECODE;
        layer.bindTooltip(tooltipContent, {
            sticky: true,
            direction: "top",
            offset: [0, -5]
        });
    },
    style: function(feature) {
        return {
            bubblingMouseEvents: false,
            color: feature.properties.LINESECTIO.getHashCode().intToHSL()
        };
    }
}).addTo(map);
var openPtMap = L.tileLayer('http://openptmap.org/tiles/{z}/{x}/{y}.png', {
    minZoom: 4,
    maxZoom: 17,
    attribution: 'Map data: &copy; <a href="http://www.openptmap.org">OpenPtMap</a> contributors'
});
var openRailwayMap = L.tileLayer('https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png', {
    minZoom: 2,
    maxZoom: 17,
    attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Map style: &copy; <a href="https://www.OpenRailwayMap.org">OpenRailwayMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
});
var other_layers = {
    "NZ railway network": nzRailwayMap,
    "Openptmap": openPtMap,
    "OpenRailwayMap": openRailwayMap
};
var layerControl = L.control.layers(baseLayers, other_layers, {
    collapsed: L.Browser.mobile, // hide on mobile devices
    position: 'topright'
}).addTo(map);
function loadNzRailwayMap() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './static/NZ_railway_network_reduced.geojson');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            nzRailwayMap.addData(JSON.parse(xhr.responseText));
        }
    };
    xhr.send();
}
loadNzRailwayMap();
