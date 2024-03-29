let map;
let markers;

let geocoder;

let queryCenter; 
let queryZoom;

//When the user clicks on a marker, it will becom the selected icon:
var selectedMarker = null;
let selectedMarkerPopup, Popup;

var Cafe_ICON = {
  url: "http://maps.google.com/mapfiles/kml/shapes/coffee.png"
}

var Mentor_DEFAULT_ICON = {
  url: "http://maps.google.com/mapfiles/kml/paddle/pink-blank.png"
}

var Mentor_SELECTED_ICON = {
  url: "http://maps.google.com/mapfiles/kml/paddle/pink-stars.png"
}

var Learner_DEFAULT_ICON = {
  url: "http://maps.google.com/mapfiles/kml/paddle/grn-blank.png"
}

var Learner_SELECTED_ICON = {
  url: "http://maps.google.com/mapfiles/kml/paddle/grn-stars.png"
}

var Myself_ICON = {
  url: "http://maps.google.com/mapfiles/kml/paddle/blu-blank.png"
}

var Myself_SELECTED_ICON = {
  url: "http://maps.google.com/mapfiles/kml/paddle/blu-stars.png"
}

function initMap() {
  console.log('InitMap')
  
  geocoder = new google.maps.Geocoder();

  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 52.5200, lng: 13.4050 }, 
    zoom: 11,
    minZoom: 6,
    maxZoom: 19,
    // disabling some controls. Reference: https://developers.google.com/maps/documentation/javascript/controls
    streetViewControl: false, 
    fullscreenControl: false,
    mapTypeControl: false,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  });

  google.maps.event.addListener(map, 'idle', function(){
    var newZoom = map.getZoom();
    var newCenter = map.getCenter();

    console.log("Map  event triggers, zoom:"+newZoom+", center: "+newCenter);

    // We want to avoid re-rendering the markers if the change
    // in position within the map is too small. Also, if we are zooming in
    // without changing the center significantly, there is also no need
    // to call the backend again for new points
    var distanceChange = (queryCenter == null) ? 0 : google.maps.geometry.spherical.computeDistanceBetween (queryCenter, newCenter);

    if (queryCenter == null || queryZoom == null || distanceChange > 100 || newZoom < queryZoom) {
      refreshMarkers(newCenter, newZoom);
    }  
  });

    // A customized popup on the map.
    Popup = class Popup extends google.maps.OverlayView {
      position;
      containerDiv;
      constructor(position, contentText) {
        super();
        this.position = position;
        
        // This zero-height div is positioned at the bottom of the bubble.
        const bubbleAnchor = document.createElement("div");
        const content = document.createElement("div");
        content.classList.add("popup-bubble");
        content.setAttribute('id', 'popup-bubble')
        content.innerHTML = contentText;

        bubbleAnchor.classList.add("popup-bubble-anchor");
        bubbleAnchor.appendChild(content);
        
        // const close_button= document.createElement('button')
        // close_button.type = 'button'
        // close_button.innerText = "X"
        // close_button.setAttribute('id', 'close_button')
        // content.appendChild(close_button)

        // This zero-height div is positioned at the bottom of the tip.
        this.containerDiv = document.createElement("div");
        this.containerDiv.classList.add("popup-container");
        this.containerDiv.appendChild(bubbleAnchor);
        // Optionally stop clicks, etc., from bubbling up to the map.
        Popup.preventMapHitsAndGesturesFrom(this.containerDiv);
      }
      /** Called when the popup is added to the map. */
      onAdd() {
        this.getPanes().floatPane.appendChild(this.containerDiv);
      }
      /** Called when the popup is removed from the map. */
      onRemove() {
        if (this.containerDiv.parentElement) {
          this.containerDiv.parentElement.removeChild(this.containerDiv);
        }
      }
      /** Called each frame when the popup needs to draw itself. */
      draw() {
        const divPosition = this.getProjection().fromLatLngToDivPixel(
          this.position
        );
        // Hide the popup when it is far out of view.
        const display =
          Math.abs(divPosition.x) < 4000 && Math.abs(divPosition.y) < 4000
            ? "block"
            : "none";

        if (display === "block") {
          this.containerDiv.style.left = divPosition.x + "px";
          this.containerDiv.style.top = divPosition.y + "px";
        }

        if (this.containerDiv.style.display !== display) {
          this.containerDiv.style.display = display;
        }
      }
      close(){
          this.containerDiv.remove()
      }
    }
  }

