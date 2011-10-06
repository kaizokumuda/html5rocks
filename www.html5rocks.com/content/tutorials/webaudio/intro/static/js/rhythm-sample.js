var RhythmSample = {
};

RhythmSample.play = function() {
  try {
    context = new webkitAudioContext();
  }
  catch(e) {
    alert("Web Audio API is not supported in this browser");
  }

  bufferLoader = new BufferLoader(context,
      ['sounds/kick.wav', 'sounds/snare.wav', 'sounds/hihat.wav'],
      startPlayingRhythm);
  bufferLoader.load();

  var ctx = this;

  function playSound(buffer, time) {
    var source = context.createBufferSource();
    source.buffer = buffer;
    source.connect(context.destination);
    source.noteOn(time);
  }

  // Plays a simple 4/4 rhythm
  function startPlayingRhythm(bufferList) {
    var kick = bufferList[0];
    var snare = bufferList[1];
    var hihat = bufferList[2];

    // We'll start playing the rhythm 100 milliseconds from "now"
    var startTime = context.currentTime + 0.100;
    var tempo = 80; // BPM (beats per minute)
    var eighthNoteTime = (60 / tempo) / 2;

    // Play 2 bars of the following:
    for (var bar = 0; bar < 2; bar++) {
      time = startTime + bar * 8 * eighthNoteTime;
      // Play the bass (kick) drum on beats 1, 5
      playSound(kick, time);
      playSound(kick, time + 4*eighthNoteTime);

      // Play the snare drum on beats 3, 7
      playSound(snare, time + 2*eighthNoteTime);
      playSound(snare, time + 6*eighthNoteTime);

      // Play the hi-hat every eighthh note.
      for (var i = 0; i < 8; ++i) {
        playSound(hihat, time + i*eighthNoteTime);
      }
    }
  }
};
