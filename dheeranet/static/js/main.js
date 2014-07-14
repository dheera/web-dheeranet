/*    
@licstart  The following is the entire license notice for the 
JavaScript code in this page.

Copyright (C) Dheera Venkatraman (dheera@dheera.net)

The JavaScript code in this page is free software: you can
redistribute it and/or modify it under the terms of the GNU
General Public License (GNU GPL) as published by the Free Software
Foundation, either version 3 of the License, or (at your option)
any later version.  The code is distributed WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU GPL for more details.

As additional permission under GNU GPL version 3 section 7, you
may distribute non-source (e.g., minimized or compacted) forms of
that code without the copy of the GNU GPL normally required by
section 4, provided you include this license notice and a URL
through which recipients can access the Corresponding Source.   

@licend  The above is the entire license notice
for the JavaScript code in this page.
*/

$(document).ready(function() {
  $('.nodrag').mousedown(function(event){event.preventDefault();});
  $('.clickable').mouseenter(function(){$(this).addClass('clickable-hover');}).mouseleave(function(){$(this).removeClass('clickable-hover');}).mousedown(function(event){event.preventDefault();});
  $('.navbar-mobile-button').click(function(){
    $(this).toggleClass('is-active');
    $('.navbar-mobile-container').slideToggle();
  });
  $('.like-buttons img').mouseenter(function(){$(this).addClass('like-buttons-hover');}).mouseleave(function(){$(this).removeClass('like-buttons-hover');}).mousedown(function(event){event.preventDefault();});
  $('.photos-like-container')
    .mouseenter(function(){
      $(this).children('.photos-like-text').transition({'top':'-140px','duration':200});
      $(this).children('.photos-like-buttons').transition({'top':'0px','duration':200});
    })
    .mouseleave(function(){
      $(this).children('.photos-like-text').transition({'top':'0px','duration':200});
      $(this).children('.photos-like-buttons').transition({'top':'140px', 'duration':200});
    })
    .mousedown(function(event){
      event.preventDefault();}
    );
  $('.photos-thumbnail-container')
    .mouseenter(function(){
      $(this).addClass('clickable-hover');
      $(this).children('.photos-thumbnail-download').css('opacity',1);
    })
    .mouseleave(function(){
      $(this).removeClass('clickable-hover');
      $(this).children('.photos-thumbnail-download').css('opacity',0);
    })
    .mousedown(function(event){
      event.preventDefault();}
    );
  $(".photos-thumbnail").swipebox({useCSS:true});
  $(".photos-thumbnail-mobile").swipebox({useCSS:true});
  $('.photos-album').mouseleave(function(){
    $(this).children('.photos-album-description').css('opacity','0');
  });
  $('.photos-album').mouseenter(function(){
    $(this).children('.photos-album-description').css('opacity','0.85');
  });

  if(window.location.hash.length>2) {
    $('#'+window.location.hash.replace('.jpg','').replace(/[^A-Za-z0-9_\.\-]/g,'')).click();
  }

  $(window).bind('hashchange', onHashChange);

});

// hack to be able to change hashes without triggering hashchange event
var oldHash = window.location.hash;

function changeHash(newHash) {
  // prevent triggering of onHashChange code
  oldHash = newHash;
  window.location.hash = newHash;
}

function onHashChange() {
  // check if hash really changed (or if we set it manually, do nothing)
  var newHash = window.location.hash;
  if(oldHash !== newHash) {
    $('#swipebox-close').click();
    if(newHash.length>1) {
      $('#' + newHash.replace('.jpg','').replace(/[^A-Za-z0-9_\.\-]/g,'')).click();
    }
  }
  oldHash = newHash;
}

var isHDDisplay = window.devicePixelRatio > 1;
var cssTransitionsSupported = false;
(function() {
    var div = document.createElement('div');
    div.innerHTML = '<div style="-webkit-transition:color 1s linear;-moz-transition:color 1s linear;"><\/div>';
    cssTransitionsSupported = (div.firstChild.style.webkitTransition !== undefined) || (div.firstChild.style.MozTransition !== undefined);
    delete div;
})();

(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)})(window,document,'script','//www.google-analytics.com/analytics.js','ga');ga('create', 'UA-52351633-1', 'auto');ga('send', 'pageview');
