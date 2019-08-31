var map = L.map('map').setView([50.0, 8.6], 4);
var wmsLayer = L.tileLayer.wms('https://sgx.geodatenzentrum.de/wms_topplus_open', {
    layers: 'web',
    format: 'image/png',
    transparent: true,
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
baselayers = {
    "TopPlusOpen": wmsLayer,
    "OpenTopoMap": otmLayer,
    "OpenStreetMap": osmLayer
};
var other_layers = {};
var layerControl = L.control.layers(baselayers, other_layers, {
    collapsed: L.Browser.mobile, // hide on mobile devices
    position: 'topright'
}).addTo(map);
var myMarker = L.marker([50, 8.6], {
    draggable: true
});
var myCircle = L.circle(myMarker.getLatLng(), {
    radius: 0
});
myMarker.bindTooltip("", {
    direction: 'top'
});

function requestHeight(e) {
    var xhr = new XMLHttpRequest();
    var latlng = e.latlng;
    xhr.open('GET', './api/get_height' + '?lat=' + latlng.lat + '&lon=' + latlng.lng);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            var height_info = JSON.parse(xhr.responseText);
            if (e.type == 'click') {
                myMarker.setLatLng(latlng);
                if (!map.hasLayer(myMarker)) {
                    myMarker.addTo(map);
                    myCircle.addTo(map);
                }
            }
//            myMarker._tooltip.setContent("<div style='width: 55px;text-align: right;'><b>"
            myMarker._tooltip.setContent("<div style='text-align: right;'><b>"
                + height_info.altitude_m + "&nbsp;m</b></div>"+ height_info.source);
            myCircle.setLatLng([height_info.latitude, height_info.longitude]);
            myCircle.setRadius(height_info.distance_m);
            map.attributionControl.addAttribution(height_info.attribution);
        }
    };
    xhr.send();
}
myMarker.on('move', requestHeight);
map.on('click', requestHeight);
