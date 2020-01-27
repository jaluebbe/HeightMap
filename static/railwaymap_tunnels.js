map.createPane('tunnels');
map.getPane('tunnels').style.zIndex = 394;
var nzRailwayTunnels = L.geoJSON(null, {
    attribution: 'Tunnels &copy; <a href="https://catalogue.data.govt.nz/dataset/kiwirail-tunnels1">KiwiRail</a> (<a href="https://creativecommons.org/licenses/by/4.0/">CC-BY</a>)',
    pane: 'tunnels',
    onEachFeature: function(feature, layer) {
        var tooltipContent =
            'Line name: ' + feature.properties.LINE_NAME + "<br>" +
            'Tunnel name: ' + feature.properties.TUNNEL_NAM + "<br>" +
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
            color: '#000000',
            weight: 7,
            lineCap: 'butt',
            opacity: 0.9
        };
    }
}).addTo(map);
layerControl.addOverlay(nzRailwayTunnels, 'NZ railway tunnels');
function loadNzRailwayTunnels() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './static/KiwiRail_tunnels_reduced.geojson');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            nzRailwayTunnels.addData(JSON.parse(xhr.responseText));
        }
    };
    xhr.send();
}
loadNzRailwayTunnels();
