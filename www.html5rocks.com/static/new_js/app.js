// Page header pulldowns.

$('#search_show').click(function(){
  $('.subheader.features').hide();
  $('#features_show').removeClass('active');
  $('#search_show').addClass('active');
  $('.subheader.search').show();
  $('#q').focus();
});

$('#search_hide').click(function(){
  $('.subheader.search').hide();
});

$('#features_show').click(function(){
  $('.subheader.search').hide();
  $('#search_show').removeClass('active');
  $('#features_show').addClass('active');
  $('.subheader.features').show();
});

$('#features_hide').click(function(){
  $('#features_show').removeClass('active');
  $('.subheader.features').hide();
});

$('.subheader.features ul li a').click(function(){
  $('#features_show').removeClass('active');
  $('.subheader.features').slideUp();
});

// Page grid builder

function buildPageAndScrollThere()
{
  var newPage = $('<div id="newPage1"></div>');

  $(newPage).html('new content!').css({'position': 'absolute', 'top': '3000px', 'left': '3000px', 'font-size': '48px', 'color': '#fff'});

  $('body').append(newPage);

  $(newPage).load('features/offline')

  $.scrollTo({top:'3000px', left:'3000px'}, 800);
}