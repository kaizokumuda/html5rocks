

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
  
  data.feed.entry.forEach(normalizeData);
  render(talks);

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
