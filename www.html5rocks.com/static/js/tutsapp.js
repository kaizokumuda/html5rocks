window.tuts = {

  feed      : undefined,
  feeddfr   : $.Deferred(),
  authors   : undefined,
  authordfr : $.Deferred(),
  tmpl      : undefined,
  tmpldfr   : $.Deferred(),

  init : function(){

    // get update feed data
    google.load("feeds", "1");
    google.setOnLoadCallback(function(){
      var gfeed = new google.feeds.Feed("http://updates.html5rocks.com/feeds/atom.xml");
      gfeed.setNumEntries(1e3);
      gfeed.load(function(result) {
        tuts.feed = result.feed;
        tuts.feeddfr.resolve();
      });
    });

    // get author data
    $.getJSON('/api/authors', function(data){
      tuts.authors = data;
      tuts.authordfr.resolve();
    });

    // get template
    $.get('/static/js/tutorialtmpl.html', {dataType: 'plain'}, function(data){
      tuts.tmpl = Handlebars.compile( data );
      tuts.tmpldfr.resolve();
    });

    // when the three of these async events finish. kick things off.
    $.when(
        tuts.feeddfr.promise(), 
        tuts.authordfr.promise(), 
        tuts.tmpldfr.promise()      
      )
    .done(tuts.compile);

  }, // eo init() 

  compile : function(){
      
      tuts.normalize();

      var html     = tuts.tmpl({ updates: tuts.feed.entries });
      $('#index').append(html);

      tuts.resort();
      
  }, // eo compile()

  normalize : function(){
    
    tuts.feed.entries = tuts.feed.entries.map(function(entry){
      
      // author names (thx ERIC...)  :p
      if (entry.author == 'ebidelman') entry.author = 'ericbidelman';
      // okay on with the author names
      var authorentry = tuts.authors[entry.author];
      entry.fullname = authorentry.given_name + ' ' + authorentry.family_name;

      // dates
      var months = ["January", "February", "March", 
                  "April", "May", "June", "July", "August", "September", 
                  "October", "November", "December"];
      var date = entry.date  = new Date(entry.publishedDate);
      entry.formattedDateStr = months[date.getMonth()].slice(0,3) + 
                               '. ' + date.getDate() + ', ' + 
                               date.getFullYear();

                            
      // tags
      entry.categories = entry.categories.map(function(cat){
        return cat.replace(/,/g,'').trim();
      });
      entry.tags = entry.categories.join(', ');

      return entry;
    });
    
      
  }, // eo normalize()

  resort : function(){
    
    var entries = $('.tutorial_listing');
    
    // always rely on sort returning what you want
    entries = entries.each(function(i, entry){

      // make real dates
      var date = new Date(entry.getAttribute('data-pubdate'));
      $.data(entry, 'date', date);

    }).get().sort(function(a,b){

      // compare the dates
      return $.data(a,'date') > $.data(b,'date') ? -1 : 1;
    
    });

    // hello DOM
    $(entries).appendTo('#index');
    initPage();
  }
}; // eo tuts{}

tuts.init();

function clearFilter() {
  $('.tutorial_listing.hidden').removeClass('hidden');
  $('#updates_tag_filter').val('');
  $('section.filter input[type="checkbox"]').attr('checked', false);
  $('#filter').parent().addClass('hidden');
  if (!!window.history) {
    var lang = document.documentElement.lang || 'en';
    history.replaceState({}, document.title, '/' + lang + '/tutorials');
  } else {
    window.location.hash = '';
  }
};

function initializeFilters(tag_str) {
  var simple_tags = [];
  tag_str.toLowerCase().split(',').forEach(function(eachtag, i) {
      var type_and_value = eachtag.split(':');
      if (type_and_value.length == 2) {
        var value_str = ' input[value="' + type_and_value[1] + '"]';
        switch (type_and_value[0]) {
          case 'type':
            $('#updates_format_filter' + value_str).attr('checked', true);
            break;
          case 'audience':
            $('#updates_audience_filter' + value_str).attr('checked', true);
            break;
          case 'technology':
            $('#updates_technology_filter' + value_str).attr('checked', true);
            break;
          default:
            break;
        }
    } else {
      simple_tags.push(type_and_value[0]);
    }
  });
  if (simple_tags.length) {
    var updates_tag_filter_elem = $('#updates_tag_filter')[0];
    if (updates_tag_filter_elem.value) {
      updates_tag_filter_elem.value += ',';
    }
    updates_tag_filter_elem.value += simple_tags.join(',');
  }
}

