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
    this.showText('No geolocation information available.');
    return this._div;
};
info.showText = function(infoText) {
    this._div.innerHTML = infoText;
};
info.updateElevation = function(altitude_m, source) {
    this._div.innerHTML = "<div style='text-align: right;'><b>"
        + altitude_m + "&nbsp;m</b></div>" + source;
};
info.addTo(map);
var myMarker = L.marker([], {
    draggable: false,
    zIndexOffset: 1000
});
var myCircle = L.circle([], {
    radius: 0
});
var myPolyline = L.polyline([], {
    color: 'red'
});

function requestHeight(e) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', './api/get_height' + '?lat=' + e.latlng.lat + '&lon=' + e.latlng.lng);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            var height_info = JSON.parse(xhr.responseText);
            myMarker.setLatLng(e.latlng);
            myCircle.setLatLng(e.latlng);
            myCircle.setRadius(e.accuracy);
            if (!map.hasLayer(myMarker)) {
                myMarker.addTo(map);
                myCircle.addTo(map);
                myPolyline.addTo(map);
            }
            if (!map.getBounds().contains(myMarker.getLatLng())) {
                map.setView(myMarker.getLatLng());
            }
            myPolyline.setLatLngs([e.latlng, [height_info.latitude, height_info.longitude]]);
	    info.updateElevation(height_info.altitude_m, height_info.source);
            map.attributionControl.addAttribution(height_info.attribution);
        }
    };
    xhr.send();
}

map.setZoom(9)

function onLocationError(e) {
    info.showText('No geolocation information available.');
}
map.on('locationfound', requestHeight);
map.on('locationerror', onLocationError);
map.locate({
    watch: true,
    enableHighAccuracy: true
});
