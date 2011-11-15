// Navigation highlighting.

$('.main nav ul li a').click(function() {
  $('.main nav .current').removeClass('current');
  setTimeout("$('.watermark').css('top', '30px')", 1000);
});

$('.subheader.features ul li a').click(function() {
  $('.main nav .current').removeClass('current');
  setTimeout("$('.watermark').css('top', '30px')", 1000);
});


// Page grid navigation.

function finishPanelLoad(pagePanel, elemstate) {
  if (pagePanel.hasClass('next')) {
    pagePanel.removeClass('next');
    pagePanel.prev().addClass('previous');
  } else if (pagePanel.hasClass('previous')) {
    pagePanel.removeClass('previous');
    pagePanel.next().addClass('next');
  }
  $('.page').removeClass('current');
  pagePanel.addClass('current');

  // TODO(Google): scrollTo needs to scroll to and element that is not display:none.
  // base.css applies this to .page elements. Not sure why pagePanel.addClass('current')
  // doesn't take care of this.
  $.scrollTo(pagePanel, 600, {queue: true, offset: {top: -60, left: 0}, onAfter: function(){
    $('.subheader.features').slideUp('fast', function() {
      if (elemstate.popped != 'popped')
        state.push( elemstate );

      route.init(page);
    });
  }});
}

$(document).keydown(function(e) {
  var goFeature = '';
  var currentPage = $('.page.current');
  if (e.keyCode == 37) {
    goFeature = currentPage.prev().attr('id').replace(/features-/, '');
    currentPage.prev().addClass('previous')
  }
  if (e.keyCode == 39) {
    goFeature = currentPage.next().attr('id').replace(/features-/, '');
    currentPage.next().addClass('next')
  }
  if (goFeature) {
    currentPage.one('webkitTransitionEnd', function(e) {
      $('.page').removeClass('previous');
      $('.page').removeClass('next');
    });

    loadContent($('div.features a.' + goFeature)[0])
  }
});

//$('a').live('click', function() {
// TODO: go back to event delgation. Currently breaks nav.
$('a').click(function() {

  // Don't intercept external links
  if ($(this).attr('target')) {
    return true;
  }

  // Only cool browsers get cool behavior
  if (!Modernizr.history) return true;

  loadContent(this);

  return false;
});

