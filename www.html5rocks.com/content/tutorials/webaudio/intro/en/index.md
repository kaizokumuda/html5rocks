Before the HTML5 `<audio>` element, flash or a plugin was required to
break the silence of the web. However, the audio tag has significant
limitations for implementing sophisticated games and interactive
applications. The goal of the Web Audio API is to include capabilities
found in modern game audio engines as well as some of the mixing,
processing, and filtering tasks that are found in modern desktop audio
production applications.

The Web Audio API is a high-level JavaScript API for processing and
synthesizing audio in web applications. As of version 14, Google Chrome
ships with an implementation of the Web Audio API. What follows is a
gentle introduction to using this powerful API.

<h2 id="toc-context">The audio context</h2>

An [AudioContext][] is used for managing and playing all sounds. In most cases a
single AudioContext is created per page.

To produce a sound using the Web Audio API, you create one or more sound
sources and connect them to the sound destination provided by the AudioContext.
This connection doesn't need to be direct, and can instead go through
any number of chained [AudioNodes][]. This [routing][] is described in
greater detail at the Web Audio [specification][spec].

The following snippet creates an AudioContext:

    window.onload = init;
    var context;
    function init() {
      context = new webkitAudioContext();
    }

Note: for the WebKit implementation, the "webkit" prefix is used when creating
the AudioContext.

Many of the interesting Web Audio API functionality such as creating
AudioNodes and decoding audio file data are methods of the AudioContext.

[AudioContext]: https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/specification.html#AudioContext-section
[AudioNodes]: https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/specification.html#AudioNode-section
[routing]: https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/specification.html#ModularRouting-section
[spec]: https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/specification.html

<h2 id="toc-load">Loading sounds</h2>

The Web Audio API uses an AudioBuffer for short to medium length sounds
(smus: what about long sounds?). The basic approach is to use
XMLHttpRequest for fetching sound files.

The API supports loading audio file data in multiple formats, such as WAV, MP3,
AAC, or OGG. Please note that browser support for the different formats varies.
The following shippet demonstrates loading a sound sample:

    var dogBarkingBuffer = 0;
    var context = new webkitAudioContext();

    function loadDogSound(url) {
      var request = new XMLHttpRequest();
      request.open("GET", url, true);
      request.responseType = "arraybuffer";

      request.onload = function() {
        // Decode asynchronously
        context.decodeAudioData(
            request.response,
            function(buffer) {
            dogBarkingBuffer = buffer;
          }
        );
      }

      request.send();
    }

The audio file data is binary (not text) so we set the `responseType` of the
request to `"arraybuffer"`.

Once the (undecoded) audio file data has been received, it can be kept around
for later decoding, or more normally, it can be decoded right away using the
AudioContext `decodeAudioData()` method. This method takes the `ArrayBuffer` of
audio file data stored in `request.response` and decodes it asynchronously (not
blocking the main JavaScript execution).

When `decodeAudioData()` is finished it calls a callback function which
provides the decoded PCM audio data as an `AudioBuffer`.


<h2 id="toc-play">Playing sounds</h2>

![simple-graph][]

Once one or more AudioBuffers are loaded then we're ready to play sounds. Let's
assume we've just loaded an AudioBuffer with the sound of a dog barking and
that the loading has finished.

Then we can play this dogBarkingBuffer with a the following code.

    var context = new webkitAudioContext();

    function playSound() {
      var source = context.createBufferSource();  // creates a sound source
      source.buffer = dogBarkingBuffer;           // tell the source which sound to play
      source.connect(context.destination);        // connect the source to the context's destination (the speakers)
      source.noteOn(0);                           // play the source now
    }

This playSound() function could be called every time somebody presses a key or
clicks something with the mouse.

Note that the `noteOn(time)` function makes it easy to schedule precise sound
playback for games and other time-critical applications.

[simple-graph]: https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/modular-routing1.png

<h2 id="toc-abstract">Abstracting the Web Audio API</h2>

Of course, it would be better to create a more general loading system which
isn't hard-coded to loading this specific sound. There are many approaches for
dealing with the many short to medium length sounds that an audio application
or game would use - here's one way using a [BufferLoader class][BufferLoader].

Here's how the BufferLoader class can be used. In this simple example, two
AudioBuffers are created and when they are finished loading, they are played
back at the same time.

    window.onload = init;
    var context;
    var bufferLoader;

    function init() {
      context = new webkitAudioContext();

      bufferLoader = new BufferLoader(
        context,
        [
          "../sounds/hyper-reality/br-jam-loop.wav",
          "../sounds/hyper-reality/laughter.wav",
        ],
        finishedLoading
        );

      bufferLoader.load();
    }

    function finishedLoading(bufferList) {
      // Create two sources and play them both together.
      var source1 = context.createBufferSource();
      var source2 = context.createBufferSource();
      source1.buffer = bufferList[0];
      source2.buffer = bufferList[1];

      source1.connect(context.destination);
      source2.connect(context.destination);
      source1.noteOn(0);
      source2.noteOn(0);
    }

