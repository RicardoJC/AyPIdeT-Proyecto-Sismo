// Create map





function initMap() {
  // Map options
  var options = {
    zoom: 8,
    center: { lat: 19.4326, lng: -99.1332 }
  }

  // New map
  var map = new google.maps.Map(document.getElementById('map'), options);
  var infoWindow = new google.maps.InfoWindow();


  loadJSON(function(response) {

    var json = JSON.parse(response);

    for (var i = 0, length = json.length; i < length; i++) {
      var data = json[i],
          latLng = new google.maps.LatLng(data.lat, data.lng);
      // Creating a marker and putting it on the map
      var marker = new google.maps.Marker({
        position: latLng,
        map: map,
        title: data.title
      });

      (function(marker, data) {

        // Attaching a click event to the current marker
        google.maps.event.addListener(marker, "click", function(e) {
          infoWindow.setContent(data.description);
          infoWindow.open(map, marker);
        });

      }(marker, data));
    }

  });


  // capturar campo
  var locationForm = document.getElementById('location-form');

  // Listen for submit
  locationForm.addEventListener('submit', geocode);

  function geocode(e) {
    e.preventDefault();
    console.log("botonazo");
    var query_city = document.getElementById('location-input').value;
    console.log(query_city);
    document.getElementById('ltnlng').innerHTML = query_city;
    axios.get('https://maps.googleapis.com/maps/api/geocode/json', {
      params: {
        address: document.getElementById('ltnlng').innerHTML,
        key: 'AIzaSyBL5XV9C6bmq7oct5X0pkLHbEvtVwInQPg'
      }
    })
      .then(function (response) {
        console.log(response.data.results[0].address_components);
        var lat = response.data.results[0].geometry.location.lat;
        var lng = response.data.results[0].geometry.location.lng;
        var marker = {
          coords: {lat:lat,lng:lng},
          content: '<h>' + query_city +'</h>'
        }
        var geometryOutput = `
          <ul class="list-group">
            <li class="list-group-item"><strong>Latitude</strong>: ${lat}</li>
            <li class="list-group-item"><strong>Longitude</strong>: ${lng}</li>
          </ul>
        `;
        addMarker(marker);
        document.getElementById('ltnlng').innerHTML = geometryOutput;
      }
      )
  }


  function loadJSON(callback) {

      var xobj = new XMLHttpRequest();
      xobj.overrideMimeType("application/json");
      xobj.open('GET', 'locations.json', true);
      xobj.onreadystatechange = function() {
          if (xobj.readyState == 4 && xobj.status == "200") {
              // .open will NOT return a value but simply returns undefined in async mode so use a callback
              callback(xobj.responseText);

          }
      }
      xobj.send(null);

  }



}
