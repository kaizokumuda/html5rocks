// Controls whether or not the site should function with ajax loads or not.
var AJAXIFY_SITE = false;

// Navigation highlighting.
$('.main nav ul li a').click(function() {
  $('.main nav .current').removeClass('current');
  if (AJAXIFY_SITE) {
    $(this).addClass('current');
  }
  setTimeout("$('.watermark').css('top', '30px')", 1000);
});

$('.subheader.features ul li a').click(function() {
  $('.main nav .current').removeClass('current');
  setTimeout("$('.watermark').css('top', '30px')", 1000);
});


// Page grid navigation.
function finishPanelLoad(pagePanel, elemstate) {
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

  if (e.keyCode === 27) { // ESC
    // Hide search and/or feature bar.
    $('#search_hide, #features_hide').click();

    // Hide +/- feature navigation.
    $('.outline_nav_toggle').removeClass('activated')
                            .find('nav.outline').fadeOut('fast');
  }
});


// TODO: go back to event delgation. Currently breaks nav.
if (AJAXIFY_SITE) {
  //$('a').live('click', function() {
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
}

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

// basic routing setup based on the global page variable
// everything happens on the `page` variable

// if it is equal to 'features-offline', then we will execute (in this order)
// route.common();
// route['features']();
// route['features-offline']();

window.route = {
  common : function() {

    // TODO(Google): record GA hit on new ajax page load.
  },

  home: function(){
    $.getScript(feed.pipeURL + '_callback=feed.home');
  },

  tutorials: function(){

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
    //var curelem = $('.page.current'),
    //    curid   = curelem[0].id;
    //$('[id=' + curid + ']').eq(1).replaceWith(curelem);

    // kick off any functions associated with the current route
    route.init(document.body.getAttribute('data-href'));
  }
};

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

// yahoo pipe returning our feed to do stuff with it.
// called from inside route[home|tutorials]()
window.feed = {
  pipeURL : 'http://pipes.yahoo.com/pipes/pipe.run?_id=\
            647030be6aceb6d005c3775a1c19401c&_render=json&',

  // homepage.

  home : function(result){
    result = feed.process(result);

    var container = document.getElementById('latest_articles_feed')
      , html = []

    if (!container) return;

    if (container.textContent == 'loading feed...') {
      container.textContent = '';
    }

    for (var i = 0, entry; entry = result.value.items[i]; ++i) {

      var classes = '<span class="classes">';
      if (entry.category && entry.category.length) {
        entry.category.forEach(function(cat) {
          classes += '<span class="class ' + cat.term + '"><span class="class_name">' + cat.term + '</span></span>';
          //TODO: use each cat.term
          //TODO: do categories correspond to classes?
          // No...
          //   categories are formats: Tutorial, Article, Case Study, Announcements, Presentation, Video
          //   classes are technologies: Offline, Storage, Connectivity, File, Access, Semantics, Audio/Video, 3D/Graphics, Presentation, Performance, Nuts & Bolts
          //   audiences/personas: General, Mobile, Gaming, Business
        });
      }
      classes += '</span>';

      html.push('<li><span class="byline"><span class="date">',
                entry.formattedDateStr, '</span> ', '<span class="author">',
                // TODO(mkwst): This shouldn't be a blank alt-attribute. It
                // should contain the author's name. That apparently isn't
                // available in the feed.
                //
                // TODO(ericbidelman): Why is this being loaded via a feed,
                // anyway? Don't we have a database?
                entry.author ?
                    '<img src="/static/images/profiles/' + entry.author +
                        '.png" alt="">' :
                    '',
                '</span></span>',
                '<span class="details"><span class="title">',
                entry.title.link(entry.link), '</span>', classes
                //,'<span data-type="', entry.type, '" class="type">', entry.type, '</span></span></li>'
                );
    }
    container.innerHTML += html.join('');

  },
  

  // normalize feed data.
  process : function(result) {
    
    if (!result.value.items) return;

    for (var i = 0, entry; entry = result.value.items[i]; ++i) {
      var date = new Date(entry.pubDate.split('T')[0].replace(/-/g, '/'));
      var formattedDateStr = date.getUTCMonth() + 1 + '/' + date.getUTCDate();

      var author = '';
      if (entry.author) {
        author = entry.author.name;
      }

      var type = '';
      if (entry.id.match('www.html5rocks.com') || entry.id.match('htmlfiverocks')) {
        type = 'tutorial';
      } else if (entry.id.match('updates.html5rocks.com')) {
        type = 'update';
      }

      entry.date = date;
      entry.formattedDateStr = formattedDateStr;
      entry.author = author;
      entry.type = type;

    }
    
    return result;

  } // eo process()
} // eo feed{}





// https://github.com/nectify/jquery-ajax-jstorage-cache
// modded by paulirish to use localStorage directly
//   and to use a 5 hour ttl on the caches.
$.ajaxPrefilter( function( options, originalOptions, jqXHR ) {
  // Cache it ?
  if( !Modernizr.localstorage || !options.localCache )
    return;

  var cacheKey;
  // If cacheKey exist we take it, or default one will be used
  if ( options.cacheKey )
    cacheKey = options.cacheKey;
  else 
     cacheKey = options.url + options.type + options.data;
  
  // isCacheValid is a function to validate cache
  if( options.isCacheValid &&  ! options.isCacheValid() ){
    localStorage.removeItem( cacheKey );
  }
  // if there's a TTL that's expired, flush this item
  var ttl = localStorage.getItem(cacheKey + 'cachettl');
  if (ttl && ttl < +new Date()){
    localStorage.removeItem( cacheKey );
    localStorage.removeItem( cacheKey  + 'cachettl');
    ttl = 'expired';
  }
  
  var value = localStorage.getItem( cacheKey );
  if( value ){
    //In the cache? So get it, apply success callback & abort the XHR request
    options.success( value );
    // Abort is broken on JQ 1.5 :(
    jqXHR.abort();
  }else{
    //If it not in the cache, we change the success callback, just put data on localstorage and after that apply the initial callback
    if( options.success ) {
      var successhandler = options.success;
      
      options.success = function( data ) {
        localStorage.setItem( cacheKey, data );
        successhandler( data );
      };
    }else{
       options.success = function( data ) {
         localStorage.setItem( cacheKey, data );
       };
    }

    // store timestamp
    if (!ttl || ttl === 'expired'){
      localStorage.setItem( cacheKey  + 'cachettl', +new Date() + 1000 * 60 * 60 * 5);
    }
    
  }
});






if (AJAXIFY_SITE) {
  window.addEventListener('popstate', state, false);
}
window.addEventListener('DOMContentLoaded', route.onload, false);
