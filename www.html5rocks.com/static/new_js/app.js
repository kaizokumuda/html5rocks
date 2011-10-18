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

$('#search_show').click(function() {
  $('#features_hide').click(); // Hide features panel if it's out.

  if ($(this).hasClass('current')) {
    $('.subheader.search').hide();
    $(this).removeClass('current');
  } else {
    $('nav.main .current').removeClass('current');
    $(this).addClass('current');
    $('.subheader.search').show();
    $('#q').focus();
  }
});

$('#search_hide').click(function() {
  $('#search_show').removeClass('current');
  $('.subheader.search').hide();
});

$('#features_show').click(function() {
  $('#search_hide').click(); // Hide search panel if it's out.

  if ($(this).hasClass('current')) {
    $('.subheader.features').hide();
    $(this).removeClass('current');
  } else {
    $('nav.main .current').removeClass('current');
    $(this).addClass('current');
    $('.subheader.features').show();
  }
});

$('#features_hide').click(function() {
  $('#features_show').removeClass('current');
  $('.subheader.features').hide();
});

$('.subheader.features ul li a').click(function() {
  $('nav.main .current').removeClass('current');
});

// Page grid navigation.

$('a').click(function() {
  // Don't intercept external links
  if ($(this).attr('target')) {
    return true;
  }

  window.page = this.pathname
                  // remove locale
                  .replace(/\/\w{2,3}\//gi, '')
                  // slashes to dashes
                  .replace(/\/([A-Za-z]+)/gi, '-$1')
                  // remove trailing slashes and initial dashes
                  .replace(/(\/$)|(^-)/g, '');

  $('body').removeClass().attr('data-href', page);
  $('.page').removeClass('current');

  window.pagePanel = $('.page#' + page);

  if (pagePanel.hasClass('loaded')) {
    pagePanel.addClass('current');
  } else {
    pagePanel
      .addClass('current loaded')
      .load($(this).attr('href') + ' article', function(){
        $('.subheader.features').slideUp();
        route.init(page);
      });

  }

  /*$('.page#' + page).addClass('current').load($(this).attr('href') + ' .page', function() {
    $.scrollTo($('page#' + page), 800, {queue:true});
  });*/

  // TODO(Google): record GA hit on new ajax page load.
  // TODO(paulirish): add window.history.pushState

  return false;
});

$(document).keydown(function(e) {
  currentId = $('.current').attr('id');
  if (e.keyCode == 39) {
    nextPage = $('.current').next();
    nextPage.html('<p style="border: 4px solid red">Loading content...</p>');
    nextPage.addClass('next');
    nextPage.addClass('loaded');
    setTimeout(function() {
      $('.current').attr('class', $('.current').attr('class').replace(/current/, 'previous'));
      $('.page.next').attr('class', $('.page.next').attr('class').replace(/next/, 'current'));
    }, 10);
    
    $('.page.current').one('webkitTransitionEnd', function(e) {
      e.target.classList.remove('previous');
      $('.next').removeClass('next');
    });
  } else if (e.keyCode == 27) { // ESC
    $('#search_hide').click();
    $('#features_hide').click();
  }
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

// basic routing setup based on the global page variable
window.route = {
  "features" : function(){
    window.loadFeaturePanels && loadFeaturePanels();
  },

  // if 'features-offline' gets passed in we will execute both:
  // route['features']() && route['features-offline']()
  init : function(thing){
    var commonfn = route[thing.split('-')[0]],
        pagefn   = route[thing];
    route.fire(commonfn);
    if (pagefn != commonfn){
      route.fire(pagefn);
    }
  }, 
  fire : function(fn){
    if (typeof fn == 'function'){
      fn.call(route);
    }
  },
  onload : function(){
    // TODO(paulirish): be less hacky. just doing this to trigger our click handler above.
    $('<a>').attr('href', location.href).click();
  }
};

addEventListener('DOMContentLoaded', route.onload, false);