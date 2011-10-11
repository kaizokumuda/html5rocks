var FilterSample = {
  FREQ_MUL: 7000,
  QUAL_MUL: 30,
  playing: false
};

FilterSample.play = function() {
  // Create the source.
  var source = context.createBufferSource();
  source.buffer = BUFFERS.techno;
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
  this.source = source;
  this.filter = filter;
};

FilterSample.stop = function() {
  this.source.noteOff(0);
};

FilterSample.toggle = function() {
  this.playing ? this.stop() : this.play();
  this.playing = !this.playing;
};

FilterSample.changeFrequency = function(element) {
  var sampleRate = 44100.0;  // !!@@ don't hardcode
  var nyquist = sampleRate * 0.5;
  var noctaves = Math.log(nyquist / 40.0) / Math.LN2;
  var v2 = Math.pow(2.0, noctaves * (element.value - 1.0));
  var freq = v2*nyquist;
  
  this.filter.frequency.value = freq;
};

FilterSample.changeQuality = function(element) {
  this.filter.Q.value = element.value * this.QUAL_MUL;
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
