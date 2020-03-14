var map = L.map('map').setView([50.0, 8.0], 5);
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
        return L.marker(latlng, {
            icon: L.icon({
                iconUrl: 'static/peak.svg',
                iconSize: [22, 17],
                tooltipAnchor: [11, -8.5]
            })
        });
    }
}).addTo(map);
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
        if (feature.properties.type == 'depression')
            return L.marker(latlng, {
                icon: L.icon({
                    iconUrl: 'static/depression.svg',
                    iconSize: [22, 8],
                    tooltipAnchor: [11, -4]
                })
            });
        else if (feature.properties.type == 'subsea_depression')
            return L.marker(latlng, {
                icon: L.icon({
                    iconUrl: 'static/subsea_depression.svg',
                    iconSize: [22, 8],
                    tooltipAnchor: [11, -4]
                })
            });
        else if (feature.properties.type == 'surface_mine')
            return L.marker(latlng, {
                icon: L.icon({
                    iconUrl: 'static/mining.svg',
                    iconSize: [22, 19.343],
                    tooltipAnchor: [11, -10]
                })
            });
        else if (feature.properties.type == 'shipwreck')
            return L.marker(latlng, {
                icon: L.icon({
                    iconUrl: 'static/shipwreck.svg',
                    iconSize: [22, 12],
                    tooltipAnchor: [11, -6]
                })
            });
        else
            return L.circleMarker(latlng, {
                color: 'red',
                fillColor: 'red'
            });
    }
}).addTo(map);
var openSeaMap = L.tileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png', {
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
if (typeof mapboxAccessToken !== 'undefined') {

    var mapbox_streets = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>',
        tileSize: 512,
        maxZoom: 18,
        zoomOffset: -1,
        id: 'mapbox/streets-v11',
        accessToken: mapboxAccessToken
    });
    var mapbox_satellite_streets = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>',
        tileSize: 512,
        maxZoom: 18,
        zoomOffset: -1,
        id: 'mapbox/satellite-streets-v11',
        accessToken: mapboxAccessToken
    });
    var mapbox_outdoors = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>',
        tileSize: 512,
        maxZoom: 18,
        zoomOffset: -1,
        id: 'mapbox/outdoors-v11',
        accessToken: mapboxAccessToken
    });
    var mapbox_navigation_preview = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>',
        tileSize: 512,
        maxZoom: 18,
        zoomOffset: -1,
        id: 'mapbox/navigation-preview-day-v4',
        accessToken: mapboxAccessToken
    });
    layerControl.addBaseLayer(mapbox_streets, 'Mapbox Streets');
    layerControl.addBaseLayer(mapbox_satellite_streets, 'MapBox Satellite Streets');
    layerControl.addBaseLayer(mapbox_outdoors, 'Mapbox Outdoors');
    layerControl.addBaseLayer(mapbox_navigation_preview, 'Mapbox Navigation Preview');
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
loadSevenSummits();
loadLowLocations();