var radiusToZoomLevel = [
  800000, // zoom: 0
  800000, // zoom: 1
  800000, // zoom: 2
  800000, // zoom: 3
  800000, // zoom: 4
  800000, // zoom: 5 
  800000, // zoom: 6
  400000, // zoom: 7
  200000, // zoom: 8
  100000, // zoom: 9
  51000, // zoom: 10
  26000, // zoom: 11
  13000, // zoom: 12
  6500, // zoom: 13
  3500, // zoom: 14
  1800, // zoom: 15
  900, // zoom: 16
  430, // zoom: 17
  210, // zoom: 18
  120,  // zoom: 19
];

// When refreshing the page
function refreshMarkers(mapCenter, zoomLevel) {
  console.log("refreshing markers")
  //Update query cener and zoom so we know in referenec to what
  //we queried for markers the last time and can decide if a re-query is needed
  queryCenter = mapCenter;
  queryZoom = zoomLevel;

  // If we had already some markers in the map, we need to clear them
  clearMarkers();

  // This will helpt to understand the radius, its for debug only
  //createCircle(mapCenter,radiusToZoomLevel[zoomLevel]);

  // we call the backend to get the list of markers
  var params = {
    "lat" : mapCenter.lat(),
    "lng" : mapCenter.lng(),
    "radius" : radiusToZoomLevel[zoomLevel]
  }
  var url = "/api/get_items_in_radius?" + dictToURI(params) 
  console.log(url)

  loadJSON(url, function(response) {
    // Parse JSON string into object
    var response_JSON = JSON.parse(response);
    if (!response_JSON.success) {
      // something failed in the backed serching for the items
      console.log("/api/get_items_in_radius call FAILED!")
      return
    }  
    
    // place new markers in the map
    placeItemsInMap(response_JSON.results)
    });
  }
  
  function placeItemsInMap(items) {
    // Add some markers to the map.
    // Note: The code uses the JavaScript Array.prototype.map() method to
    // create an array of markers based on the given "items" array.
    // The map() method here has nothing to do with the Google Maps API.
    markers = items.map(function(item, i) {
      var marker = new google.maps.Marker({
        map: map,
        position: item.location
      });
      
      if (item.learner_or_mentor === "Learner") {
        marker.setIcon(Learner_DEFAULT_ICON)
      } else if(item.learner_or_mentor === "Mentor"){
        marker.setIcon(Mentor_DEFAULT_ICON)
      } else {
        marker.setIcon(Cafe_ICON)
      }
      
      //we attach the item to the marker, so when the marker is selected
      //we can get all the item data to fill the highlighted profile box under
      // the map 
      marker.profile = item;
      // console.log(item)
      
      google.maps.event.addListener(marker, 'click', function(evt) {
        markerClick(this);
      });
      return marker;
    });
  }
  
// show all markers
let button_on = document.getElementById('filter_all')
button_on.addEventListener('click', showAllMarkers)

function showAllMarkers() {
  if (markers) {
    console.log(markers)
    markers.map(function(marker, i) {
      marker.setVisible(true);
    });
  }
}

// Show only learner markers
let filter_learner_marker = document.getElementById('filter_learner_marker')
filter_learner_marker.addEventListener('click', hide_mentor_Markers)

