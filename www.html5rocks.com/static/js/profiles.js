$(function() {
  $(".profile").click(function(ev) {
    $(this).toggleClass("active");
    $(".profile").not(this).removeClass("active");
    return false;
  });
});
