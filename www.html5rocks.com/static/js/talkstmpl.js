
//Presenter	Date	Event	Location	Slides	Slideshare	Youtube	Vimeo	Origlink	Presently	Notes

var talktmpl = '' +
'                                                      \
{{#each talksArr}}                                     \
<article data-event="{{title}}">                       \
  <h2>{{title}}</h2>                                   \
  <h4>                                                 \
      <span class=presenter>{{presntr presenter}}</span>       \
      <span class=event>{{event}}</span>               \
      {{#if location}}                                 \
        (<span class=location>{{location}}</span>)     \
      {{/if}}                                          \
      {{#if date}}                                     \
        <span class=date data-time="{{dateexact}}">{{date}}</span>               \
      {{/if}}                                          \
  </h4>                                                \
  <div class="body">                                   \
                                                          \
    {{#if youtube}} {{video youtube}} {{/if}}             \
    {{#if vimeo}} {{video vimeo}} {{/if}}                 \
    {{#if blip}} {{video blip}} {{/if}}                   \
                                                          \
    {{#if slideshare}} {{slides slideshare}} {{/if}}      \
    {{#if presently}} {{slides presently}} {{/if}}        \
    {{#unless slideshare}}                                \
      {{#if slideslink}}                                  \
        <div class="slides">                              \
          <a href="{{slideslink}}" class="slides" target="_blank" title="Click to open slides in new tab">      \
            {{#if image}} <img src="{{img image}}"> {{/if}}                                                         \
            {{#unless image}} <img src="http://www.awwwards.com/awards/images/1284023910slides.jpg">{{/unless}} \
          </a>                                          \
        </div>                                          \
      {{/if}}                                           \
    {{/unless}}                                         \
                                                        \
  </div>                                                \
  {{#if notes}}                                         \
    <p class=notes>{{{notes}}}</p>                      \
  {{/if}}                                               \
</article>                                              \
{{/each}}                                               \
 '; 
 
 
// jQuery('article.profile').each(function(){ obj[ $(this).find('h2').text().replace(/\s+/g,' ').trim() ] = this.id })

// TODO: generate this list from the db results
var presenters = {"Eric Bidelman":"ericbidelman","Geoff Blair":"geoffblair","Jeremy Chone":"jeremychone","Michael Deal":"mdeal","Ernest Delgado":"ernestd","Derek Detweiler":"derekdetweiler","Mike Dewey":"michaeldewey","Hakim El Hattab":"hakimelhattab","Adrian Gould":"adriangould","Matt Hackett":"matthackett","Ilmari Heikkinen":"ilmari","Paul Irish":"paulirish","Paul Kinlan":"paulkinlan","Jan Kleinert":"jankleinert","Seth Ladd":"sethladd","Pete LePage":"petele","Paul Lewis":"paullewis","Michael Mahemoff":"mahemoff","Adam Mark":"adammark","Luigi Montanez":"luigimontanez","Daniel X. Moore":"danielmoore","Boris Smus":"smus","David Tong":"davidtong","Malte Ubl":"malteubl"};