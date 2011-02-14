

if (caniusefeatures[0] && caniusefeatures[0].length){
   $('.support').show();
   
   var ref = document.getElementsByTagName('script')[0],
       myscript = document.createElement('script');

   myscript.src = 'http://caniuse.com/jsonp.php?callback=caniusecallback';
   ref.parentNode.insertBefore(myscript, ref);
}
   
   
window.caniusecallback = function(data){
  
 var dom = $('.support').detach();

  $.each(caniusefeatures, function(i, feature){
    
    var featurestats = data.data[feature],
        localdom     = dom.clone();

    localdom.find('h4').text(featurestats.title + ' browser support');
  
    $.each(featurestats.stats, function(browser, browserobj){
    
      var resulttext = '---';
    
      $.each(browserobj, function(version, result){
        if (result == 'y') {
          if (resulttext != '---'){
            resulttext += '+';
            return false;
          }
          resulttext = version;
        }
      });
    
      localdom.find('.' + browser).text(resulttext);
    });
  
    localdom
     .find('table').fadeIn().css('visibility','visible').end()
     .insertAfter('div.description');
  
  }); // eo feature loop
}; // eo caniusecallback()


// Request associated tutorials and populate into this page.
var div = $('<div>').load('/tutorials/ #index', function() {
  var ul = $('section.tutorials ul');
  var matches = $([]);

  $.each(features.split(','), function(i, eachtag) {
    var elem = div.find('.sample span.tag:contains(' + eachtag + ')').closest('.sample');
    matches = matches.add(elem);
  });

  $(matches)
     .find('h2 a').clone().wrap('<li>').parent().prependTo(ul);
     
});