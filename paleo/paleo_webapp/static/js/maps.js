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
    function getSpinner() {
        return new Spinner({
            lines: 10,
            length: 3,
            width: 2,
            radius: 4,
            color: '#000',
            speed: 3,
            trail: 60,
            shadow: false,
            hwaccel: false,
            className: 'spinner',
            zIndex: 2e9,
            top: 0,
            left: 8
        });
    }
    getSpinner().spin(document.getElementById('yelp_spinner'));
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
        $("#info_rating").hide();
        $("#info_phone_number").hide();
        $("#loading_yelp_results").show();
        $("#info_menu_items dl").empty();
        $("#info_title h2 span").text(place.fields.name);
        $("#info_address p").text(place.fields.location);
        $.ajax({
          url: '/get_yelp_url',
          type: 'post',
          cache: true,
          data: {'business_pk' : place.pk, 'yelp_id' : place.fields.yelp_id},
          dataType: 'json',
          error: function(data) {
            $("#info_rating p").text('Yelp reviews could not be retrieved at this time');
            $("#info_rating").show();
          },
          success: function(data) {
            if (! ('error' in data)) {
              $.ajax({
                  'url': data.yelp_url,
                  'cache': true,
                  'dataType': 'jsonp',
                  'jsonpCallback': 'cb',
                  'success': function(yelp_data, textStats, XMLHttpRequest) {
                      if (currentPlace == place) {
                          $(".yelp_link").attr('href', yelp_data.url);
                          $("#yelp_rating_img").attr('src', yelp_data.rating_img_url_small);
                          var reviewPlural = (yelp_data.review_count == '1' ? ' review' : ' reviews');
                          $("#info_rating p").text(yelp_data.review_count + reviewPlural);
                          var phone = yelp_data.display_phone;
                          if (phone.indexOf("+") == 0) {
                            phone = phone.slice(phone.indexOf("-")+1, phone.length);
                          }
                          $("#info_phone_number span").text(phone);
                          $("#info_phone_number").show();
                          $("#loading_yelp_results").hide();
                          $("#info_rating").show();
                      }
                  }
              });
            }
            else {
              $("#info_rating p").text('Yelp reviews could not be retrieved at this time');
              $("#info_rating").show();
            }

          }
        });

        var spinner = getSpinner()
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
            'chain_pk': place.fields.chain
        },
        function(data) {
            spinner.stop();
            if (data.length < 1) {
                $("#info_menu_items dl").append("<dt id='no_menu_items'>No menu items available</dt>")
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

    var placesWaitingList = [];
    var placesList = [];

    function addPlace(place, redraw, refresh) {
        placesWaitingList.push(place);
        if (redraw) {
            var addedPlaces = renderPage(refresh);
            if (addedPlaces && 'addedMarkers' in addedPlaces) {
              index = addedPlaces['addedMarkers'].length -1;
              var marker = addedPlaces['addedMarkers'][0];
              var place = addedPlaces['addedPlaces'][0];
              selectPlace(place, marker);
            }
        }
    }
    var markersArray = [];
    function deleteOverlays() {
        if (markersArray) {
            for (i in markersArray) {
                markersArray[i].setMap(null);
            }
            markersArray.length = 0;
        }
    }
    function selectPlace(place, marker) {
      flashPlaceInfo(place);
      highlightPin(marker);
      map.panTo(marker.getPosition());
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
        markersArray.push(marker);
        google.maps.event.addListener(marker, 'click',
        function() {
            selectPlace(place, marker);
        });
        var listEntry = $("<li><a href=#>" + place.fields.name + "<i class='icon-chevron-right pull-right' /></a></li>"); 
        listEntry.click(function() {
            selectPlace(place, marker);
        });
        $("#info_panel ul").append(listEntry);
        return marker;

    }
    function renderPage(refresh) {
        var addedPlaces = [];
        var addedMarkers = [];
        if (refresh) {
            $("#info_panel ul").empty();
            deleteOverlays();
            while (placesList.length > 0) {
                place = placesList.pop();
                placesWaitingList.push(place);
            }
        }
        while (placesWaitingList.length > 0) {
            place = placesWaitingList.pop();
            var marker = addMarkerFromJson(place);
            addedMarkers.push(marker);
            placesList.push(place);
            addedPlaces.push(place);
        }
        hidePlaceInfo();
        return {'addedPlaces': addedPlaces, 'addedMarkers' : addedMarkers};
    }

    $.get("/get_all_places",
    function(data) {
        data.map(function(place) {
            addPlace(place, false, false)
        });
        renderPage(true);
    },
    "json");
    var autocomplete_options = {
        types: ['establishment']
    };

    var alert_success = $("#alert_success");
    alert_success.css('top', -1 * alert_success.outerHeight());
    function showSuccessAlert(placeName) {
        alert_success.find("span").text(placeName);
        alert_success.animate({
            top: 0
        },
        function() {
            setTimeout(function() {
                alert_success.animate({
                    top: -1 * alert_success.outerHeight()
                });
            },
            2000);
        });
    }
    var alert_error = $("#alert_error");
    alert_error.css('top', -1 * alert_error.outerHeight());
    function showErrorAlert(placeName) {
        alert_error.find("span").text(placeName);
        alert_error.animate({
            top: 0
        },
        function() {
            setTimeout(function() {
                alert_error.animate({
                    top: -1 * alert_error.outerHeight()
                });
            },
            2000);
        });
    }


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
          place.latitude 
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
                'latitude': place.geometry.location.Ua,
                'longitude': place.geometry.location.Va,
                'description': $('#add_place_description').val(),
                'is_chain': $('#is_chain_checkbox').is(':checked'),
                'menu_items': JSON.stringify(menuItems)
            };
            var spinner = getSpinner();
            spinner.spin(document.getElementById('modal_spinner'));
            $.ajax({
                url: "/add_place",
                type: "post",
                data: postData,
                dataType: "json",
                error: function(data) {
                    showErrorAlert(place.name);
                },
                success: function(data) {
                    if (! ('error' in data)) {
                      var places = data.places;
                      for (var i=places.length-1; i>0; i--) {
                        var returned_place = places[i];
                        addPlace(returned_place, false, false);
                      }
                      addPlace(places[0], true);
                      showSuccessAlert(places[0].fields.name);
                    }
                    else {
                        showErrorAlert(place.name);
                    }
                },
                complete: function() {
                    spinner.stop();
                    $('#addPlaceModal').modal('hide');
                    $(':input', '#add_place_form').val('').removeAttr('checked');
                }
            });
        }
        else {
            console.log('nooo');
        }
    });
    $('#addPlaceModal').on('hidden', function () {
      $(':input', '#add_place_form').val('').removeAttr('checked');
    });
    
    $('#why_chain').popover();
    
    $('.append_menu_item').on('keydown', function() {
      $('#append_menu_item_submit').removeClass('disabled')
      });
    $("#append_menu_item_submit").click(function() {
      var postData = {};
      postData['menu_item_name'] = $('#append_menu_item_name').val();
      postData['menu_item_description'] = $('#append_menu_item_description').val();
      postData['chain_pk'] = currentPlace.fields.chain;
      //ajax call
      $.ajax({
        url: "/add_menu_item",
        type: "post",
        data: postData,
        dataType: "json",
      });
      $("#no_menu_items").remove();
      $(':input', '#append_menu_item_form').val('').removeAttr('checked');
      $("#info_menu_items dl").append("<dt>" + postData['menu_item_name'] + "</dt><dd>" + postData['menu_item_description'] + "</dd>");
    });

});