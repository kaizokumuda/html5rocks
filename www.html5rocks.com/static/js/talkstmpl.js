
//Presenter	Date	Event	Location	Slides	Slideshare	Youtube	Vimeo	Origlink	Presently	Notes

var talktmpl = '' +
'                                                      \
{{#each talksArr}}                                     \
<article>                                              \
  <h2>{{title}}</h2>                                   \
  <h4>                                                 \
      <span class=presenter>{{presenter}}</span>       \
      <span class=event>{{event}}</span>               \
      {{#if location}}                                 \
        (<span class=location>{{location}}</span>)     \
      {{/if}}                                          \
      {{#if date}}                                     \
        <span class=date>{{date}}</span>               \
      {{/if}}                                          \
  </h4>                                                \
  <div class="body">                                   \
                                                          \
    {{#if youtube}} {{video youtube}} {{/if}}             \
    {{#if vimeo}} {{video vimeo}} {{/if}}                 \
                                                          \
    {{#if slideshare}} {{slides slideshare}} {{/if}}      \
    {{#if presently}} {{slides presently}} {{/if}}        \
    {{#unless slideshare}}                                \
      {{#if slideslink}}                                  \
        <div class="slides">                              \
          <a href="{{slideslink}}" class="slides" target="_blank">                                              \
            {{#if image}} <img src="{{image}}"> {{/if}}                                                         \
            {{#unless image}} <img src="http://www.awwwards.com/awards/images/1284023910slides.jpg">{{/unless}} \
          </a>                                          \
        </div>                                          \
      {{/if}}                                           \
    {{/unless}}                                         \
                                                        \
  </div>                                                \
  {{#if notes}}                                         \
    <p class=notes>{{notes}}</p>                        \
  {{/if}}                                               \
</article>                                              \
{{/each}}                                               \
 '; 