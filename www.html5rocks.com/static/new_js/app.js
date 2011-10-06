// +1 buttons.

(function() {
  var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
  po.src = 'https://apis.google.com/js/plusone.js';
  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
})();

// Page header pulldowns.

$('#search_show').click(function(){
  $('.subheader.features').hide();
  $('#features_show').removeClass('current');
  $('#search_show').addClass('current');
  $('.subheader.search').show();
  $('#q').focus();
});

$('#search_hide').click(function(){
  $('.subheader.search').hide();
  $('#search_show').removeClass('current');
});

$('#features_show').click(function(){
  $('.subheader.search').hide();
  $('#search_show').removeClass('current');
  $('#features_show').addClass('current');
  $('.subheader.features').show();
});

$('#features_hide').click(function(){
  $('#features_show').removeClass('current');
  $('.subheader.features').hide();
});

$('.subheader.features ul li a').click(function(){
  $('#features_show').removeClass('current');
  $('.subheader.features').slideUp();
});

// Page grid builder

function buildPageAndScrollThere()
{
  var newPage = $('<div class="page" id="feature-offline"></div>');

  $(newPage).html('new content!').css({'position': 'absolute', 'top': '3000px', 'left': '3000px', 'font-size': '48px', 'color': '#fff'});

  $('body').append(newPage);

  $(newPage).load('features/offline .page', function(){
    $.scrollTo({top:'3000px', left:'3000px'}, 800, {queue:true});
  });
}