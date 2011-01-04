// todo

// fluid height work
// js cleanup
// review words.
// carousel shit.


/*
 1. opens in TOC view.  - toc class
    transitions immediately fire to spin out the thumbnails
 2. on selection they collapse into controlbar - tos class is removed. show class is added.
    transition position into stacked in bar
 3. on last box's transitionEnd hit, position scheme is changed to relative to the box and they float
    a. need a fallback for no transitionEnd event support.
    b. need a fallback for no transition support
*/


window.UI = {
    
  /* each box: 160 x 166, padded size: 190 x 190 */
  gridInitX : 30, 
  gridInitY : 25,
  boxWidth  : 190,
  boxHeight : 190,
  
  lastDemo : undefined, // keeping track of last demo opened
  boxes    : undefined,
  
  onReady : function(){
      UI.boxes = $('div.box');
  },
  
  onLoad : function(){
      UI.writeBoxStyles();

      if (location.hash.length > 2) { return; }

      setTimeout(function () {
        $(document.body).addClass('go');
      }, 500);
  } // eo UI.onLoad
  
  
};


// css transition handling
UI.trans = {
    
    // transition queue
    fnQueue : [
      function () {
        $('#body').addClass('show')
      }, function () {
        $('#body').addClass('open');
        $(UI.lastDemo).click()
      }
    ], // eo UI.trans.fnQueue[]
    
    onEnd : function f(e) {

      if ($('body').hasClass('toc') || $('#body').hasClass('open')) {
        return;
      }

      f.boxes = f.boxes || UI.boxes.length;
      // use the in progress one or make a shallow copy
      f.fns = (f.fns && f.fns.length) ? f.fns : $.extend([], UI.trans.fnQueue);

      f.boxes--;

      // allow for forced progression (!csstransitions)
      if (f.boxes === 0 || e === true) {
        f.boxes = UI.boxes.length;
        var fn = f.fns.shift();
        fn && setTimeout(fn, 400);
      }
    } // eo UI.trans.onEnd()
};



// tooltip 
UI.tip = {
  over: function (e) {
    
    // hover over the invisible tooltip?
    var srcElement = (e && e.srcElement && $(e.srcElement)) || [];
    if (srcElement.length && srcElement.closest('.tooltip').length && srcElement.closest('.tooltip').is(':visible')){
      return;
    }
    
    var h3 = $('<h3>').text($(UI.lastDemo).find('a:first span').text());
    var info = $(UI.lastDemo).find('p,ul').clone();
    var support = $(UI.lastDemo).data('support');
    var suphtml = $('<div class="support">').addClass( ('' + !!support) ).text(
        'Your browser ' + (support ? ' appears to ' : ' may not fully ') + ' support these features.'
      );
      

    $('.tooltip').find('h3,p,ul,.support').remove().end()
     .append(h3).append(info).append(suphtml)
     .appendTo("#info").addClass('popped');
   },
   out: function (e) {
     $('.tooltip').removeClass('popped');
   }
};




UI.flexHeight = {
    
    initialOffset : undefined,
    firstRun: false,
    
    tops : {
      '#stage iframe': 'height',
      '#container': 'height',
      '.controlbar': 'top',
      'footer': 'top'
    },
    
    setShowcaseSize : function() {
      if (!UI.flexHeight.firstRun) {
        UI.flexHeight.storeInitialTops(UI.flexHeight.tops);
        UI.flexHeight.firstRun = true;
      }

      var offset = UI.flexHeight.getOffset();

      $.each(UI.flexHeight.tops, function (sel, prop) {
        var elem = $(sel);
        var value = $.data(elem[0], 'initial');
        //log(elem[0],prop,   value, offset)
        elem.css(prop, parseFloat(value) + offset + 'px')
      });

    },
    
    storeInitialTops : function (tops) {
      $.each(tops, function (sel, prop) {
        var elem = $(sel); //log( elem.css(prop))
        var value = elem.css(prop);
        value = (value === 'auto' || !value) ? 491 : value; // fix for controlbar position
        $.data(elem[0], 'initial', value);
      });

      var footer = $('footer');
      UI.flexHeight.initialOffset = footer.offset().top + footer.height();
    },
    
    getOffset : function () {
      // magic number 33 is a good looking amount of padding before bottom of window
      var offset = $(window).height() - 33 - UI.flexHeight.initialOffset;
      // allow between 0 and 160 px of offset
      return Math.min(160, Math.max(0, offset));
    }
    
    
};