function hide_mentor_Markers() { // hide_mentor_cafe_Markers
  showAllMarkers();
  if (markers) {
    console.log(markers)
    markers.map(function(marker, i) {
      let learner_or_marker = marker.profile.learner_or_mentor 
      let cafe_detail = marker.profile.cafe_detail 
      // let cafe_marker = marker.profile.pet_friendly 
      // if (typeof(cafe_marker) === Boolean)  {
        if (learner_or_marker === 'Mentor' || typeof(cafe_detail) === "object") 
        marker.setVisible(false);
      });
    }
  }
  
// Show only Mentor markers
let filter_mentor_marker = document.getElementById('filter_mentor_marker')
filter_mentor_marker.addEventListener('click', hide_learner_Markers)

function hide_learner_Markers() {
  showAllMarkers();
  if (markers) {
    markers.map(function(marker, i) {
      let learner_or_marker = marker.profile.learner_or_mentor 
      let cafe_detail = marker.profile.cafe_detail 
      if (learner_or_marker === 'Learner' || typeof(cafe_detail) === "object")
      marker.setVisible(false);
    });
  }
}

//Show only cafe markers
let filter_cafe_marker = document.getElementById('filter_cafe_marker')
filter_cafe_marker.addEventListener('click', hide_learner_Mentor_Markers)

function hide_learner_Mentor_Markers() {
  showAllMarkers();
  if (markers) {
    markers.map(function(marker, i) {
      let learner_or_marker = marker.profile.learner_or_mentor 
      if (learner_or_marker === 'Learner' || learner_or_marker === 'Mentor') 
        marker.setVisible(false);
    });
  }
}

function clearMarkers() {
  if (markers) {
    markers.map(function(marker, i) {
      marker.setMap(null);
    });
  }
    
  markers = new Array();
  selectedMarker = null;
}

// サーチボックスに地名等を入れた時。不明瞭な地名だとelseをかえす
function searchAddressSubmit() {
  console.log('searchAddressSubmit');

  const address = document.getElementById("search_address").value;
  geocoder.geocode({ address: address }, (results, status) => {
    if (status === "OK") {
      // If you want to provide feedback to the user on the map page:
      //document.getElementById('addressHelpBlock').innerHTML="Perfect! Here are the results near you:";
      map.setZoom(15);
      map.setCenter(results[0].geometry.location);
    } else {
      console.log("Geocode was not successful for the following reason: " + status);
      // If you want to provide feedback to the user on the map page:
      //document.getElementById('addressHelpBlock').innerHTML="Sorry! That search did not work, try again!";
    }
  });

  //prevent refresh
  return false;
}



