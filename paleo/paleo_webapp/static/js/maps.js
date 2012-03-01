$(document).ready(function() {
  var myOptions = {
      center: new google.maps.LatLng( 34.038058, -118.468677),
      zoom: 13,
      mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
  function success(position) {
    var latLng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
    map.panTo(latLng);
  }

  function error(msg) {
     var latLng = new google.maps.LatLng( 34.038058, -118.468677);
     map.panTo(latLng)     
  }

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(success, error);
  } else {
    error('not supported');
  }
  function addMarkerFromJson(item) {
    var latLng = new google.maps.LatLng(item.fields.latitude, item.fields.longitude);
    new google.maps.Marker({position: latLng, map: map, title:item.fields.name, animation:google.maps.Animation.DROP});
  }
  $.get("/get_all_places",
     function(data){
       console.log(data);
       data.map(addMarkerFromJson)
     }, "json");
  
});