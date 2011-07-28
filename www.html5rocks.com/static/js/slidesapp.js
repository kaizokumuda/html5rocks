

window.talks = [];
window.template = Handlebars.compile( talktmpl );



Handlebars.registerHelper('video', function(video) {
  
  var uri = parseUri(video)
    , domain = uri.host
    , id
    , html
  
  if (/youtube\.com$/.test(domain)){
    id = uri.queryKey.v;
    html = '<iframe src="http://www.youtube.com/embed/' + id + 
           '" frameborder="0" allowfullscreen></iframe> ';
    
  } else if (/vimeo\.com$/.test(domain)){
    id = uri.path.match(/\d+/)[0];
    html = '<iframe src="http://player.vimeo.com/video/' + id +
           '?title=0&amp;byline=0&amp;portrait=0&amp;color=0" frameborder="0"></iframe>';
  } else if (~video.indexOf('blip.tv')){
   
    html = '<iframe src="' + video.match(/src="(.*?)"/)[1] +
           '" frameborder="0" scrolling="no"></iframe>';
  }
  
  return new Handlebars.SafeString('<div class="video">' + html + '</div>');
});


Handlebars.registerHelper('slides', function(slides) {
  
  var uri = parseUri(slides)
    , domain = uri.host
    , id
    , html
  
  if (~slides.indexOf('docs.google.com/present')){
    id = uri.queryKey.id;
    html = '<iframe src="https://docs.google.com/present/view?id=' + id + 
           '&revision=_latest&start=0&theme=blank&cwj=true" frameborder="0"></iframe> ';
    
  } else if (/slideshare\.net$/.test(domain)){

    html = '<iframe ' +
           'src="http://icant.co.uk/slidesharehtml/embed.php?url=' + uri.source + 
           '&width=450"></iframe>';
  }
  
  return new Handlebars.SafeString('<div class="slides">' + html + '</div>');
});



Handlebars.registerHelper('presntr', function(names) {
  
  var html = '';
  
  names = names.split(/ and|&|, /)

  // need map polyfill and string.trim
  html = names.map(function(name) {

    var lookup = presenters[name.trim()];
    if (lookup) {
      return '<a href="/profiles/#!/' + lookup + '">' + name + '</a>';
    } else {
      return name;
    }

  }).join(' & ');
  
  return new Handlebars.SafeString(html);
});



// called from jsonp
function receiveSpreadsheet(data) {
  if (data.feed)
    data.feed.entry.forEach(normalizeData);
    
  render(talks.length && talks || backuptalks);

}

function normalizeData(obj, i){
    
  var talk = {};
  talk.title = obj.title.$t;
  
  // split up the weird list view. all key names start with 'omg'
  var items = obj.content.$t.split(/(^|,\s)omg/)
  // drop whitespace items
  .filter(function(item){ return !!item.replace(/,?\s+/g,''); })
  // iterate over the rest, populating our talk obj
  .forEach(function(item){
    var splitted = item.split(':');
    talk[splitted.shift()] = splitted.join(':').trim();
  });
  
  talks.push(talk);
  
}


function render(talks) {
  var html = template({ talksArr: talks })
    , output = document.querySelector('#output')
    , elems
    

  output.innerHTML = html;
  
  FLTR.setup();
  
}

window.FLTR = {
  
  input : document.querySelector('input#filter'),
  
  elems : undefined,
  entries : undefined,
  value : undefined,
  
  setup : function(){
    inputPlaceholder( FLTR.input );
    FLTR.elems = document.querySelector('#output').querySelectorAll('h2,h4,p');
    FLTR.entries = document.querySelector('#output').querySelectorAll('article');
    FLTR.input.addEventListener('keyup', FLTR.keyup, false);
    FLTR.keyup(); 
  },
  
  keyup : function(e){
    var val = FLTR.value = (e && e.target.value.toLowerCase()) || ''
      , i   = 0
    
    if (val == ''){
      FLTR.toggle(true);
      [].forEach.call( document.querySelectorAll('#output article:nth-of-type(even)'), function(elem, i){
        elem.classList.add('even')
      });
      return;
    }
    
    FLTR.toggle(false);
    
    [].forEach.call( FLTR.elems, function(elem){
      var text = elem.innerText || elem.textContent;
      if (~text.toLowerCase().indexOf(val)){
        var curNode = elem;
        while (curNode.nodeName != 'ARTICLE') curNode = curNode.parentNode;
        curNode.classList.remove('hidden');
        curNode.classList.remove('even');
        if (++i % 2) curNode.classList.add('even')
      }
    });
    
  },
  
  toggle : function(bool){
    [].forEach.call( FLTR.entries, function(elem){
      // can't do elem.classList[ bool ? 'remove' : 'add' ]('hidden') because of the polyfill
      if (bool) {
        elem.classList.remove('hidden')
      } 
      else {
        elem.classList.add('hidden')
      }
    });
  }
  
  
};


function offline(){
  receiveSpreadsheet(backuptalks);
}

