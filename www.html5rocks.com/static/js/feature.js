window.caniusecallback = function(data) {

  var dom = $('.page.current .support div');

  $.each(caniuse.caniusefeatures, function(i, feature) {

    var featurestats = data.data[feature];
    var localdom = dom.clone();

    var url = 'http://caniuse.com/#search=' + feature;
    localdom.find('h4').html((featurestats.title).link(url));

    $.each(featurestats.stats, function(browser, browserobj) {

      var resulttext = '—';

      $.each(browserobj, function(version, result) {
        if (result.indexOf('y') == 0) {
          if (resulttext != '—') {
            resulttext += '+';
            return false;
          }
          resulttext = version;
        }
      });

      localdom.find('td.' + browser).text(resulttext);
    });

    localdom.find('table').css('visibility', 'visible').end()
            .insertAfter('.page.current .support h3');

    // remove placeholder table
    dom.remove();

    // Show names of browsers when hovering over the logo/version cells.
    // TODO(ericbidelman): This should be done with CSS, not JS.
    $('section.support td').hover(
      function() {
        $(this).parents('table').find('th:nth-child(' + ($(this).index() + 1) + ')').addClass('current');
      },
      function() {
        $(this).parents('table').find('th:nth-child(' + ($(this).index() + 1) + ')').removeClass('current');
      }
    );

  }); // eo feature loop
}; // eo caniusecallback()


window.loadCanIUseData = function() {
  if (caniuse.caniusefeatures[0] && caniuse.caniusefeatures[0].length) {
    $('.page.current .support').show();

    var myscript = document.createElement('script');
    myscript.src = 'http://caniuse.com/jsonp.php?callback=caniusecallback';

    var ref = document.getElementsByTagName('script')[0];
    ref.parentNode.insertBefore(myscript, ref);
  }
};

window.loadTutorials = function() {
// Request associated tutorials and populate into this page.
  var lang = document.documentElement.getAttribute('lang') || 'en';
  var div = $('<div>').load('/' + lang + '/tutorials/ #index', function() {
    var MAX_NUM_TUTS = 5;

    var ul = $('.page.current .tutorials ul');
    var matches = $([]);

    $.each(caniuse.features.split(','), function(i, eachtag) {
      var elem = div.find('.sample span.tag:contains(' + eachtag + ')')
                    .closest('.sample');
      matches = matches.add(elem);
    });

    matches.splice(MAX_NUM_TUTS);

    $(matches).find('h2 a').clone().wrap('<li>').parent().prependTo(ul);
  });
};

window.loadFeaturePanels = function() {
  if (window.caniuse) {
    loadCanIUseData();
    loadTutorials();
  }
};
