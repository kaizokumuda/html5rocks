/*
 * JavaScript detach - v0.2 - 5/18/2011
 * https://gist.github.com/938767
 *
 * Copyright (c) 2011 "Cowboy" Ben Alman
 * Dual licensed under the MIT and GPL licenses.
 * http://benalman.com/about/license/
 */
function detach(f,e,d){var c=f.parentNode;var b=f.nextSibling;if(!c){return}c.removeChild(f);if(typeof e!="boolean"){d=e;e=false}if(d&&e){d.call(f,a)}else{if(d){d.call(f);a()}}function a(){c.insertBefore(f,b)}};



if (caniusefeatures[0] && caniusefeatures[0].length) {
  $('.support').show();

  var myscript = document.createElement('script');
  myscript.src = 'http://caniuse.com/jsonp.php?callback=caniusecallback';

  var ref = document.getElementsByTagName('script')[0];
  ref.parentNode.insertBefore(myscript, ref);
}


window.caniusecallback = function(data) {

  var dom = $('.support');

  $.each(caniusefeatures, function(i, feature) {

    var featurestats = data.data[feature];
    var localdom = dom.clone();

    var url = 'http://caniuse.com/#search=' + feature;
    localdom.find('h4').html(
        (featurestats.title + ' browser support').link(url));

    $.each(featurestats.stats, function(browser, browserobj) {

      var resulttext = '---';

      $.each(browserobj, function(version, result) {
        if (result.indexOf('y') == 0) {
          if (resulttext != '---') {
            resulttext += '+';
            return false;
          }
          resulttext = version;
        }
      });

      localdom.find('.' + browser).text(resulttext);
    });

    localdom.find('table').css('visibility', 'visible').end()
            .insertAfter('article.description');
    // remove placeholder table  
    dom.remove();

  }); // eo feature loop
}; // eo caniusecallback()


// Request associated tutorials and populate into this page.
var lang = document.documentElement.getAttribute('lang') || 'en';
var div = $('<div>').load('/' + lang + '/tutorials/ #index', function() {
  var MAX_NUM_TUTS = 5;

  var ul = $('section.tutorials ul');
  var matches = $([]);

  $.each(features.split(','), function(i, eachtag) {
    var elem = div.find('.sample span.tag:contains(' + eachtag + ')')
                  .closest('.sample');
    matches = matches.add(elem);
  });

  matches.splice(MAX_NUM_TUTS);

  $(matches).find('h2 a').clone().wrap('<li>').parent().prependTo(ul);

});