function loadContent(elem, popped){

  window.page = elem.pathname
                  // remove locale
                  .replace(/\/\w{2,3}\//gi, '')
                  // slashes to dashes
                  .replace(/\/([A-Za-z]+)/gi, '-$1')
                  // remove trailing slashes and initial dashes
                  .replace(/(\/$)|(^-)/g, '')
                  // drop the hash
                  .split('#')[0];

  window.pagePanel =  $('.page#' + page);

  var href = elem.href;
  var hash = href.split('#')[1];
  var elemstate = {
    href: href,
    hash: hash,
    popped: popped,
    title: page[0].toUpperCase() + page.substring(1)
  };

  // Special case for homepage. Just redirect.
  if (page == '') {
    location.href = '/';
    return false;
  }

  $('body').attr('data-href', page);


  // If we have an anchor, just scroll to it on the current page panel.
  if (hash) {
    var panelSegment = pagePanel.find('.' + hash);
    if (panelSegment.length) {
      finishPanelLoad(panelSegment, elemstate);
    }
    return false;
  }

  if (pagePanel.hasClass('loaded')) {
    finishPanelLoad(pagePanel, elemstate);
  } else {
    pagePanel
      .addClass('loaded')
      .load(href + ' [data-import-html]', function() {
        finishPanelLoad(pagePanel, elemstate);
      });
  }

}; // eo loadContent()

$(document).keydown(function(e) {
  if (e.keyCode == 27) { // ESC
    // Hide search and/or feature bar.
    $('#search_hide, #features_hide').click();

    // Hide +/- feature navigation.
    $('.outline_nav_toggle').removeClass('activated');
    $('nav.features_outline').fadeOut('fast');
  }
});


// Features navigation.

// Toggle the feature nav.
$('.outline_nav_toggle').click(function(e) {
  $(this).toggleClass('activated');
  $(this).find('nav.outline').fadeToggle('fast');
});

// A feature is clicked.
$('nav.features_outline a.section_title').click(function(e) {
  if ($(this).parent('li').hasClass('current')) {
    $(this).parent('li').removeClass('current');
    $(this).siblings('ul').slideUp('fast');
  } else {
    $('nav.features_outline li').removeClass('current');
    $('nav.features_outline a.section_title').siblings('ul').slideUp('fast');
    $(this).parent('li').addClass('current');
    $(this).siblings('ul').slideDown('fast');
  }
  e.stopPropagation();
});

$('.main nav li a').click(function(e) {
  $('.main nav .current').removeClass('current');
  $(this).addClass('current');
});

// basic routing setup based on the global page variable
// everything happens on the `page` variable

// if it is equal to 'features-offline', then we will execute (in this order)
// route.common();
// route['features']();
// route['features-offline']();

window.route = {
  common : function() {
    gapi.plusone.go(pagePanel.find('.plusone').get(0));
    twttr.widgets.load();

    // TODO(Google): record GA hit on new ajax page load.
  },

  "features" : function() {
    window.loadFeaturePanels && loadFeaturePanels();
  },

  init : function(thing) {
    var commonfn = route[thing.split('-')[0]],
        pagefn   = route[thing];

    route.fire(route.common);
    route.fire(commonfn);
    if (pagefn != commonfn) {
      route.fire(pagefn);
    }
  },
  fire : function(fn) {
    if (typeof fn == 'function') {
      fn.call(route);
    }
  },
  onload : function() {

    // due to the funky templating, we output into the same div, but we
    // want to move it into "correct" DOM order (in base.html)
    var curelem = $('.page.current'),
        curid   = curelem[0].id;

    // Special case for the homepage and profiles.
    // Former prevents the DOM replacement causing a double load of the Y!
    // pipe feed.
    if (curid == 'home' || curid == 'profiles') {
      return false;
    }

    $('[id=' + curid + ']').eq(1).replaceWith(curelem);

    route.fire(route.features);
  }
};

window.addEventListener('DOMContentLoaded', route.onload, false);

window.state = {
  push : function(obj){
    if (!Modernizr.history) {
      return;
    }
    history.pushState(obj, '', obj.href);
    document.title = 'HTML5 Rocks - ' + obj.title;
  },

  popstate : function(e){
    if (!(e && e.state)) return;

    var elem = document.createElement('a');
    elem.href = e.state.href;

    document.title = 'HTML5 Rocks - ' + e.state.title;

    // trigger a click to kick off our navigation loop
    loadContent(elem, 'popped');
  },
  handleEvent : function(e){
    state[e.type].call(state, e);
  }

};

window.addEventListener('popstate', state, false);


$(document).ready(function() {
  $('.tag').live('click', filterTag);
  if (document.location.hash) {
    // Hide all samples as soon as DOM is loaded to prevent flicker effect.
    var samples = $('.tutorial_listing');
    samples.addClass('hidden');
    filterTag(document.location.hash.substring(1));
  }
});

function clearFilter() {
  $('.tutorial_listing.hidden').removeClass('hidden');
  $('.tag_filter input[type="text"]').val('');
  $('#updates_format_filter input[type="checkbox"]').attr('checked', false);
  $('#filter').parent().addClass('hidden');
  if (!!window.history) {
    var lang = document.documentElement.lang || 'en';
    history.replaceState({}, document.title, '/' + lang + '/tutorials');
  } else {
    document.location.hash = '';
  }
};

function toggleFormatFilter(e) {
  $(this).find('input[type="checkbox"]').attr('checked', false);

  var checkbox = e.target;
  checkbox.checked = true;
  var tag = checkbox.parentElement.textContent;

  // 'Case Study' -> 'casestudy'.
  var type = $.trim(tag).toLowerCase().replace(' ', '');

  if (checkbox.checked) {
    filterTag('type:' + type);
  } else {
    clearFilter();
  }
}

//$('#updates_format_filter').live('click', toggleFormatFilter);

function filterTag(opt_tag) {
  var e = window.event;

  var tag = typeof opt_tag == 'string' ? opt_tag : $(this).text();
//document.location.hash = tag;

  var samples = $('.tutorial_listing');

  if (tag) {

    var types = [];
    $('#updates_format_filter input[type="checkbox"]:checked').each(function(i, checkbox) {
      var type = checkbox.parentElement.textContent;
      // 'Case Study' -> 'casestudy'.
      types.push('type:' + $.trim(type).toLowerCase().replace(' ', ''));
    });

    samples.addClass('hidden');
    $.each(tag.split(','), function(i, eachtag) {
      if (types.length) {
        types.forEach(function(type, i) {
          samples.find('span.tag:contains("' + type + '")')
                 .closest('.tutorial_listing')
                 .find('span.tag:contains("' + eachtag + '")')
                 .closest('.tutorial_listing').removeClass('hidden');
        });
      } else {
        samples.find('span.tag:contains("' + eachtag + '")')
               .closest('.tutorial_listing').removeClass('hidden');
      }
    });
    $('#filter_tag').text(tag);
    $('#filter').parent().removeClass('hidden');
    //window.scrollTo(0, 0);
  } else {
    clearFilter();
  }
};

// Adds back button support.
window.addEventListener('hashchange', function(e) {
  filterTag(document.location.hash.substring(1));
  if (window._gaq) {
    _gaq.push(['_trackPageview', document.location.href]);
  }
}, false);