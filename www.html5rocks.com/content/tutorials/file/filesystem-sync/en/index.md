<h2 id="toc-prereqs">Prerequisites</h2>

The HTML5 [FileSystem API][fs-spec] and [Web Workers][workers-spec] are massively
powerful in their own regard. Workers bring true asynchronous 'multi-threading'
to JavaScript and the FileSystem API finally brings hierarchical storage and
file I/O to web applications. However, when used in together, these APIs can be
used to build some truly interesting apps. 

<h3 id="toc-getting-started">Getting started</h3>

This tutorial provides a guide and code examples for leveraging the HTML5
FileSystem inside of a Web Worker. However, it assumes a working knowledge of
both APIs. If you're interested in learning more about these APIs, I've written
two great tutorials that discuss the basics:
[Exploring the FileSystem APIs](/tutorials/file/filesystem/) and
[Basics of Web Workers](/tutorials/workers/basics/).

<h2 id="toc-intro">Introduction</h2>

Asynchronous JS APIs can be tough to use. They're often large, complex, and offer
plenty of opportunities for things to go wrong. The last thing you want when
building a new app is attempting to use and debug an async API (FileSystem)
in an already asynchronous world (Workers)! The good news is that the
[FileSystem API][fs-spec] API defines a synchronous version for exclusive use in
Web Workers.

For the most part, the synchronous API is exactly the same as its asynchronous cousin.
The methods, properties, features, and functionality will be familiar. The major deviations are:

* The synchronous API can only be used within a Web Worker context, whereas the
asynchronous API can be used in and out of a worker.
* Callbacks are out. API methods now return values.
* The global methods on the window object (`requestFileSystem()` and
`resolveLocalFileSystemURL()`) become `requestFileSystemSync()` and
`resolveLocalFileSystemSyncURL()`. *Note:* These methods are members of the
worker's global scope, not the <code>window</code> object.

Apart from these exceptions, the APIs are the same. We're good to go!

<h2 id="toc-requesting">Requesting a filesystem</h2>

A web application obtains access to the synchronous filesystem by requesting a
`LocalFileSystemSync` object from within a web worker. The `requestFileSystemSync()`
is exposed to the worker's global scope:

    var fs = requestFileSystemSync(TEMPORARY, 1024*1024 /*1MB*/);

Notice the new return value now that we're using the sync API and absence of success
and error callbacks.

As with the normal FileSystem API, methods are prefixed:

    self.requestFileSystemSync = self.webkitRequestFileSystemSync ||
                                 self.requestFileSystemSync;


<h3 id="toc-quota">Dealing with quota</h3>

Currently, it's not possible to [request `PERSISTENT` quota](/tutorials/file/filesystem/#toc-requesting-quota) in a Worker context. I recommend taking care of quota issues outside of workers.
The process could look like something this:

1.  worker.js: wrap any FileSystem API code in a `try/catch` so any
`QUOTA_EXCEED_ERR` errors will be caught.
2. worker.js: If you catch a `QUOTA_EXCEED_ERR`, send a `postMessage('get me more quota')` back to the main app.
3. main app: go through the `window.webkitStorageInfo.requestQuota()` dance when #2 is received.
4. main app: after the user grants more quota, send `postMessage('resume writes')` back
to the worker to inform it of additional storage space.

That's a fairly involved workaround, but should work. See [requesting quota](/tutorials/file/filesystem/#toc-requesting-quota) for more information on using `PERSISTENT` storage with the FileSystem API.

<h2 id="toc-files-dirs">Working with files and directories</h2>

The synchronous version of `getFile()` and `getDirectory()` return a `FileEntrySync`
and `DirectoryEntrySync`, respectively.

For example, the following code creates an empty file called "log.txt" in the
root directory.

    var fileEntry = fs.root.getFile('log.txt', {create: true});

The following creates a new directory in the root folder.

    var dirEntry = fs.root.getDirectory('mydir', {create: true});


<h2 id="toc-errors">Handling errors</h2>

If you've never had to debug Web Worker code, I envy you! It can be a real pain
to figure out what is going wrong.

The lack of error callbacks in the synchronous world makes dealing with problems
trickier than they should be. If we add the general complexity debugging in a worker,
you'll frustrated in no time. One thing that can make life easier is to wrap all
of your relevant worker code in a try/catch. Then, if any errors occur, forward
the error to the main app using `postMessage()`:

    function onError(e) {
      postMessage('ERROR: ' + e.toString());
    }

    try {
      // Error thrown if "log.txt" already exists.
      var fileEntry = fs.root.getFile('log.txt', {create: true, exclusive: true});
    } catch (e) {
      onError(e);
    }


<h2 id="toc-passing-data">Passing around Files, Blobs, and ArrayBuffers</h2>

