let markers = [];
let map = null;


// Using for new-location and add-cafe

function initAutocomplete() {
    map = new google.maps.Map(document.getElementById("map"), {
      center: { lat: 52.5200, lng: 13.4050 }, //We start at the center of Berlin
      zoom: 13,
      mapTypeId: "roadmap",
    });
    // Create the search box and link it to the UI element.
    const input = document.getElementById("address");
    const searchBox = new google.maps.places.SearchBox(input);
    
    // Bias the SearchBox results towards current map's viewport.
    map.addListener("bounds_changed", () => {
      
      // searchBox.setPlaces(map.getBounds());
      searchBox.setBounds(map.getBounds());
    });
    
    // Listen for the event fired when the user selects a prediction and retrieve
    // more details for that place.
    searchBox.addListener("places_changed", () => {
      const places = searchBox.getPlaces();
      
      if (places.length == 0) {
        return;
      }
      
      console.log('How many places did I get? '+ places.length)
      
      // We take only the first place and ignore the (possible) rest
      let place = places[0];
      console.log(place.name)
      
      if (!place.geometry || !place.geometry.location) {
        console.log("Returned place contains no geometry");
        return;
      }
      
      // console.log(places[0].html_attributions.name)
      placeMarker(place.geometry.location);
    });

    // Additionally, if the user clicks anywhere on the map, they create 
    // a Marker there
    google.maps.event.addListener(map, 'click', function(event) {
        placeMarker(event.latLng);
    });
}

function placeMarker(latLng) {
    // Clear out the old markers. We want at most one marker in the map at any given time
    markers.forEach((marker) => {
        marker.setMap(null);
    });
    markers = [];

    // Send the latitude and longitude of the found location 
    // into the Form hidden fields, so this data can reach the backend:
    updateFormCoordinates(latLng.lat(), latLng.lng());

    const icon = {
        url: "https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/geocode-71.png",
    };
  
    // Create a marker for this place.
    let newMarker = new google.maps.Marker({
        map,
        icon,
        position: latLng,
        draggable: true // this is a way to allow the user to re-position the marker if they wish
    })  
      
    // Because we created a draggable marker,
    // we need to define what happens after the user drags / repositions
    // the marker
    google.maps.event.addListener(newMarker, 'dragend', function (evt) {
        // If the user drags the marker,
        // the Form coordinates need to be updated
        updateFormCoordinates(evt.latLng.lat().toFixed(6), evt.latLng.lng().toFixed(6));
        map.panTo(evt.latLng);
    });

    // We add newMarker to the markers list
    // so it can be cleared before a new marker can be added
    // (remember we want to ensure only a single marker in the map)
    markers.push(
        newMarker
    );
    
    // Move the map center to this coordinate
    map.panTo(latLng);    
}

function updateFormCoordinates(newLat, newLng) {
    console.log('Updating form coordinates to: '+newLat+' '+newLng);
    document.getElementById('coord_latitude').value = newLat;
    document.getElementById('coord_longitude').value = newLng;
}  

// depends on clicking learner/mentor, showing different questionaires
const learner = document.getElementById('learner_or_mentor-0')
const mentor = document.getElementById('learner_or_mentor-1')
const language_learn = document.getElementsByClassName('language_learn')
const language_skilled = document.getElementsByClassName('language_skilled')
const language_speak = document.getElementsByClassName('language_speak')
const how_long_experienced = document.getElementsByClassName('how_long_experienced')
const how_long_learning = document.getElementsByClassName('how_long_learning')
const online_inperson = document.getElementsByClassName('online_inperson')

learner.addEventListener('click', show_for_learner)
mentor.addEventListener('click', show_for_mentor)

function show_for_learner() {
  if(learner.checked) {
    console.log(12)
    language_learn[0].style.display ="block";
    language_skilled[0].style.display ="block";
    language_speak[0].style.display ="block";
    // how_long_experienced[0].style.display ="block";
    how_long_learning[0].style.display ="block";
    online_inperson[0].style.display ="block";
  } else {
    language_learn[0].style.display ="none";
    language_skilled[0].style.display ="none";
    language_speak[0].style.display ="none";
    // how_long_experienced[0].style.display ="none";
    how_long_learning[0].style.display ="none";
    online_inperson[0].style.display ="none";
    }
}

function show_for_mentor() {
  if(mentor.checked) {
    // language_learn[0].style.display ="block";
    language_skilled[0].style.display ="block";
    language_speak[0].style.display ="block";
    how_long_experienced[0].style.display ="block";
    // how_long_learning[0].style.display ="block";
    online_inperson[0].style.display ="block";
  } else {
    language_learn[0].style.display ="none";
    language_skilled[0].style.display ="none";
    language_speak[0].style.display ="none";
    how_long_experienced[0].style.display ="none";
    // how_long_learning[0].style.display ="none";
    online_inperson[0].style.display ="none";
    }
}
