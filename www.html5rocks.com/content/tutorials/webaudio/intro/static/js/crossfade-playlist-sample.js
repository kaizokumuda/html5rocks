var CrossfadePlaylistSample = {
  FADE_TIME: 2 // Seconds
};

CrossfadePlaylistSample.play = function() {
  try {
    context = new webkitAudioContext();
    this.gainNode = context.createGainNode();
  }
  catch(e) {
    alert("Web Audio API is not supported in this browser");
  }

  bufferLoader = new BufferLoader(context, [
      "sounds/br-jam-loop.wav",
      "sounds/clapping-crowd.wav",
  ], finishedLoading);
  bufferLoader.load();

  var ctx = this;

  function finishedLoading(bufferList) {
    // Playback a buffer, scheduling the next buffer to play.
    playHelper(bufferList[0], bufferList[1]);
  }

  function createSource(buffer) {
    var source = context.createBufferSource();
    var gainNode = context.createGainNode();
    source.buffer = buffer;
    // Connect source to gain.
    source.connect(gainNode);
    // Connect gain to destination.
    gainNode.connect(context.destination);

    return {
      source: source,
      gainNode: gainNode
    };
  }

  function playHelper(bufferNow, bufferLater) {
    var playNow = createSource(bufferNow);
    var source = playNow.source;
    var gainNode = playNow.gainNode;
    var duration = bufferNow.duration;
    // Fade the playNow track in.
    scheduleGain(gainNode.gain, 0, 0);
    scheduleGain(gainNode.gain, ctx.FADE_TIME, 1);
    // Play the playNow track.
    source.noteOn(0);
    // At the end of the track, fade it out.
    scheduleGain(gainNode.gain, duration - ctx.FADE_TIME, 1);
    scheduleGain(gainNode.gain, duration, 0);
    // Schedule a recursive track change with the tracks swapped.
    var recurse = arguments.callee;
    setTimeout(function() {
      if (!ctx.shouldStop) {
        recurse(bufferLater, bufferNow);
      }
    }, (duration - ctx.FADE_TIME) * 1000);
  }

  function scheduleGain(gainAttr, time, value) {
    gainAttr.linearRampToValueAtTime(value, context.currentTime + time);
  }
};

CrossfadePlaylistSample.stop = function() {
  this.shouldStop = true;
};
