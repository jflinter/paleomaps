$(document).ready(function() {
    var locationPinColor = "8109E3";
    var locationPinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_icon&chld=home|" + locationPinColor);
    var placePinColor = "FE7569";
    var placePinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + placePinColor);
    var highlightedPinColor = "5BB75B";
    var highlightedPinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + highlightedPinColor);
    var pinShadow = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_shadow", new google.maps.Size(40, 37),
    new google.maps.Point(0, 0),
    new google.maps.Point(12, 35));
    var spinner = new Spinner({
        lines: 10,
        // The number of lines to draw
        length: 3,
        // The length of each line
        width: 2,
        // The line thickness
        radius: 4,
        // The radius of the inner circle
        color: '#000',
        // #rgb or #rrggbb
        speed: 3,
        // Rounds per second
        trail: 60,
        // Afterglow percentage
        shadow: false,
        // Whether to render a shadow
        hwaccel: false,
        // Whether to use hardware acceleration
        className: 'spinner',
        // The CSS class to assign to the spinner
        zIndex: 2e9,
        // The z-index (defaults to 2000000000)
        //top: 6,
        // Top position relative to parent in px
        //left: 236
        // Left position relative to parent in px
    });
    var myOptions = {
        center: new google.maps.LatLng(34.038058, -118.468677),
        zoom: 13,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
    function success(position) {
        var latLng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
        map.panTo(latLng);
        var marker = new google.maps.Marker({
            position: latLng,
            map: map,
            title: 'Your Location',
            icon: locationPinImage,
            shadow: pinShadow,
            zIndex: -5
        });
    }

    function error(msg) {
        var latLng = new google.maps.LatLng(34.038058, -118.468677);
        map.panTo(latLng)
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
    } else {
        error('not supported');
    }
    var width = $("#info_panel").width();
    $("#place_info").css('marginLeft', width).show();
    $(".hide_place").click(hidePlaceInfo);

    var currentPlace = null;
    var placeInfoVisible = false;
    var currentPin = null;

    function flashPlaceInfo(place) {
        var element = $('#place_info');
        if (currentPlace == place) return;
        if (placeInfoVisible) {
            hidePlaceInfo(function() {
                populatePlaceInfo(place);
                showPlaceInfo();
            });
        }
        else {
            populatePlaceInfo(place);
            showPlaceInfo();
        }
    }
    function hidePlaceInfo(callback) {
      if (currentPin != null) currentPin.setIcon(placePinImage);
        var element = $('#place_info');
        if (!placeInfoVisible) return;
        currentPlace = null;
        placeInfoVisible = false;
        element.animate({
            marginLeft: parseInt(element.outerWidth())
        },
        callback);
    }
    function showPlaceInfo() {
        var element = $('#place_info');
        if (placeInfoVisible) return;
        placeInfoVisible = true;
        element.animate({
            marginLeft: 0
        });
    }
    function populatePlaceInfo(place) {
        currentPlace = place;
        $("#info_menu_items dl").empty();
        $("#info_title h2 span").text(place.fields.name);
        $(".yelp_link").attr('href', place.fields.yelp_url);
        $("#yelp_rating_img").attr('src', place.fields.yelp_image_rating_url);
        $("#info_rating p").text(place.fields.yelp_review_count + ' ratings');
        $("#info_address p").text(place.fields.location);
        $("#info_phone_number").text(place.fields.yelp_phone_number);
        spinner.spin(document.getElementById('menu_items_spinner'));
        if (place.fields.description != '') {
            $("#info_restaurant_notes h3").text('Restaurant Notes:');
            $("#info_restaurant_notes p").text(place.fields.description);
        }
        else {
          $("#info_restaurant_notes h3").text('');
          $("#info_restaurant_notes p").text('');
        }
        $.get("/menu_for_place", {
            'pk': place.pk
        },
        function(data) {
            spinner.stop();
            if (data.length < 1) {
                $("#info_menu_items dl").append("<dt>No menu items available</dt>")
            }
            data.map(function(menu_item) {
                $("#info_menu_items dl").append("<dt>" + menu_item.fields.name + "</dt><dd>" + menu_item.fields.description + "</dd>");
            })
        },
        "json");
    }
    function highlightPin(marker) {
      if (currentPin != null) currentPin.setIcon(placePinImage);
      currentPin = marker;
      currentPin.setIcon(highlightedPinImage);
    }
    function addMarkerFromJson(place) {

        var latLng = new google.maps.LatLng(place.fields.latitude, place.fields.longitude);
        var marker = new google.maps.Marker({
            position: latLng,
            map: map,
            title: place.fields.name,
            icon: placePinImage,
            shadow: pinShadow
        });
        var infowindow = new google.maps.InfoWindow({
            content: '<div class="place_info_window">'+place.fields.name+'</div>',
            maxWidth: 20
        });
        google.maps.event.addListener(marker, 'click',
        function() {
            flashPlaceInfo(place);
            highlightPin(marker);
            map.panTo(marker.getPosition());
        });
        var listEntry = $("<li><a href=#>" + place.fields.name + "<i class='icon-chevron-right pull-right' /></a></li>");
        listEntry.click(function() {
            flashPlaceInfo(place);
            highlightPin(marker);
            map.panTo(marker.getPosition());
        });
        $("#info_panel ul").append(listEntry);
        
    }

    $.get("/get_all_places",
    function(data) {
        data.map(addMarkerFromJson)
    },
    "json");
    var autocomplete_options = {
        types: ['establishment']
    };
    var autocomplete = new google.maps.places.Autocomplete(document.getElementById('add_place_input'), autocomplete_options);
    autocomplete.bindTo('bounds', map);
    google.maps.event.addListener(autocomplete, 'place_changed',
    function() {
        var place = autocomplete.getPlace();
        if (place) {
          $('#add_place_submit').removeClass('disabled');
        }
        else {
          $('#add_place_submit').addClass('disabled');
        }
    });

    $(document).on('keydown', '.new_menu_field',
    function() {
        var fieldsEmpty = true;
        $(".new_menu_field").each(function() {
            if (this.value != '') fieldsEmpty = false;
        });
        if (!fieldsEmpty) {
            $(".new_menu_field").removeClass("new_menu_field");
            $(".add_menu").append('<input class="new_menu_field menu_item" type="text" placeholder="Another menu item...">');
            $(".add_menu").append(' <input class="new_menu_field menu_item_description" type="text" placeholder="Comments/Notes">');
        }
    }
    );

    $("#add_place_submit").click(function(event) {
        event.preventDefault();
        var place = autocomplete.getPlace();
        if (place) {
            var menuItems = [];
            $('.menu_item:not(.new_menu_field)').each(function(index) {
                var name = this.value;
                if (name != '') {
                    var menuItem = {
                        'name': name
                    };
                    var description = $('.menu_item_description:not(.new_menu_field)')[index].value;
                    menuItem['description'] = description;
                    menuItems.push(menuItem);
                }
            });
            var postData = {
                'name': place.name,
                'location': place.formatted_address,
                'description': $('#add_place_description').val(),
                'menu_items': menuItems
            };
            console.log(postData);
            spinner.spin(document.getElementById('modal_spinner'));
            $.post("/add_place", JSON.stringify(postData), function() {
              console.log('add place returned');
              spinner.stop();
              location.reload();
            }, 'json');
        }
        else {
            console.log('nooo');
        }
    });
    $('a[data-dismiss="modal"]').click(function() {
        $(':input', '#add_place_form').val('').removeAttr('checked');
    });

});