[BufferLoader]: js/buffer-loader.js

<h2 id="toc-abstract">Dealing with time: playing sounds with rhythm</h2>

The Web Audio API lets developers precisely schedule playback. To
demonstrate this, let's setup a simple rhythm track. Probably the
most widely known drumkit pattern is the following:

![drumkit][]

in which a hihat is played every eight note, and kick and snare are
played alternating every quarter, in 4/4 time.

Supposing we have loaded the `kick`, `snare` and `hihat` buffers, the
code to do this is simple:

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

Here, we make only two repeats instead of the unlimited loop we see in
the sheet music. The function `playSound` is is a method that plays a
buffer at a specified time, as follows:

    function playSound(buffer, time) {
      var source = context.createBufferSource();
      source.buffer = buffer;
      source.connect(context.destination);
      source.noteOn(time);
    }

[drumkit]: diagrams/drum.png

<input type="button" onclick="RhythmSample.play();" value="Play"/>

<h2 id="toc-volume">Changing the volume of a sound</h2>

One of the most basic operations you might want to do to a sound is
change its volume. Using the Web Audio API, we can route our source to
its destination through an [AudioGainNode][] in order to manipulate the
volume:

![gain-graph][]

This connection setup can be achieved as follows:

    // Create a gain node.
    var gainNode = context.createGainNode();
    // Connect the source to the gain node.
    source.connect(gainNode);
    // Connect the gain node to the destination.
    gainNode.connect(context.destination);

After the graph has been set up, you can programmatically change the
volume by manipulating the `gainNode.gain.value` as follows:

    // Reduce the volume.
    gainNode.gain.value = 0.5;

The following is a demo of a volume control implemented with an `<input
type="range">` element:

<input type="button" onclick="VolumeSample.loadAndPlay();" value="Play"/>
<input type="button" onclick="VolumeSample.stop();" value="Stop"/>
Volume: <input type="range" min="0" max="100" value="100" onchange="VolumeSample.changeVolume(this);" />

<h2 id="toc-xfade">Cross-fading between two sounds</h2>

Now, suppose we have a slightly more complex scenario, where we're
playing multiple sounds, but want to cross fade between them. This is a
common case in a DJ-like application, where we have two turntables and
want to be able to pan from one sound source to another.

This can be done with the following audio graph:

![crossfade-graph][]