function markerClick(marker) {

  console.log('Marker clicked');
  console.log(336, marker.profile);
  
  // de-select the previously active marker, if present, When clicked the icon, the icon will be changed to the one with a star
  // selecetedMarker=nullなのでfalse
  let learner_or_mentor = marker.profile.learner_or_mentor
  if (learner_or_mentor === "Learner" || learner_or_mentor === "Mentor" ) {
    if (selectedMarker) {
      if(selectedMarker.profile.learner_or_mentor==='Learner' ){
        selectedMarker.setIcon(Learner_DEFAULT_ICON);
      } 
      if(selectedMarker.profile.learner_or_mentor==='Mentor'){
        selectedMarker.setIcon(Mentor_DEFAULT_ICON);
      }
    } 
    
    if(learner_or_mentor==='Learner'){
      marker.setIcon(Learner_SELECTED_ICON)
    } 
    if (learner_or_mentor==='Mentor') {
      marker.setIcon(Mentor_SELECTED_ICON)
    }

    let myself_name_database = document.getElementsByClassName("nav-link text-reset")[0].innerHTML
    let myself_name = marker.profile.user_name 
    console.log(myself_name)

    console.log(myself_name_database)
    if (myself_name_database.includes('Ayumi')) {
      marker.setIcon(Myself_SELECTED_ICON)
    }


   
  
    // remove the popup for the previously selected marker
    if (selectedMarkerPopup) {
      selectedMarkerPopup.setMap(null);
    }
    
    // update selected marker reference. Set a marker on the icon that is clicked right before
    selectedMarker = marker;
  
    // Show popup for the clicked marker
    selectedMarkerPopup = new Popup(
      selectedMarker.position,
      `<a href='/detail?id=${selectedMarker.profile.id}'>
      <li>${selectedMarker.profile.user_name}</li>
      </a>`
    );
    selectedMarkerPopup.setMap(map);

      // <li>${selectedMarker.profile.learner_or_mentor}</li>
      // <li>${selectedMarker.profile.language_learn}</li>
      // <li>${selectedMarker.profile.language_speak}</li>
      // <li>I want to chat ${selectedMarker.profile.online_inperson}</li>
      
    map.addListener('click',function(){
      selectedMarkerPopup.setMap(null);
      if(learner_or_mentor === "Learner"){
        selectedMarker.setIcon(Learner_DEFAULT_ICON);
      } 
      if(learner_or_mentor === "Mentor"){
        selectedMarker.setIcon(Mentor_DEFAULT_ICON);
      }
  });
    
  } else {  // below for cafe info

    // remove the popup for the previously selected marker
    if (selectedMarkerPopup) {
      selectedMarkerPopup.setMap(null);
    }
    
    // update selected marker reference. クリックしたアイコンの前のアイコンにmakerを設定
    selectedMarker = marker;
    console.log(selectedMarker)

    // Show popup for the clicked marker for cafe
    selectedMarkerPopup = new Popup(
      selectedMarker.position,
      `
      <li style=display:block">${selectedMarker.profile.address_cafe}</li>
      <li style=display:block"> ${selectedMarker.profile.cafe_detail}</li>
      `
      );
      selectedMarkerPopup.setMap(map);
      console.log(selectedMarker.profile)
      
      // `<a href='/detail?id=${selectedMarker.profile.id}'></a>

    map.addListener('click',function(){
      let cafe_quiet = selectedMarker.profile.quiet
      selectedMarkerPopup.setMap(null);
      if (cafe_quiet){
        selectedMarker.setIcon(Cafe_ICON);
      }
    });
  }
}





// window.addEventListener('DOMContentLoaded', function(){
//   const a = document.getElementById('close_button')
//   console.log(a)
//   a.addEventListener('click', function(){
//     console.log(123)
//   })
// });

// });
// let abc = document.getElementById('filter_all')
// let abc = document.getElementById('close_button')
// ;


// this is just for debugging purposes!
// To be able to better understand if the radius in which I search for 
// teachers is well adjussted to the level of zoom of the map, 
// I add this function to draw a circle showing the radius
function createCircle(latLng,radius) {
	options = getDefaultDrawingOptions();

	options['map']=map;
	options['center']=latLng;
	options['radius']=radius;

	var circle = new google.maps.Circle(options);
	circle.drawing_type = "circle";
}

function getDefaultDrawingOptions() {
  options = new Array();
  options['strokeColor']  = "#000000";
  options['strokeOpacity'] = 0.8;
  options['strokeWeight'] = 2;
  options['fillOpacity'] = 0;
  options['geodesic'] = false;
  options['editable'] = false;
  options['draggable'] = false;
	
	return options;
}

function loadJSON(url, callback) {   
  var xobj = new XMLHttpRequest();
  
  xobj.overrideMimeType("application/json");
  xobj.open('GET', url, true); 
  xobj.onreadystatechange = function () {
        if (xobj.readyState == 4 && xobj.status == "200") {
          // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
          callback(xobj.responseText);
        }
        //TODO: what to do in case of failures?
  };
  xobj.send(null);  
}

function dictToURI(dict) {
  var str = [];
  for(var p in dict){
     str.push(encodeURIComponent(p) + "=" + encodeURIComponent(dict[p]));
  }
  return str.join("&");
}


