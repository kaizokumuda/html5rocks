$(function() {

  $(".profile").click(function(ev) {
    $(this).toggleClass("active");
    $(".profile").not(this).removeClass("active");
    return false;
  });

  $(window).hashchange( function(){
    $(".profile").removeClass("active");
    $("[data-profile-id='"+location.hash+"']").addClass("active");
  })
  $(window).hashchange(); // run on page load

});
