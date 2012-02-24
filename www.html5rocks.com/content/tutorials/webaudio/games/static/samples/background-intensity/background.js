function BackgroundIntensity(buttonElement, rangeElement, context) {
  var ctx = this;

  buttonElement.addEventListener('click', function() {
    ctx.playPause.call(ctx);
  });

  rangeElement.addEventListener('change', function(e) {
    var value = parseInt(e.target.value);
    var max = parseInt(e.target.max);
    ctx.setIntensity(value / max);
  });

  var sources = ['sounds/1-atmos.mp3', 'sounds/2-swell.mp3',
    'sounds/3-pierce.mp3', 'sounds/4-boss.mp3'];

  // Load all sources.
  var ctx = this;
  loader = new BufferLoader(context, sources, onLoaded);
  loader.load();

  function onLoaded(buffers) {
    // Store the buffers.
    ctx.buffers = buffers;
  }

  this.sources = new Array(sources.length);
  this.gains = new Array(sources.length);
}

BackgroundIntensity.prototype.playPause = function() {
  if (this.playing) {
    // Stop all sources.
    for (var i = 0, length = this.sources.length; i < length; i++) {
      var src = this.sources[i];
      src.noteOff(0);
    }
  } else {
    var targetStart = context.currentTime + 0.1;
    // Start all sources simultaneously.
    for (var i = 0, length = this.buffers.length; i < length; i++) {
      this.playSound(i, targetStart);
    }
    this.setIntensity(0);
  }
  this.playing = !this.playing;
}

BackgroundIntensity.prototype.setIntensity = function(value) {
  // Set the gain values appropriately.
  for (var i = 0, length = this.gains.length; i < length; i++) {
    var x = i / (length - 1);
    var y = computeGaussian(x, value, 0.01);
    // Max gain is 1.
    this.gains[i].gain.value = Math.min(1, y);
  }
}

BackgroundIntensity.prototype.playSound = function(index, targetTime) {
  var buffer = this.buffers[index];
  var source = context.createBufferSource();
  source.buffer = buffer;
  source.loop = true;
  var gainNode = context.createGainNode();
  // Make a gain node.
  source.connect(gainNode);
  gainNode.connect(context.destination);
  // Save the source and gain node.
  this.sources[index] = source;
  this.gains[index] = gainNode;
  source.noteOn(targetTime);
}


var context;
window.addEventListener('load', init, false);
function init() {
  try {
    context = new webkitAudioContext();
  }
  catch(e) {
    alert('Web Audio API is not supported in this browser');
  }
  sample = new BackgroundIntensity(document.querySelector('button'),
                                   document.querySelector('input'),
                                   context);
}

function computeGaussian(x, mu, sd2) {
  return Math.exp(- (x - mu)*(x - mu)/(2 * sd2)) /
    Math.sqrt(2 * Math.PI * sd2);
}
