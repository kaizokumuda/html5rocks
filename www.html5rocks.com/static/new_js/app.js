// +1 buttons.

(function() {
  var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
  po.src = 'https://apis.google.com/js/plusone.js';
  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
})();

// Show header box shadow on scroll.
var docTop = $('html, body').offset().top;
$(window).bind('scroll', function(event) {
  var y = $(this).scrollTop();
  if ((y - docTop) > 100) {
   $('header').addClass('scroll');
  $(this).unbind('scroll', event.handler); // Remove this listen for performance. 
  }
});

// Page header pulldowns.

$('#search_show').click(function(){
  if($(this).hasClass('current'))
  {
    $('.subheader.search').hide();
    $(this).removeClass('current');
  }
  else
  {
    $('.subheader.search').hide();
    $('#features_show').removeClass('current');
    $(this).addClass('current');
    $('.subheader.search').show();
    $('#q').focus();
  }
});

$('#search_hide').click(function(){
  $('.subheader.search').hide();
  $('#search_show').removeClass('current');
});

$('#features_show').click(function(){
  if($(this).hasClass('current'))
  {
    $('.subheader.features').hide();
    $(this).removeClass('current');
  }
  else
  {
    $('#search_show').removeClass('current');
    $(this).addClass('current');
    $('.subheader.features').show();
  }
});

$('#features_hide').click(function(){
  $('#features_show').removeClass('current');
  $('.subheader.features').hide();
});

$('.subheader.features ul li a').click(function(){
  $('#features_show').removeClass('current');
  $('.subheader.features').slideUp();
});

// Page grid navigation.

$('a').click(function() {
  page = $(this).attr('href').substr($(this).attr('href').indexOf('/')).replace(/\/\w{2,3}\//gi, '').replace(/\/([A-Za-z]+)/gi, '-$1').replace(/\/$/, '').replace(/^-/, '');

  $('body').removeClass().attr('data-href', page);
  $('.page').removeClass('current');

  if ($('.page#' + page).hasClass('loaded'))
    $('.page#' + page).addClass('current');
  else
    $('.page#' + page).addClass('current loaded').load($(this).attr('href') + ' .page');

  // $('.page#' + page).addClass('current').load($(this).attr('href') + ' .page', function(){
  //   $.scrollTo($('page#' + page), 800, {queue:true});
  // });

  return false;
});


// Features navigation.

// Toggle the feature nav.
$('.features_outline_nav_toggle').click(function(){
  $(this).toggleClass('activated');
  $('nav.features_outline').fadeToggle('fast');
});

// A feature is clicked.
$('nav.features_outline a.section_title').click(function(){
  if ($(this).parent('li').hasClass('current'))
  {
    $(this).parent('li').removeClass('current');
    $(this).siblings('ul').slideUp('fast');
  }
  else
  {
    $('nav.features_outline li').removeClass('current');
    $('nav.features_outline a.section_title').siblings('ul').slideUp('fast');
    $(this).parent('li').addClass('current');
    $(this).siblings('ul').slideDown('fast');
  }
});