To set this up, we simply create two [AudioGainNode][]s, and connect
each source through the nodes, using something like this function:

    function createSource(buffer) {
      var source = context.createBufferSource();
      // Create a gain node.
      var gainNode = context.createGainNode();
      source.buffer = buffer;
      // Turn on looping.
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

<h3 id="toc-xfade-ep">Equal power crossfading</h3>

Note that a naive linear crossfade approach will exhibit a volume dip as
you pan between the samples.

![linear-crossfade-graph][]

To address this issue, we use an equal power curve, in which the
corresponding gain curves are non-linear, and intersect at a higher
amplitude. This minimizes volume dips between audio regions, resulting
in a more even crossfade between regions that may be slightly different
in level.

![equalpower-crossfade-graph][]

The following demo uses an `<input type="range">` control to crossfade
between the two sound sources:

<input type="button" onclick="CrossfadeSample.play();" value="Play"/>
<input type="button" onclick="CrossfadeSample.stop();" value="Stop"/>
Drums <input type="range" min="0" max="100" value="100" onchange="CrossfadeSample.crossfade(this);" /> Organ

<h3 id="toc-xfade-play">Playlist crossfading</h3>

Another common crossfader application is for a music player application.
When a song changes, we want to fade the current track out, and fade the
new one in, to avoid a jarring transition. To do this, we need to
schedule a crossfade into the future. While we could use `setTimeout` to
do this scheduling, this is [quite inaccurate][jstimer]. With the Web
Audio API, we can use the [AudioParam][] interface to schedule future
values for parameters such as the gain value of an AudioGainNode.

Thus, given a playlist, we can transition between tracks by scheduling a
gain decrease on the currently playing track, and a gain increase on the
next one, both slightly before the current track finishes playing:

    function playHelper(bufferNow, bufferLater) {
      // Get the track length.
      var playNow = createSource(bufferNow);
      var source = playNow.source;
      var gainNode = playNow.gainNode;
      var duration = bufferNow.duration;
      // Start playback.
      source.noteOn(0);
      // Schedule a fade-in.
      scheduleGain(gainNode.gain, 0, 0);
      scheduleGain(gainNode.gain, ctx.FADE_TIME, 1);
      // At the end of the track, fade it out.
      scheduleGain(gainNode.gain, duration - ctx.FADE_TIME, 1);
      scheduleGain(gainNode.gain, duration, 0);
      // Schedule a recursive track change with the tracks swapped.
      var recurse = arguments.callee;
      setTimeout(function() {
        recurse(bufferLater, bufferNow);
      }, (duration - ctx.FADE_TIME) * 1000);
    }

The Web Audio API provides a convenient set of RampToValue methods to
gradually change the value of a parameter:

    function scheduleGain(gainAttr, time, value) {
      gainAttr.linearRampToValueAtTime(value, context.currentTime + time);
    }

While the transition timing function can be picked from built-in linear
(as above) and exponential ones (see `exponentialRampToValueAtTime`),
you can also specify your own value curve via an array of values using
the `setValueCurveAtTime` function.

The following demo shows an playlist-like auto-crossfade between two
tracks using the above approach:

<input type="button" onclick="CrossfadePlaylistSample.play();" value="Play"/>
<input type="button" onclick="CrossfadePlaylistSample.stop();" value="Stop"/>

[jstimer]: http://stackoverflow.com/questions/2779154/understanding-javascript-timer-thread-issues
[AudioParam]: https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/specification.html#AudioParam-section
[AudioGainNode]: https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/specification.html#AudioGainNode-section
[crossfade-graph]: diagrams/crossfade.png
[gain-graph]: diagrams/gain.png
[linear-crossfade-graph]: diagrams/linear-fade.png
[equalpower-crossfade-graph]: diagrams/equal-fade.png

<h2 id="toc-filter">Applying a simple filter effect to a sound</h2>

![filter-graph][]

The Web Audio API lets you pipe sound from one audio node into another,
creating a potentially complex chain of processors to add complex
effects to your soundforms.

One way to do this is to place [BiquadFilterNode][]s between your sound
source and destination. This type of audio node can do a variety of
low-order filters which can be used to build graphic equalizers and even
more complex effects, mostly to do with selecting which parts of the
frequency spectrum of a sound to emphasize and which to subdue.

Supported types of filters include:

* Low pass filter
* High pass filter
* Band pass filter
* Low shelf filter
* High shelf filter
* Peaking filter
* Notch filter
* All pass filter

And all of the filters include parameters to specify some amount of
gain, the frequency at which to apply the filter, and a quality factor.
The low-pass filter keeps the lower frequency range, but discards high
frequencies. The breakoff point is determined by the frequency value,
and the Q factor is unitless, and determines the shape of the graph, and
the gain value determines the overall gain that the filter affects on
the input sound.

The frequency response graph for this low-pass filter looks roughly like
the following:

![lowpass][]

You can see the peaking occurs at the specified frequency, and the
quality affects how quickly the volume decays.

Let's setup a simple low-pass filter to extract only the bases from a
sound sample:

    // Create the audio graph.
    source.connect(filter);
    filter.connect(context.destination);
    // Specify parameters for the low-pass filter.
    filter.type = 0; // Low-pass filter. See BiquadFilterNode docs
    filter.frequency.value = 440; // Set cutoff to 440 HZ
    // Playback the sound.
    source.noteOn(0);

The following demo uses a similar technique and lets you enable and
disable a lowpass filter via a checkbox, as well as tweak the frequency
and quality values with the slider:

<input type="button" onclick="FilterSample.play();" value="Play"/>
<input type="button" onclick="FilterSample.stop();" value="Stop"/>
Filter on: <input type="checkbox" checked="false"
    onchange="FilterSample.toggleFilter(this);"/>
Frequency: <input type="range" min="0" max="5000" value="5000" onchange="FilterSample.changeFrequency(this);" />
Quality: <input type="range" min="0" max="30" step="1" value="0" onchange="FilterSample.changeQuality(this);" />

Note that the sample code lets you connect and disconnect the filter,
dynamically changing the AudioContext graph. We can disconnect
AudioNodes from the graph by calling `node.disconnect(outputNumber)`.
For example, to re-route the graph from going through a filter, to a
direct connection, we can do the following:

    // Disconnect the source and filter.
    this.source.disconnect(0);
    this.filter.disconnect(0);
    // Connect the source directly.
    this.source.connect(context.destination);

[lowpass]: http://www.beis.de/Elektronik/AudioMeasure/Images/FRLowPass.GIF
[BiquadFilterNode]: https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/specification.html#BiquadFilterNode-section
[filter-graph]: diagrams/filter.png

<h2 id="toc-further">Further listening</h2>

Although the Web Audio API has just been release, many talented
engineers have been doing [great work][samples]. Have a listen :)

[samples]: http://chromium.googlecode.com/svn/trunk/samples/audio/samples.html
