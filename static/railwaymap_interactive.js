var hg;
function getHeightGraphData(feature) {
    console.log(feature);
    var xhr = new XMLHttpRequest();
    xhr.open('POST', './api/geojson/get_height_graph_data');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            console.log(JSON.parse(xhr.responseText));
//            nzRailwayMap.addData(JSON.parse(xhr.responseText));
        }
    };
    xhr.send(JSON.stringify(feature));
}
var activeTrackSegment = L.geoJSON(null, {
    onEachFeature: function(feature, layer) {
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
            weight: 2,
            dashArray: '3, 4',
            color: 'orange'
        };
    }
}).addTo(map);
function trackClicked(eo) { 
    var pt = turf.point([eo.latlng.lng, eo.latlng.lat]);
    var min_distance = 1e4;
    var closestLineString = {};
    turf.flattenEach(eo.target.feature, function (currentFeature, featureIndex, multiFeatureIndex) {
        var distance_km = turf.pointToLineDistance(pt, currentFeature);
        if (distance_km < min_distance && currentFeature.geometry.type == 'LineString') {
            min_distance = distance_km;
            closestLineString = currentFeature;
        }
    });
    activeTrackSegment.clearLayers()
    activeTrackSegment.addData(closestLineString);
    getHeightGraphData(closestLineString);
}
map.on('click', function(eo) {
    activeTrackSegment.clearLayers();
});
