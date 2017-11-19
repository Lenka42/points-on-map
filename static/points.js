var mymap = L.map('mapid').setView([53.9, 27.56], 13);

var BASE_URL = 'http://localhost:8888/api/';

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox.streets',
    accessToken: 'pk.eyJ1IjoibGVua2E0MiIsImEiOiJjamE2cThtNnAzbDluMnpsN3FyMWh0cncwIn0.JiUoqW1EHEs0jf4pMmTWSw'
}).addTo(mymap);

mymap.doubleClickZoom.disable();
var bounds = mymap.getBounds();
getPoints(bounds);

function postNewPoint(data) {
    var xhr = new XMLHttpRequest();
    var url = BASE_URL + 'point';
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 201) {
            var response = JSON.parse(xhr.responseText);
            placeMarkers(response);
        }
    };
    var jsonStringData = JSON.stringify(data);
    xhr.send(jsonStringData);
}

function deletePoint(pointId) {
    var xhr = new XMLHttpRequest();
    var url = BASE_URL + 'point/' + pointId;
    xhr.open("DELETE", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.send();
}

function updatePoint(pointId, newX, newY) {
    var xhr = new XMLHttpRequest();
    var url = BASE_URL + 'point/' + pointId;
    xhr.open("PATCH", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    var jsonStringData = JSON.stringify({"x": newX, "y": newY});
    xhr.send(jsonStringData);
}

function placeMarkers(responseData) {
    for (var point_id in responseData) {
        var point = responseData[point_id];
        var pointLatLng = L.latLng(point.x, point.y);
        if (bounds.contains(pointLatLng)) {
            var marker = new L.marker(pointLatLng, {draggable: true, title: point.name}).addTo(mymap);
            marker.db_id = point_id;
            marker.on('dblclick', function (e) {
                deletePoint(this.db_id);
                this.remove();
            });
            marker.bindPopup(point.name);
            marker.on('click', function (e) {
                if (this.popupopen) {
                    this.closePopup();
                }
                else {
                    this.openPopup();
                }
            });
            marker.on('move', function (e) {
                updatePoint(this.db_id, e.latlng.lat, e.latlng.lng);
            });
        }
    }
}

function getPoints(bounds) {
    var xhr = new XMLHttpRequest();
    var url = BASE_URL + 'point';
    xhr.open("GET", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            placeMarkers(response);
        }
    };
    xhr.send();
}

function onMapDblClick(e) {
    var data = {"x": e.latlng.lat, "y": e.latlng.lng};
    postNewPoint(data);
}

mymap.on('dblclick', onMapDblClick);