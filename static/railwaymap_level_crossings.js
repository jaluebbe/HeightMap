map.createPane('level_crossings');
map.getPane('level_crossings').style.zIndex = 394;
var nzLevelCrossings = L.geoJSON(null, {
    attribution: 'Level crossings &copy; <a href="https://catalogue.data.govt.nz/dataset/level-crossings-railway">KiwiRail</a> (<a href="https://creativecommons.org/licenses/by/4.0/">CC-BY</a>)',
    pane: 'level_crossings',
    onEachFeature: function(feature, layer) {
        var tooltipContent =
            'Line name: ' + feature.properties.lineName + "<br>" +
            'Crossing type: ' + feature.properties.type + "<br>" +
            'Use: ' + feature.properties.Use_ + "<br>" +
            'TLA name: ' + feature.properties.TLA_Name;
        layer.bindTooltip(tooltipContent, {
            sticky: true,
            direction: "top",
            offset: [0, -5]
        });
    },
    pointToLayer: function(feature, latlng) {
        return L.marker(latlng, {
            icon: L.icon({
                iconUrl: 'static/level_crossing.svg',
                iconSize: [20, 30.31],
                tooltipAnchor: [10, -30.31]
            })
        });
    }
});
var clusteredLevelCrossings = L.markerClusterGroup({
    maxClusterRadius: 30
});
map.addLayer(clusteredLevelCrossings);
layerControl.addOverlay(clusteredLevelCrossings, 'NZ level crossings');

function loadNzLevelCrossings() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './static/level_crossings_railway_reduced.geojson');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            nzLevelCrossings.addData(JSON.parse(xhr.responseText));
            clusteredLevelCrossings.clearLayers();
            clusteredLevelCrossings.addLayer(nzLevelCrossings);
        }
    };
    xhr.send();
}
loadNzLevelCrossings();
