var map;
var path;
var highlighted_path;

function loadData() {
    // remove current path
    if (path != null) {
        path.setMap(null);
    }

    // loading data
    var req = new XMLHttpRequest();
    req.onload = function () {
        dataLoaded();
    }
    req.onprogress = function () {
        console.log('progress...');
    }
    req.onerror = function () {
        console.log('data load error!');
    }
    req.open('GET', 'data', true);
    req.send()
}

function dataLoaded() {
    var data = JSON.parse(this.responseText);
    console.log('data loaded');
    points = data['all_points']
    path = new google.maps.Polyline({
        path: points,
        geodesic: true,
        strokeColor: '#FF7777',
        strokeOpacity: 1.0,
        strokeWeight: 2
    });
    path.setMap(map);
}

function highlightPath() {

}

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 8,
        center: {
            lat: 50.4,
            lng: 30.4
        },
        mapTypeId: 'terrain'
    });
}