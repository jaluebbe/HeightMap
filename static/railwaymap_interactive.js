var hg;

function getSteepnessBin(steepness) {
    if (steepness < 2)
        return 0;
    else if (steepness < 5)
        return 1;
    else if (steepness < 10)
        return 2;
    else if (steepness < 20)
        return 3;
    else
        return 4;
}

function getSteepnessTrack(geojson) {
    var features = [];
    var track = [];
    var currentBin = null;
    turf.segmentEach(geojson, function(currentSegment, featureIndex, multiFeatureIndex, geometryIndex, segmentIndex) {
        var segmentLength = turf.length(currentSegment) * 1e3;
        if (segmentLength == 0)
            return;
        var coords = currentSegment.geometry.coordinates;
        var steepness = Math.round(coords[1][2] - coords[0][2]) /
            segmentLength * 100;
        var steepnessBin = getSteepnessBin(steepness);
        if (track.length == 0) {
            currentBin = steepnessBin;
            track.push(coords[0]);
        } else if (steepnessBin != currentBin) {
            features.push(turf.lineString(track, {
                attributeType: currentBin
            }));
            track = [];
            currentBin = steepnessBin;
            track.push(coords[0]);
        } else {}
        track.push(coords[1]);
    });
    if (track.length > 0)
        features.push(turf.lineString(track, {
            attributeType: currentBin
        }));
    featureCollection = turf.featureCollection(features);
    featureCollection.properties = {
        summary: "steepness"
    };
    return featureCollection;
}

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
                mappings: colorMappings,
                width: 640,
                height: 200,
                margins: {
                    top: 10,
                    right: 30,
                    bottom: 55,
                    left: 50
                },
                expand: true,
                position: "bottomright",
                highlightStyle: {
                    weight: 2,
                    color: 'red'
                }
            });
            hg.addTo(map);
            geojson.push(getSteepnessTrack(geojson[0]));
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
