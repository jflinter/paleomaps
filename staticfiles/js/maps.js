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
        $("#info_title h2 span").text(place.name);
        $("#info_address p").text(place.location);
        $.ajax({
            url: '/get_yelp_url',
            type: 'post',
            cache: true,
            data: {
                'business_id': place.id,
                'yelp_id': place.yelp_id
            },
            dataType: 'json',
            error: function(data) {
                $("#info_rating p").text('Yelp reviews could not be retrieved. ');
                $(".yelp_link").attr('href', 'http://www.yelp.com/');
                $("#info_rating").show();
                $("#loading_yelp_results").hide();
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
                                var reviewPlural = (yelp_data.review_count == '1' ? ' review': ' reviews');
                                $("#info_rating p").text(yelp_data.review_count + reviewPlural);
                                var phone = yelp_data.display_phone;
                                if (phone.indexOf("+") == 0) {
                                    phone = phone.slice(phone.indexOf("-") + 1, phone.length);
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
                    $("#info_rating p").text('Yelp reviews could not be retrieved. ');
                    $(".yelp_link").attr('href', 'http://www.yelp.com/');
                    $("#info_rating").show();
                    $("#loading_yelp_results").hide();
                }

            }
        });

        var spinner = getSpinner()
        spinner.spin(document.getElementById('menu_items_spinner'));
        if (place.description != '') {
            $("#info_restaurant_notes h3").text('Restaurant Notes:');
            $("#info_restaurant_notes p").text(place.description);
        }
        else {
            $("#info_restaurant_notes h3").text('');
            $("#info_restaurant_notes p").text('');
        }
        $.get("/menu_for_place", {
            'chain_name': place.chain
        },
        function(data) {
            spinner.stop();
            if (data.length < 1) {
                $("#info_menu_items dl").append("<dt id='no_menu_items'>No menu items available</dt>")
            }
            data.map(function(menu_item) {
                $("#info_menu_items dl").append("<dt>" + menu_item.name + "</dt><dd>" + menu_item.description + "</dd>");
            })
        },
        "json");
    }
    function highlightPin(marker) {
        if (currentPin != null) currentPin.setIcon(placePinImage);
        currentPin = marker;
        currentPin.setIcon(highlightedPinImage);
    }

    function addPlaceAndDraw(place, select) {
        var marker = addMarkerFromJson(place);
        if (select) {
            selectPlace(place, marker);
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
        var place_location = place.latlng;
        var latLng = new google.maps.LatLng(place_location.latitude, place_location.longitude);
        var marker = new google.maps.Marker({
            position: latLng,
            map: map,
            title: place.name,
            icon: placePinImage,
            shadow: pinShadow
        });
        markersArray.push(marker);
        google.maps.event.addListener(marker, 'click',
        function() {
            selectPlace(place, marker);
        });
        var listEntry = $("<li><a href=#>" + place.name + "<i class='icon-chevron-right pull-right' /></a></li>");
        listEntry.click(function() {
            selectPlace(place, marker);
        });
        $("#info_panel ul").append(listEntry);
        return marker;

    }

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
                        var google_id = data['place_id'];
                        initializeMap(function(place) {
                            return (place.google_id == google_id);
                        });
                        showSuccessAlert(place.name);
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
    $('#addPlaceModal').on('hidden',
    function() {
        $(':input', '#add_place_form').val('').removeAttr('checked');
    });

    $('#why_chain').popover();

    $('.append_menu_item').on('keydown',
    function() {
        $('#append_menu_item_submit').removeClass('disabled')
    });
    $("#append_menu_item_submit").click(function() {
      
        var postData = {};
        postData['menu_item_name'] = $('#append_menu_item_name').val();
        postData['menu_item_description'] = $('#append_menu_item_description').val();
        postData['chain_name'] = currentPlace.chain;
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

    var currentLatLng = {
        latitude: 34.038058,
        longitude: -118.468677
    };
    function location_success(position) {
        var latLng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
        currentLatLng.latitude = position.coords.latitude;
        currentLatLng.longitude = position.coords.longitude;
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

    function location_error(msg) {
        var latLng = new google.maps.LatLng(34.038058, -118.468677);
        map.panTo(latLng)
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(location_success, location_error);
    } else {
        location_error();
    }
    
    var locationSortedPlaceList = [];
    var nameSortedPlaceList = [];
    var sortMethod = "LOCATION";
    
    function drawPlaces(places, shouldHighlightFunction) {
      if (!shouldHighlightFunction) shouldHighlightFunction = function() {
          return false
      };
      $("#info_panel ul").empty();
      deleteOverlays();
      for (var i = 0; i < places.length; i++) {
          var shouldHighlight = shouldHighlightFunction(places[i]);
          addPlaceAndDraw(places[i], shouldHighlight);
      }
    }
    function initializeMap(shouldHighlightFunction) {
        $.ajax({
            url: "/get_all_places",
            type: "get",
            data: {
                latitude: currentLatLng.latitude,
                longitude: currentLatLng.longitude
            },
            dataType: "json",
            success: function(data) {
              locationSortedPlaceList = data;
              nameSortedPlaceList = data.slice(0);
              nameSortedPlaceList.sort(function(a,b){
                if (a.name > b.name) return 1;
                return -1;
              });
              if (sortMethod == "NAME") {
                drawPlaces(nameSortedPlaceList, shouldHighlightFunction);
              }
              else {
                drawPlaces(locationSortedPlaceList, shouldHighlightFunction);
              }
            }
        });
    }
    initializeMap();
    
    $(".sortPlaceRadio").change(function() {
      if (sortMethod != "NAME") {
        sortMethod = "NAME";
        drawPlaces(nameSortedPlaceList);
      }
      else if (sortMethod != "LOCATION") {
        sortMethod = "LOCATION";
        drawPlaces(locationSortedPlaceList);
      }
    });

});