When Web Workers first came on the scene, they only allowed string data to be
sent in `postMessage()`. Later, browsers began accepting serializable data, which
meant passing a JSON object was possible. Recently however, some browsers like Chrome
accept more complex data types to be passed through `postMessage()` using the
[structured clone algorithm][structuredclone].

What does this really mean? It means that it's now a heck-of-a-lot easier to pass
binary data between main app and worker thread. Browsers that support structured cloning
for workers allow you to pass a Typed Array, `ArrayBuffer`, `File`, or `Blob`
into a worker. Although the data is still a copy, being able to pass a `File` means
a performance benefit over the former approach, which involved base64ing the file
before passing it into `postMessage()`.

The following example passes a user-selected list of files to an inline web worker.
The worker simply passes through the file list and the main app reads each file
as an `ArrayBuffer`. This shows the returned data is a `FileList`.

The sample also uses an improved version of the [inline web worker technique](/tutorials/workers/basics/#toc-inlineworkers)
described in [Basics of Web Workers](/tutorials/workers/basics/).

    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta http-equiv="X-UA-Compatible" content="chrome=1">
      <title>Passing a FileList to a Worker</title>
      <script type="javascript/worker" id="fileListWorker">
      self.onmessage = function(e) {
        // TODO: do something interesting with the files.
        postMessage(e.data); // Pass through.
      };
      </script>
    </head>
    <body>
    </body>

    <input type="file" multiple>

    <script>
    document.querySelector('input[type="file"]').addEventListener('change', function(e) {
      var files = this.files;
      loadInlineWorker('fileListWorker', function(worker) {

        worker.onmessage = function(e) {
          console.log(e.data);
        };

        for (var i = 0, file; file = files[i]; ++i) {
          var reader = new FileReader();
          reader.onload = function(e) {
            console.log(this.result); // this.result is the read file as an ArrayBuffer.
          };
          reader.onerror = function(e) {
            console.log(e);
          };
          reader.readAsArrayBuffer(file);
        }
      });
    }, false);


    function loadInlineWorker(selector, callback) {
      window.URL = window.URL || window.webkitURL || null;
      window.BlobBuilder = window.WebKitBlobBuilder ||
                           window.MozBlobBuilder || window.BlobBuilder;

      var script = document.querySelector(selector);
      if (script.type === 'javascript/worker') {
        var bb = new BlobBuilder();
        bb.append(script.textContent);
        callback(new Worker(window.URL.createObjectURL(bb.getBlob()));
      }
    }
    </script>
    </html>

[structuredclone]: https://developer.mozilla.org/en/DOM/The_structured_clone_algorithm

<h2 id="toc-readingsync">Reading files in a worker</h2>

It's perfectly acceptable to use the asynchronous [`FileReader` API to read files](/tutorials/file/dndfiles/#toc-reading-files) in a worker. However, there's a streamlined synchronous API (`FileReaderSync`)
for workers that we can take advantage of instead:

*Main app:*

    <!DOCTYPE html>
    <html>
    <head>
      <title>Using FileReaderSync Example</title>
      <style>
        #error { color: red; }
      </style>
    </head>
    <body>
    <input type="file" multiple />
    <output id="error"></output>
    <script>
      var worker = new Worker('worker.js');

      worker.onmessage = function(e) {
        console.log(e.data); // e.data should be an array of ArrayBuffers.
      };

      worker.onerror = function(e) {
        document.querySelector('#error').textContent = [
            'ERROR: Line ', e.lineno, ' in ', e.filename, ': ',
            e.message].join('');
      };

      document.querySelector('input[type="file"]').addEventListener('change', function(e) {
        worker.postMessage(this.files);
      }, false);
    </script>
    </body>
    </html>


*worker.js*

    self.addEventListener('message', function(e) {
      var files = e.data;
      var buffers = [];

      // Read each file synchronously as an ArrayBuffer and
      // stash it in a global array to return to the main app.
      [].forEach.call(files, function(file) {
        <b>var reader = new FileReaderSync();</b>
        buffers.push(reader.readAsArrayBuffer(file));
      });

      postMessage(buffers);
    }, false);

As expected, callbacks are gone with the synchronous `FileReader`. This simplifies
the amount of callback nesting when reading files. Instead, the read data is
returned by the readAs* methods, directly.

<h2 id="toc-listing">Example: Fetching all entries</h2>

In some cases, the synchronous API is much cleaner for some tasks. Fewer callbacks
are nice and certainly make things more readable. The real disadvantage of the
synchronous API is due to the limitations of web workers.

For security reasons, data between the calling app and a web worker thread is
never shared. This going to
[change in the future](https://bugs.webkit.org/show_bug.cgi?id=65209), but for
now, data is always copied to and from the worker when `postMessage()` is called.
As a result, not every data type can be passed.

Unfortunately, the `FileEntrySync` and `DirectoryEntrySync` types are not
currently acceptable types. So how can you get entries back to the calling app?
One way to circumvent the limitation is to return a list of [filesystem: URLs](/tutorials/file/filesystem/#toc-filesystemurls) instead of a list of entries. `filesystem:` URLs are just strings,
so they're super easy to pass around. Furthermore, they can be resolved to 
entries in the main app using `resolveLocalFileSystemURL()`. That'll get you back
to a `FileEntrySync`/`DirectoryEntrySync` object.

*Main app:*

    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="chrome=1">
    <title>Listing filesystem entries using the synchronous API</title>
    </head>
    <body>
    <script>
      window.resolveLocalFileSystemURL = window.resolveLocalFileSystemURL ||
                                         window.webkitResolveLocalFileSystemURL;

      var worker = new Worker('worker.js');
      worker.onmessage = function(e) {
        var urls = e.data.entries;
        urls.forEach(function(url, i) {
          window.resolveLocalFileSystemURL(url, function(fileEntry) {
            console.log(fileEntry.name); // Print out file's name.
          });
        });
      };

      worker.postMessage({'cmd': 'list'});
    </script>
    </body>
    </html>

*worker.js*

    self.requestFileSystemSync = self.webkitRequestFileSystemSync ||
                                 self.requestFileSystemSync;

    var paths = []; // Global to hold the list of entry filesystem URLs.

    function getAllEntries(dirReader) {
      var entries = dirReader.readEntries();

      for (var i = 0, entry; entry = entries[i]; ++i) {
        paths.push(entry.toURL()); // Stash this entry's filesystem: URL.

        // If this is a directory, we have more traversing to do.
        if (entry.isDirectory) {
          getAllEntries(entry.createReader());
        }
      }
    }

    function onError(e) {
      postMessage('ERROR: ' + e.toString()); // Forward the error to main app.
    }

    self.onmessage = function(e) {
      var data = e.data;

      // Ignore everything else except our 'list' command.
      if (!data.cmd || data.cmd != 'list') {
        return;
      }

      try {
        var fs = requestFileSystemSync(TEMPORARY, 1024*1024 /*1MB*/);

        getAllEntries(fs.root.createReader());

        self.postMessage({entries: paths});
      } catch (e) {
        onError(e);
      }
    };


<h2 id="toc-download-xhr2">Example: Downloading files using XHR2</h2>

A common use case for using web workers is to download a bunch of files using XHR2,
and write those files to the HTML5 FileSystem. A perfect task for a worker thread!

The following example only fetches and writes one file, but you can image
expanding it to download a set of files.

*Main app:*

    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="chrome=1">
    <title>Download files using a XHR2, a worker, and saving to filesystem</title>
    </head>
    <body>
    <script>
      var worker = new Worker('downloader.js');
      worker.onmessage = function(e) {
        console.log(e.data);
      };
      worker.postMessage({fileName: 'GoogleLogo',
                          url: 'googlelogo.png', type: 'image/png'});
    </script>
    </body>
    </html>

*downloader.js:*

    self.requestFileSystemSync = self.webkitRequestFileSystemSync ||
                                 self.requestFileSystemSync;
    self.BlobBuilder = self.BlobBuilder ||
                       self.WebKitBlobBuilder || self.MozBlobBuilder;

    function makeRequest(url) {
      try {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, false); // Note: synchronous
        xhr.responseType = 'arraybuffer';
        xhr.send();
        return xhr.response;
      } catch(e) {
        return "XHR Error " + e.toString();
      }
    }

    function onError(e) {
      postMessage('ERROR: ' + e.toString());
    }

    onmessage = function(e) {
      var data = e.data;

      // Make sure we have the right parameters.
      if (!data.fileName || !data.url || !data.type) {
        return;
      }
      
      try {
        var fs = requestFileSystemSync(TEMPORARY, 1024 * 1024 /*1MB*/);

        postMessage('Got file system.');

        var fileEntry = fs.root.getFile(data.fileName, {create: true});

        postMessage('Got file handle.');

        var writer = fileEntry.createWriter();
        writer.onerror = onError;
        writer.onwrite = function(e) {
          postMessage('Write complete!');
          postMessage(fileEntry.toURL());
        };

        var bb = new BlobBuilder();
        bb.append(makeRequest(data.url)); // Append the arrayBuffer XHR response.

        postMessage('Begin writing');

        writer.write(bb.getBlob(data.type));
      } catch (e) {
        onError(e);
      }
    };

[fs-spec]: http://dev.w3.org/2009/dap/file-system/file-dir-sys.html
[workers-spec]: http://www.whatwg.org/specs/web-apps/current-work/multipage/workers.html
