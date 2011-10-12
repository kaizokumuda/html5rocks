var VolumeSample = {
};

// Gain node needs to be mutated by volume control.
VolumeSample.gainNode = null;

VolumeSample.play = function() {
  this.gainNode = context.createGainNode();
  var source = context.createBufferSource();
  source.buffer = BUFFERS.techno;

  // Connect source to a gain node
  source.connect(this.gainNode);
  // Connect gain node to destination
  this.gainNode.connect(context.destination);
  // Start playback in a loop
  source.loop = true;
  source.noteOn(0);
  this.source = source;
};

VolumeSample.changeVolume = function(element) {
  var volume = element.value;
  var percent = parseInt(element.value) / parseInt(element.max);
  // Volume is not linear, but exponential. Adjust the control.
  this.gainNode.gain.value = percent * percent;
};

VolumeSample.stop = function() {
  this.source.noteOff(0);
};

VolumeSample.toggle = function() {
  this.playing ? this.stop() : this.play();
  this.playing = !this.playing;
};
