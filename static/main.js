var map;
var data;
var h_path;

window.onload = function() {
    loadData();
};

function loadData() {
    var req = new XMLHttpRequest();
    req.onloadstart = function () {
        console.log('start load');
    }
    req.onload = dataLoaded;
    req.onerror = function () {
        console.log('data load error!');
    }
    req.open('GET', 'data', true);
    req.send();
}

function dataLoaded() {
    data = JSON.parse(this.responseText);
    console.log('data loaded');
    console.log(data);
    
    var points = data['all_points'];
    var all_path = new google.maps.Polyline({
        path: points,
        geodesic: true,
        strokeColor: '#7777FF',
        strokeOpacity: 0.75,
        strokeWeight: 2
    });
    all_path.setMap(map);

    var h_points = data['days'][0]['points'];
    console.log(h_points);
    h_path = new google.maps.Polyline({
        path: h_points,
        geodesic: true,
        strokeColor: '#FF7777',
        strokeOpacity: 0.75,
        strokeWeight: 3
    });
    h_path.setMap(map);

    fillPanel();
}

function fillPanel(content, id) {
    var days = data['days'];
    for (var i in days) {
        var day = days[i];

        var table = document.getElementById('days-table');
        var tr = document.createElement("tr");
        var td = document.createElement("td");
        td.innerHTML = day['date'];
        td.data = "testdata";
        var td2 = document.createElement("td");
        td2.innerHTML = day['points'].length;
        tr.appendChild(td);
        tr.appendChild(td2);
        table.appendChild(tr);
    }
}

function dayClicked() {
    console.log('dayclick');
    console.log(this);
}

function tableClick(e) {
    console.log(e);
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