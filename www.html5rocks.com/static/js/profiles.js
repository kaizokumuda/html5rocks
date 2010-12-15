$(function() {

  function updateHash() {
    $activeProfile = $(".active");
    if ($activeProfile.length) {
      location.hash = $activeProfile.attr("id");
    } else {
      if (typeof(window["history"])!="undefined")
        history.replaceState({}, document.title, "/profiles");
      else
        location.hash = "#"; // oh well, old browsers have to live with a #
    }
  }

  $(".profile").click(function(ev) {
    $(this).toggleClass("active");
    $(".profile").not(this).removeClass("active");
    updateHash();
    return false;
  });

  $(window).click(function(ev) {
    $(".profile").removeClass("active");
    updateHash();
  });

  window.onhashchange = function() {
    $(".profile").removeClass("active");
    if (!location.hash.length) return;
    var profileID = location.hash.substr(1);
    $("#"+profileID).addClass("active");
  };

  window.onhashchange(); // run on page load

});
