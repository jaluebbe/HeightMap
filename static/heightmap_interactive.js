var throttle = function throttle(func, limit) {
  var inThrottle;
  return function () {
    var args = arguments;
    var context = this;

    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(function () {
        return inThrottle = false;
      }, limit);
    }
  };
};

var info = L.control({position: 'bottomright'});
info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.showText('Click on the map to place a marker!<br>You can drag that marker.');
    return this._div;
};
info.showText = function(infoText) {
    this._div.innerHTML = infoText;
};
info.updateElevation = function(altitude, source, surfaceLabel) {
    var txt = "<div style='text-align: right;'><b>"
        + altitude + "&nbsp;m</b></div>";
    txt += "<div style='text-align: right;'>" + source + "</div>";
    if (surfaceLabel)
        txt += "<div style='text-align: right;'>" + surfaceLabel + "</div>";
    this._div.innerHTML = txt;
};
info.addTo(map);
var myMarker = L.marker([50, 8.6], {
    draggable: true,
    zIndexOffset: 1000,
    icon: L.icon({
        iconUrl: 'static/level_staff_red.svg',
        shadowUrl: 'static/level_staff_shadow.png',
        shadowSize: [46, 66],
        shadowAnchor: [0, 66],
        iconSize: [10, 121],
        iconAnchor: [5, 121],
        tooltipAnchor: [0, -121]
    })
});
var myCircle = L.circle(myMarker.getLatLng(), {
    radius: 0
});
myMarker.bindTooltip("", {
    direction: 'top'
});

var minMaxLocations = L.geoJSON(null, {
    onEachFeature: function(feature, layer) {
        var tooltipContent =
            '' + feature.properties.type + "<br>" +
            feature.properties.elevation_m + "&nbsp;m<br>" + feature.properties.source;
        layer.bindTooltip(tooltipContent, {
            direction: "top"
        });
    },
    pointToLayer: function(feature, latlng) {
        if (feature.properties.type == 'minimum')
            return L.marker(latlng, {
                icon: L.icon({
                    iconUrl: 'static/minimum_marker.svg',
                    iconSize: [20, 97],
                    iconAnchor: [10, 97],
                    tooltipAnchor: [0, -97]
                })
            });
        else
            return L.marker(latlng, {
                icon: L.icon({
                    iconUrl: 'static/maximum_marker.svg',
                    iconSize: [20, 105],
                    iconAnchor: [10, 105],
                    tooltipAnchor: [0, -105]
                })
            });
    }
});

function requestHeight(e) {
    var xhr = new XMLHttpRequest();
    var latlng = e.latlng.wrap();
    xhr.open('GET', './api/get_height' + '?lat=' + latlng.lat + '&lon=' + latlng.lng);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            var height_info = JSON.parse(xhr.responseText);
            if (e.type == 'click' || e.type == 'locationfound') {
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
            myCircle.setLatLng([height_info.lat_found, height_info.lon_found]);
            myCircle.setRadius(height_info.distance_m);
            if (height_info.wb_label == 'Land')
                addLandCover(latlng.lat, latlng.lng, height_info.altitude_m, height_info.source);
            else
                info.updateElevation(height_info.altitude_m, height_info.source, height_info.wb_label);
            height_info.attributions.forEach(attribution => map.attributionControl.addAttribution(attribution));
        }
    };
    xhr.send();
}

function addLandCover(lat, lon, altitude, heightSource) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './api/get_land_cover' + '?lat=' + lat + '&lon=' + lon);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            let lcData = JSON.parse(xhr.responseText)
            lcData.attributions.forEach(attribution => map.attributionControl.addAttribution(attribution));
            info.updateElevation(altitude, heightSource, lcData.label);
        } else {
            info.updateElevation(altitude, heightSource, 'Land');
        }
    };
    xhr.send();
}

function requestMinMaxHeight(bounds) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './api/get_min_max_height' + '?lat_ll=' + bounds._southWest.lat +
        '&lon_ll=' + bounds._southWest.lng + '&lat_ur=' + bounds._northEast.lat +
        '&lon_ur=' + bounds._northEast.lng);
    minMaxLocations.clearLayers();
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            minMaxLocations.addData(JSON.parse(xhr.responseText));
            if (!map.hasLayer(minMaxLocations)) {
                minMaxLocations.addTo(map);
            }
        }
    };
    xhr.send();
}
L.Map.BoxZoom.prototype._onMouseUp = function(e) {
    if ((e.which !== 1) && (e.button !== 1)) {
        return;
    }
    this._finish();
    if (!this._moved) {
        return;
    }
    setTimeout(L.bind(this._resetState, this), 0);
    var bounds = new L.LatLngBounds(
        this._map.containerPointToLatLng(this._startPoint),
        this._map.containerPointToLatLng(this._point));
    requestMinMaxHeight(bounds);
    this._map.fire('boxzoomend', {
        boxZoomBounds: bounds
    });
}
myMarker.on('move', throttle(requestHeight, 100));
map.on('click', requestHeight);
map.on('locationfound', requestHeight);
map.locate();
