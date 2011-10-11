var FilterSample = {};

FilterSample.play = function() {
  try {
    context = new webkitAudioContext();
  }
  catch(e) {
    alert("Web Audio API is not supported in this browser");
  }

  bufferLoader = new BufferLoader(context,
      ["sounds/techno.mp3"], finishedLoading);
  bufferLoader.load();

  var ctx = this;
  function finishedLoading(bufferList) {
    // Create the source.
    var source = context.createBufferSource();
    source.buffer = bufferList[0];
    // Create the filter.
    var filter = context.createBiquadFilter();
    filter.type = 0; // LOWPASS
    filter.frequency.value = 5000;
    // Connect source to filter, filter to destination.
    source.connect(filter);
    filter.connect(context.destination);
    // Play!
    source.noteOn(0);
    source.loop = true;
    // Save source and filterNode for later access.
    ctx.source = source;
    ctx.filter = filter;
  }
};

FilterSample.stop = function() {
  this.source.noteOff(0);
};

FilterSample.changeFrequency = function(element) {
  this.filter.frequency.value = element.value;
};

FilterSample.changeQuality = function(element) {
  this.filter.Q.value = element.value;
};

FilterSample.toggleFilter = function(element) {
  this.source.disconnect(0);
  this.filter.disconnect(0);
  // Check if we want to enable the filter.
  if (element.checked) {
    // Connect through the filter.
    this.source.connect(this.filter);
    this.filter.connect(context.destination);
  } else {
    // Otherwise, connect directly.
    this.source.connect(context.destination);
  }
};
