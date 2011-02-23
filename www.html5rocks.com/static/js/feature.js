if (caniusefeatures[0] && caniusefeatures[0].length) {
  $('.support').show();

  var myscript = document.createElement('script');
  myscript.src = 'http://caniuse.com/jsonp.php?callback=caniusecallback';

  var ref = document.getElementsByTagName('script')[0];
  ref.parentNode.insertBefore(myscript, ref);
}


window.caniusecallback = function(data) {

  var dom = $('.support').detach();

  $.each(caniusefeatures, function(i, feature) {

    var featurestats = data.data[feature];
    var localdom = dom.clone();

    localdom.find('h4').text(featurestats.title + ' browser support');

    $.each(featurestats.stats, function(browser, browserobj) {

      var resulttext = '---';

      $.each(browserobj, function(version, result) {
        if (result == 'y') {
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
            .insertAfter('div.description');

  }); // eo feature loop
}; // eo caniusecallback()


// Request associated tutorials and populate into this page.
var div = $('<div>').load('/tutorials/ #index', function() {
  var MAX_NUM_TUTS = 5;

  var ul = $('section.tutorials ul');
  var matches = $([]);

  $.each(features.split(','), function(i, eachtag) {
    var elem = div.find('.sample span.tag:contains(' + eachtag + ')')
                  .closest('.sample');
    matches = matches.add(elem);
  });

  matches = matches.splice(0, MAX_NUM_TUTS);

  $(matches).find('h2 a').clone().wrap('<li>').parent().prependTo(ul);

});

