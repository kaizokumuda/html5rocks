// Content section used alot
var content = document.getElementById('content');

if (!window.FileReader) {
	content.innerHTML = "<p>This browser doesnt support the File API</p>";
} else {
	// Page Layout
	content.innerHTML =
		"<p>Pick a file below or drag one into this area <br> <input type='file' id='file' /></p>" +
		"<p><b>Name:</b> <span id='name'></span><br>" +
		"<b>File Size:</b> <span id='size'></span><br>" +
		"<b>Content:</b> <br><br> <span id='file-content'></span>" +
		"</p>";

	// Simple print out of file
	function displayFile(file) {
		document.getElementById('name').innerHTML = file.fileName;
		document.getElementById('size').innerHTML = file.fileSize;

		var reader = new FileReader();

		reader.onload = function(event) {
			document.getElementById('file-content').innerHTML = 
				event.target.result.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n|\r/g, "<br>");
		};

		reader.onerror = function() {
			document.getElementById('file-content').innerHTML = "Unable to read " + file.fileName;
		};

		reader.readAsBinaryString(file);
	}

	// Input handler
	document.getElementById('file').onchange = function() {
		displayFile(this.files[0]);
	};

	// Reduce movement by adding invisible border
	content.style.border = '4px solid transparent';

	// Add dragging events
	content.ondragenter = function() {
		content.style.border = '4px solid #b1ecb3';
		return false;
	};

	content.ondragover = function() {
		return false;
	};

	content.ondragleave = function() {
		return false;
	};

	content.ondrop = function(event) {
		content.style.border = '4px solid transparent';
		displayFile(event.dataTransfer.files[0]);
		return false;
	};
}