UI.tocToDemos = function (e) {

  UI.lastDemo = this;

  $(document.body).removeClass('go toc');
  
  // if we dont have transitionEnd events..
  if (!Modernizr.csstransitions){
    UI.trans.onEnd(true);
    UI.trans.onEnd(true);
  }
};


UI.hashChange = function(e, firstTime) {
  
  var text = location.hash.replace(/^#/,'');
  
  // An empty hash means he user went back to the start.
  if (text === ''){
    $('body')[0].className = 'go toc';
       $.publish('return-to-grid');
  } else {
    firstTime && UI.tocToDemos();
    $('#body').addClass('show open');
    $('div.box')
      .find('a:contains(' + text + ')')
      .trigger('click', [true]);
  }
  
};

UI.scrollDemoContainer = function(){
    
    var boxes = $('div.box');
    var trigger = $(this);
    
    $('.controlbar').animate({'scrollTop': '+=' + UI.boxHeight }, function(){
        // if we've scrolled up all the boxes so no more are invisble,
        // kill the scroll trigger
        if (boxes.last().offset().top - $('#container').height() + UI.boxHeight <= 0){
            trigger.hide();
        }
    });
    

    return false;
};


UI.writeBoxStyles = function(){

    // just making a style rule.
    var rules = $('div.box').map(function(i, elem){

        return '' + 
        '.go div.box:nth-child(' + (i+1) + ') { ' + 
            'left : ' + ((i % 3) * UI.boxWidth + UI.gridInitX) + 'px;' +
            'top  : ' + ((~~(i/3)) * UI.boxHeight + UI.gridInitY) + 'px;' +
        '}';

    }).get().join('');
    
    $('<style>').text(rules).appendTo('head');
};


UI.returnToGrid = function (e) {
  $('#stage iframe').hide().attr('src', 'about:blank');
  $(document.body).addClass('go toc');
  $('#body').removeClass('show open');
};


// load iframe and all that jazz
UI.demoChosen = function(e, forced) {

  UI.tip.out();
  
  UI.lastDemo = this;
   
  $(this).addClass('selected').siblings().removeClass('selected');
  var link = $(this).find('a:first');
  var iframe = $('<iframe>').attr('src', link.attr('href'));
  iframe.insertAfter('#stage iframe').show().prev().remove();
  
  
  // set the hash to be the chosen demo
  var hashtext = $(UI.lastDemo).find('a').text().split(/\s+/).slice(-1);
  location.hash = hashtext;
  
  
  // tell google analytics
  window._gaq && _gaq.push(['_trackPageview', link.attr('href')]);
  
  
  // don't show the tooltip twice
  if (Modernizr.sessionstorage){
    var key = link.text().replace(/\s+/g,'').toLowerCase();
    if (sessionStorage[key]) return;
    sessionStorage[key] = true;
  }
  
  
  UI.tip.over();
  
  clearTimeout(UI.demoChosen.t); // clear any stale timeouts
  UI.demoChosen.t = setTimeout(UI.tip.out,10*1000);
  

};






$('.show.open div.box').live('click', UI.demoChosen);
$.subscribe('return-to-grid',UI.returnToGrid);
$(document).bind('webkitTransitionEnd transitionend oTransitionEnd', UI.trans.onEnd);
$(document).ready(UI.onReady);
$(window).load(UI.onLoad);



// when we click from TOC view, kick off the transition to showcase view
$('#boxes')
  .delegate('.toc .box', 'click', UI.tocToDemos)
  .delegate('.box a', 'click', function(e) {
    e.preventDefault();
  });



$('#view_source').click(function () {
  window.open('view-source:' + $('iframe')[0].contentDocument.location.href);
});


$('#download').click(function () {
  var path = $('iframe')[0].contentDocument.location.href.split('/');
  window.open( path.slice(0,-1).join('/') + '/' + path.slice(-2,-1)[0] + '.zip' );
});


$([document,window]).bind('ready resize', UI.flexHeight.setShowcaseSize);
$('a#boxtrigger').click(UI.scrollDemoContainer);

$(window).bind('hashchange', UI.hashChange);


$("#info").hoverIntent({
  over: UI.tip.over,
  out: UI.tip.out,
  timeout: 500
});



$(window).trigger('hashchange', [true]);
