var hg;
function getHeightGraphData(feature) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', './api/geojson/get_height_graph_data');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        map.spin(false);
        if (xhr.status === 200) {
            var geojson = JSON.parse(xhr.responseText);
            if (hg !== undefined)
                hg.remove();
            hg = L.control.heightgraph({
                width: 640,
                height: 200,
                margins: {
                    top: 10,
                    right: 30,
                    bottom: 55,
                    left: 50
                },
                expand: true,
                position: "bottomright"
            });
            hg.addTo(map);
            hg.addData(geojson);
        }
    };
    map.spin(true);
    xhr.send(JSON.stringify(feature));
}
var activeTrackSegment = L.geoJSON(null, {
    onEachFeature: function(feature, layer) {
        var tooltipContent =
            '' + feature.properties.LINESECTIO + "<br>" +
            'Line code: ' + feature.properties.LINECODE + "<br>" +
            'Length: ' + feature.properties.length_km + '&nbsp;km';
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
    closestLineString.properties.length_km = Math.round(1e3 * turf.length(closestLineString)) / 1e3;
    activeTrackSegment.clearLayers()
    activeTrackSegment.addData(closestLineString);
    getHeightGraphData(closestLineString);
}
map.on('click', function(eo) {
    activeTrackSegment.clearLayers();
});