// TODO: this method is being called twice for some reason. Because of onhashchange?
var times = 0;
function filterTag(opt_tag) {
  var e = window.event;

  // Don't perform another filter if we're initiated from a hashchange.
  if (e && e.type == 'hashchange') {
    return;
  }

  console.log('called: ' + ++times);

  var samples = $('.tutorial_listing');
  samples.addClass('hidden');

  if (opt_tag && typeof(opt_tag) == 'string' && opt_tag.length) {
    initializeFilters(opt_tag);
  }

  var filter_arr = [];

  // Gets all filters
  var types = [];
  $('#updates_format_filter input[type="checkbox"]:checked').each(function(i, checkbox) {
    types.push(checkbox.value);
    filter_arr.push('type:' + checkbox.value);
  });

  var audiences = [];
  $('#updates_audience_filter input[type="checkbox"]:checked').each(function(i, checkbox) {
    audiences.push(checkbox.value);
    filter_arr.push('audience:' + checkbox.value);
  });

  var technologies = [];
  $('#updates_technology_filter input[type="checkbox"]:checked').each(function(i, checkbox) {
    technologies.push(checkbox.value);
    filter_arr.push('technology:' + checkbox.value);
  });

  var tags = $('#updates_tag_filter')[0].value;
  var tag_list;
  if (tags) {
    tag_list = tags.toLowerCase().split(',');
    filter_arr.push(tags);
  } else {
    tag_list = [];
  }
  
  for (var i = 0; i < samples.length; i++) {
    var qualified = true;
    var sample = samples[i];

    if ((types.length > 0) && (types.indexOf(sample.dataset['type']) < 0)) {
      qualified = false;
    }

    if (qualified && (audiences.length > 0)) {
      var matched = false;
      for (var j = 0; j < audiences.length; j++) {
        if ($('span.tag:contains("' + audiences[j] + '")', sample).length > 0) {
          matched = true;
          break;
        }
      }
      qualified = matched;
    }

    if (qualified && (technologies.length > 0)) {
      var matched = false;
      var class_list = sample.dataset['classes'].split(',');
      for (var j = 0; j < technologies.length; j++) {
        if (class_list.indexOf(technologies[j]) >= 0) {
          matched = true;
          break;
        }
      }
      qualified = matched;
    }

    if (qualified && (tags)) {
      var matched = false;
      for (var j = 0; j < tag_list.length; j++) {
        if ((tag_list[j].length > 0) &&
            $('span.tag:contains("' + tag_list[j] + '")', sample).length > 0) {
          matched = true;
          break;
        }
      }
      qualified = matched;
    }
    
    if (qualified) {
      sample.classList.remove('hidden');
    }
  }
  
  if (filter_arr.length) {
    var filter_str = filter_arr.join(',');
    window.location.hash = filter_str;
    $('#filter_tag').text(filter_str);
    $('#filter').parent().removeClass('hidden');
  } else {
    $('#filter_tag').text('');
    $('#filter').parent().addClass('hidden');
  }
};

// Adds back button support.
window.addEventListener('hashchange', function(e) {
  if (window.location.hash) {
    filterTag(window.location.hash.substring(1));
  } else {
    clearFilter();
  }
  if (window._gaq) {
    _gaq.push(['_trackPageview', window.location.href]);
  }
}, false);

function initPage() {
  $('.tag').click(function(e){
    filterTag(this.textContent);
  });
  $('section.filter input[type="checkbox"]').click(filterTag);

  if (window.location.hash) {
    // Hide all samples as soon as DOM is loaded to prevent flicker effect.
    //var samples = $('.tutorial_listing');
    //samples.addClass('hidden');
    filterTag(window.location.hash.substring(1));
  }
}
