var map;
var days = [];
var h_path;

window.onload = function() {
    initMap();
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
    req.open('GET', 'days', true);
    req.send();
}

function dataLoaded() {
    days = JSON.parse(this.responseText)['days'];
    console.log('data loaded');

    fillPanel();
    fillMap();
}

function fillPanel() {
    for (var i in days) {
        var day = days[i];

        var dist_factor = Math.min(day['dist'] / 300000, 1);
        var dist_color = parseInt(16 - (16 * dist_factor)).toString(16)

        var table = document.getElementById('days-table');
        var tr = document.createElement("tr");
    
        var td = document.createElement("td");
        td.innerHTML = day['date'];
        td.data = "testdata";
        td.setAttribute('arr-index', i);

        var td2 = document.createElement("td");
        td2.innerHTML = day['dist'] / 1000 + ' km';
        td2.setAttribute('arr-index', i);

        tr.appendChild(td);
        tr.appendChild(td2);
        tr.style.color = '#'+dist_color+'f'+dist_color;
        table.appendChild(tr);
    }
}

function fillMap() {
    for (var i in days) {
        var day = days[i];

        var points = day['points'];
        var path = new google.maps.Polyline({
            path: points,
            geodesic: true,
            strokeColor: '#7777FF',
            strokeOpacity: 0.3,
            strokeWeight: 4
        });
        path.setMap(map);

        
    }
}

function highlightRoute(i) {
    if (h_path) {
        h_path.setMap(null);
    }

    var h_points = days[i]['points']
    h_path = new google.maps.Polyline({
        path: h_points,
        geodesic: true,
        strokeColor: '#f00',
        strokeOpacity: 1,
        strokeWeight: 4,
        fillColor: '#f00',
        fillOpacity: 1,
        zIndex: 1000
    });
    console.log(h_path.zIndex)
    h_path.setMap(map);
    console.log(h_path.zIndex)
}

function tableClick(e) {
    var i = e.target.getAttribute('arr-index');
    if (i) {
        highlightRoute(i);
    }
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
