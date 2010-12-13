$(function() {
  console.log("run ning");
  $(".profile").click(function() {
    console.log("clicked");
    $(".profile").removeClass("active");
    $(this).addClass("active");
  });
});
