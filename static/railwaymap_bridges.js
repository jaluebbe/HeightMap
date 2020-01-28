map.createPane('bridges');
map.getPane('bridges').style.zIndex = 393;
var nzRailwayBridges = L.geoJSON(null, {
    attribution: 'Bridges &copy; <a href="https://catalogue.data.govt.nz/dataset/kiwirail-bridges1">KiwiRail</a> (<a href="https://creativecommons.org/licenses/by/4.0/">CC-BY</a>)',
    pane: 'bridges',
    onEachFeature: function(feature, layer) {
        var tooltipContent =
            'Line name: ' + feature.properties.LINE_NAME + "<br>" +
            'Bridge name: ' + feature.properties.BRIDGE_NAM + "<br>" +
            'Bridge type: ' + feature.properties.BRIDGE_TYP + "<br>" +
            'TLA name: ' + feature.properties.TLA_Name;
        layer.bindTooltip(tooltipContent, {
            sticky: true,
            direction: "top",
            offset: [0, -5]
        });
    },
    style: function(feature) {
        return {
            bubblingMouseEvents: false,
            color: 'dimgray',
            weight: 7,
            lineCap: 'butt',
            opacity: 0.9
        };
    }
}).addTo(map);
layerControl.addOverlay(nzRailwayBridges, 'NZ railway bridges');
function loadNzRailwayBridges() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './static/KiwiRail_bridges_reduced.geojson');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            nzRailwayBridges.addData(JSON.parse(xhr.responseText));
        }
    };
    xhr.send();
}
loadNzRailwayBridges();
