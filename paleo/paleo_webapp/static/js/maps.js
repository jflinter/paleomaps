$(document).ready(function() {
  var spinner = new Spinner({
    lines: 10, // The number of lines to draw
    length: 3, // The length of each line
    width: 2, // The line thickness
    radius: 4, // The radius of the inner circle
    color: '#000', // #rgb or #rrggbb
    speed: 3, // Rounds per second
    trail: 60, // Afterglow percentage
    shadow: false, // Whether to render a shadow
    hwaccel: false, // Whether to use hardware acceleration
    className: 'spinner', // The CSS class to assign to the spinner
    zIndex: 2e9, // The z-index (defaults to 2000000000)
    top: 6, // Top position relative to parent in px
    left: 236 // Left position relative to parent in px
  });
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
  function addMarkerFromJson(place) {
    var latLng = new google.maps.LatLng(place.fields.latitude, place.fields.longitude);
    var marker = new google.maps.Marker({position: latLng, map: map, title:place.fields.name});
    google.maps.event.addListener(marker, 'click', function() {
      $(".info_not_start").hide();
      $(".info_start").hide();
      $("#info_menu_items dl").empty();
      $("#info_title h3").text(place.fields.name);
      $("#info_title").addClass('willShow');
      $("#info_address p").text(place.fields.location);
      $("#info_address").addClass('willShow');
      $("#info_menu_items").addClass('willShow');
      spinner.spin(document.getElementById('info_menu_items'));
      if (place.fields.description != '') {
        $("#info_restaurant_notes h3").text('Restaurant Notes:');
        $("#info_restaurant_notes p").text(place.fields.description);
        $("#info_restaurant_notes").addClass('willShow');
      }
      $(".willShow").show();
      $(".willShow").removeClass("willShow");
      $.get("/menu_for_place", { 'pk': place.pk }, function(data) {
        spinner.stop();
        if (data.length < 1) {
          $("#info_menu_items dl").append("<dt>No menu items available</dt>")
        }
        data.map(function(menu_item) {
          $("#info_menu_items dl").append("<dt>"+menu_item.fields.name+"</dt><dd>"+menu_item.fields.description+"</dd>");
        })
      }, "json");
    })
  }
  $.get("/get_all_places",
     function(data){
       data.map(addMarkerFromJson)
     }, "json");
  
});