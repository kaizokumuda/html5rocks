var CrossfadeSample = {};

CrossfadeSample.play = function() {
  try {
    context = new webkitAudioContext();
    this.gainNode = context.createGainNode();
  }
  catch(e) {
    alert("Web Audio API is not supported in this browser");
  }

  bufferLoader = new BufferLoader(context, [
      "sounds/organ-echo-chords.wav",
      "sounds/blueyellow.wav"
  ], finishedLoading);
  bufferLoader.load();

  var ctx = this;

  function finishedLoading(bufferList) {
    // Create two sources.
    ctx.ctl1 = createSource(bufferList[0]);
    ctx.ctl2 = createSource(bufferList[1]);
    // Mute the second source.
    ctx.ctl2.gainNode.gain.value = 0;
    // Start playback in a loop
    ctx.ctl1.source.noteOn(0);
    ctx.ctl2.source.noteOn(0);
    // Set the initial crossfade to be just source 1.
    ctx.crossfade(0);
  }

  function createSource(buffer) {
    var source = context.createBufferSource();
    var gainNode = context.createGainNode();
    source.buffer = buffer;
    // Turn on looping
    source.loop = true;
    // Connect source to gain.
    source.connect(gainNode);
    // Connect gain to destination.
    gainNode.connect(context.destination);

    return {
      source: source,
      gainNode: gainNode
    };
  }
};

CrossfadeSample.stop = function() {
  this.ctl1.source.noteOff(0);
  this.ctl2.source.noteOff(0);
};

// Fades between 0 (all source 1) and 1 (all source 2)
CrossfadeSample.crossfade = function(element) {
  var x = parseInt(element.value) / parseInt(element.max);
  // Use an equal-power crossfading curve:
  var gain1 = 0.5 * (1.0 + Math.cos(x * Math.PI));
  var gain2 = 0.5 * (1.0 + Math.cos((1.0 - x) * Math.PI));
  this.ctl1.gainNode.gain.value = gain1;
  this.ctl2.gainNode.gain.value = gain2;
};