window.backuptalks = [{"title":"The Latest in HTML5","presenter":"Eric Bidelman","dateexact":"7/7/2011","date":"July 2011","event":"Google Developer Relations Brown Bag","location":"Mountain View, CA","slideslink":"http://html5-demos.appspot.com/static/html5-whats-new/template/index.html"},{"title":"Building Web Apps with\nHTML5 and Chrome","presenter":"Boris Smus","dateexact":"5/15/2011","date":"May 2011","location":"Sao Paulo, Brazil","slideslink":"http://smustalks.appspot.com/brazil-11/"},{"title":"HTML5 Showcase for Web Developers: The Wow and the How","presenter":"Eric Bidelman, Arne Roomann-Kurrik","dateexact":"5/11/2011","date":"May 2011","event":"Google IO 2011","location":"San Francisco, CA","image":"http://functionscopedev.files.wordpress.com/2011/05/html5wow1.png?w=620&h=367","slideslink":"http://www.htmlfivewow.com/slide1","youtube":"http://www.youtube.com/watch?v=WlwY6_W4VG8","notes":"All code and demos are open sourced at <a href=\"http://code.google.com/p/html5wow/\">code.google.com/p/html5wow/</a>."},{"title":"HTML5 Development with the Chrome Dev Tools","presenter":"Boris Smus & Paul Irish","dateexact":"5/9/2011","date":"May 2011","event":"Google IO","location":"San Francisco","slideslink":"http://smustalks.appspot.com/devtools-lab-11/"},{"title":"MunichJS (IndexedDB & Chrome Extensions)","presenter":"Mike West","dateexact":"4/6/2011","event":"MunichJS","location":"Munich, Germany","slideslink":"http://20110406-munichjs.appspot.com/","slideshare":"http://www.slideshare.net/mikewest/munichjs-20110406"},{"title":"HTML5 & DOM & CSS3 Performance","presenter":"Paul Irish","dateexact":"4/1/2011","date":"April 2011","slideslink":"http://dl.dropbox.com/u/39519/talks/gperf/index.html","youtube":"http://www.youtube.com/watch?v=q_O9_C2ZjoA"},{"title":"State of the Browser","presenter":"Michael Mahemoff","dateexact":"3/19/2011","date":"March 2011","event":"State Of the Browser","location":"Ravensbourne, UK","slideslink":"http://prez.mahemoff.com/state-chrome/#0"},{"title":"HTML5 Storage: Application Cache","presenter":"Nikolas Coukoum","dateexact":"1/1/2011","date":"January 2011","event":"Google Tech Talk","youtube":"http://www.youtube.com/watch?v=CoUSIBep1G8","presently":"https://docs.google.com/present/view?id=ajdqczcmx5pv_147df36gf5x"},{"title":"Introduction to IndexedDB","presenter":"Mike West","dateexact":"12/13/2010","date":"December 2010","event":"Google Tech Talk","slideshare":"http://www.slideshare.net/mikewest/intro-to-indexeddb-beta","notes":"Full transcript and code examples available at <a href=\"http://mikewest.org/2010/12/intro-to-indexeddb\">mikewest.org/2010/12/intro-to-indexeddb</a>"},{"title":"HTML5 Storage","presenter":"Eric Bidelman","dateexact":"12/1/2010","date":"December 2010","event":"SenchaCon","location":"San Francisco","image":"/static/images/pres/html5storagesencha.png","slideslink":"http://html5-demos.appspot.com/static/html5storage/index.html","vimeo":"http://vimeo.com/17844271","notes":"Covers: local/sessionStorage, WebSQL, IndexedDB, app cache, File API, FileReader, BlobBuilder, FileSystem, FileWriter."},{"title":"Utilizing HTML5 in Google Chrome Extensions","presenter":"Eric Bidelman","dateexact":"12/1/2010","date":"December 2010","event":"Add-On-Con","location":"Mountain View, CA","image":"/static/images/pres/html5chromeext.png","slideslink":"http://html5-demos.appspot.com/static/addoncon2010/index.html"},{"title":"Building for a Faster Web","presenter":"Eric Bidelman","dateexact":"11/2/2010","date":"November 2010","event":"Google DevFest","location":"Buenos Aires, Argentina","slideshare":"http://www.slideshare.net/ebidel/html5-building-for-a-faster-web-5635959","youtube":"http://www.youtube.com/watch?v=PsmPF9pO56I"},{"title":"What's a web app? Building Apps for the Chrome Web Store","presenter":"Eric Bidelman","dateexact":"11/2/2010","date":"November 2010","event":"Google DevFest","location":"Buenos Aires, Argentina","slideshare":"http://www.slideshare.net/ebidel/so-whats-a-web-app-introduction-to-the-chrome-web-store","youtube":"http://www.youtube.com/watch?v=TcaWEk2O3CM"},{"title":"Web Apps and the Chrome Web Store","presenter":"Paul Kinlan","dateexact":"11/1/2010","date":"November 2010","event":"GDD","location":"Munich","image":"/static/images/pres/waandcws.png","slideslink":"http://gdd-2010.appspot.com/WebStore/index.html"},{"title":"The State of HTML5","presenter":"Paul Irish","dateexact":"10/1/2010","date":"October 2010","slideslink":"http://stateofhtml5.appspot.com/","blip":"<embed src=\"http://blip.tv/play/hq0KgoeYRwI\" type=\"application/x-shockwave-flash\" width=\"480\" height=\"300\" wmode=\"transparent\" allowscriptaccess=\"always\" allowfullscreen=\"true\" ></embed>"},{"title":"HTML5: Building the Next Generation of Web Applications","presenter":"Eric Bidelman","dateexact":"8/14/2010","date":"August 2010","event":"COSUP/GNOME.Asia","location":"Taipei, Taiwan","slideshare":"http://www.slideshare.net/ChromiumDev/html5-building-the-next-generation-of-web-applications?from=ss_embed","youtube":"http://www.youtube.com/watch?v=dVyq79wWCU4&feature=player_embedded"}];


(function(){
  var img = new Image();
  img.onerror = offline;
  img.src = 'http://html5rocks.com/static/images/identity/HTML5_Badge_64.png';
})();