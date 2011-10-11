var VolumeSample = {
};

// Gain node needs to be mutated by volume control.
VolumeSample.gainNode = null;

VolumeSample.loadAndPlay = function() {
  try {
    context = new webkitAudioContext();
    this.gainNode = context.createGainNode();
  }
  catch(e) {
    alert("Web Audio API is not supported in this browser");
  }

  bufferLoader = new BufferLoader(context,
      ["sounds/techno.mp3"], finishedLoading);
  bufferLoader.load();

  var ctx = this;

  function finishedLoading(bufferList) {
    var source = context.createBufferSource();
    source.buffer = bufferList[0];

    // Connect source to a gain node
    source.connect(ctx.gainNode);
    // Connect gain node to destination
    ctx.gainNode.connect(context.destination);
    // Start playback in a loop
    source.loop = true;
    source.noteOn(0);
    ctx.source = source;
  }
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
