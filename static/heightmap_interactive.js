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
info.updateElevation = function(altitude_m, source) {
    this._div.innerHTML = "<div style='text-align: right;'><b>"
        + altitude_m + "&nbsp;m</b></div>" + source;
};
info.addTo(map);
var myMarker = L.marker([50, 8.6], {
    draggable: true,
    zIndexOffset: 1000
});
var myCircle = L.circle(myMarker.getLatLng(), {
    radius: 0
});
myMarker.bindTooltip("", {
    direction: 'top'
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
            myCircle.setLatLng([height_info.latitude, height_info.longitude]);
            myCircle.setRadius(height_info.distance_m);
	    info.updateElevation(height_info.altitude_m, height_info.source);
            map.attributionControl.addAttribution(height_info.attribution);
        }
    };
    xhr.send();
}

myMarker.on('move', throttle(requestHeight, 100));
map.on('click', requestHeight);
map.on('locationfound', requestHeight);
map.locate();
