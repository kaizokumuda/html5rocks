// classlist, [].indexOf, placeholder


/*
 * classList.js: Cross-browser full element.classList implementation.
 * 2011-06-15
 *
 * By Eli Grey, http://eligrey.com
 * Public Domain.
 * NO WARRANTY EXPRESSED OR IMPLIED. USE AT YOUR OWN RISK.
 */

/*global self, document, DOMException */

/*! @source http://purl.eligrey.com/github/classList.js/blob/master/classList.js*/

if (typeof document !== "undefined" && !("classList" in document.createElement("a"))) {

(function (view) {

"use strict";

var
	  classListProp = "classList"
	, protoProp = "prototype"
	, elemCtrProto = (view.HTMLElement || view.Element)[protoProp]
	, objCtr = Object
	, strTrim = String[protoProp].trim || function () {
		return this.replace(/^\s+|\s+$/g, "");
	}
	, arrIndexOf = Array[protoProp].indexOf || function (item) {
		var
			  i = 0
			, len = this.length
		;
		for (; i < len; i++) {
			if (i in this && this[i] === item) {
				return i;
			}
		}
		return -1;
	}
	// Vendors: please allow content code to instantiate DOMExceptions
	, DOMEx = function (type, message) {
		this.name = type;
		this.code = DOMException[type];
		this.message = message;
	}
	, checkTokenAndGetIndex = function (classList, token) {
		if (token === "") {
			throw new DOMEx(
				  "SYNTAX_ERR"
				, "An invalid or illegal string was specified"
			);
		}
		if (/\s/.test(token)) {
			throw new DOMEx(
				  "INVALID_CHARACTER_ERR"
				, "String contains an invalid character"
			);
		}
		return arrIndexOf.call(classList, token);
	}
	, ClassList = function (elem) {
		var
			  trimmedClasses = strTrim.call(elem.className)
			, classes = trimmedClasses ? trimmedClasses.split(/\s+/) : []
			, i = 0
			, len = classes.length
		;
		for (; i < len; i++) {
			this.push(classes[i]);
		}
		this._updateClassName = function () {
			elem.className = this.toString();
		};
	}
	, classListProto = ClassList[protoProp] = []
	, classListGetter = function () {
		return new ClassList(this);
	}
;
// Most DOMException implementations don't allow calling DOMException's toString()
// on non-DOMExceptions. Error's toString() is sufficient here.
DOMEx[protoProp] = Error[protoProp];
classListProto.item = function (i) {
	return this[i] || null;
};
classListProto.contains = function (token) {
	token += "";
	return checkTokenAndGetIndex(this, token) !== -1;
};
classListProto.add = function (token) {
	token += "";
	if (checkTokenAndGetIndex(this, token) === -1) {
		this.push(token);
		this._updateClassName();
	}
};
classListProto.remove = function (token) {
	token += "";
	var index = checkTokenAndGetIndex(this, token);
	if (index !== -1) {
		this.splice(index, 1);
		this._updateClassName();
	}
};
classListProto.toggle = function (token) {
	token += "";
	if (checkTokenAndGetIndex(this, token) === -1) {
		this.add(token);
	} else {
		this.remove(token);
	}
};
classListProto.toString = function () {
	return this.join(" ");
};

if (objCtr.defineProperty) {
	var classListPropDesc = {
		  get: classListGetter
		, enumerable: true
		, configurable: true
	};
	try {
		objCtr.defineProperty(elemCtrProto, classListProp, classListPropDesc);
	} catch (ex) { // IE 8 doesn't support enumerable:true
		if (ex.number === -0x7FF5EC54) {
			classListPropDesc.enumerable = false;
			objCtr.defineProperty(elemCtrProto, classListProp, classListPropDesc);
		}
	}
} else if (objCtr[protoProp].__defineGetter__) {
	elemCtrProto.__defineGetter__(classListProp, classListGetter);
}

}(self));

}




if (!Array.prototype.indexOf)
{
  Array.prototype.indexOf = function(searchElement /*, fromIndex */)
  {
    "use strict";

    if (this === void 0 || this === null)
      throw new TypeError();

    var t = Object(this);
    var len = t.length >>> 0;
    if (len === 0)
      return -1;

    var n = 0;
    if (arguments.length > 0)
    {
      n = Number(arguments[1]);
      if (n !== n) // shortcut for verifying if it's NaN
        n = 0;
      else if (n !== 0 && n !== (1 / 0) && n !== -(1 / 0))
        n = (n > 0 || -1) * Math.floor(Math.abs(n));
    }

    if (n >= len)
      return -1;

    var k = n >= 0
          ? n
          : Math.max(len - Math.abs(n), 0);

    for (; k < len; k++)
    {
      if (k in t && t[k] === searchElement)
        return k;
    }
    return -1;
  };
}




// https://github.com/NV/placeholder.js

/**
 * Example: inputPlaceholder( document.getElementById('my_input_element') )
 * @param {Element} input
 * @param {String} [color='#AAA']
 * @return {Element} input
 */
function inputPlaceholder (input, color) {

	if (!input) return null;

	// Do nothing if placeholder supported by the browser (Webkit, Firefox 3.7)
	if (input.placeholder && 'placeholder' in document.createElement(input.tagName)) return input;

	color = color || '#AAA';
	var default_color = input.style.color;
	var placeholder = input.getAttribute('placeholder');

	if (input.value === '' || input.value == placeholder) {
		input.value = placeholder;
		input.style.color = color;
		input.setAttribute('data-placeholder-visible', 'true');
	}

	var add_event = /*@cc_on'attachEvent'||@*/'addEventListener';

	input[add_event](/*@cc_on'on'+@*/'focus', function(){
	 input.style.color = default_color;
	 if (input.getAttribute('data-placeholder-visible')) {
		 input.setAttribute('data-placeholder-visible', '');
		 input.value = '';
	 }
	}, false);

	input[add_event](/*@cc_on'on'+@*/'blur', function(){
		if (input.value === '') {
			input.setAttribute('data-placeholder-visible', 'true');
			input.value = placeholder;
			input.style.color = color;
		} else {
			input.style.color = default_color;
			input.setAttribute('data-placeholder-visible', '');
		}
	}, false);

	input.form && input.form[add_event](/*@cc_on'on'+@*/'submit', function(){
		if (input.getAttribute('data-placeholder-visible')) {
			input.value = '';
		}
	}, false);

	return input;
}


/*
@name HTML 5 dataset Support
@version 0.0.2
@home http://code.eligrey.com/html5/dataset/
@author Elijah Grey - eligrey.com
@license http://www.gnu.org/licenses/lgpl.html
*/
Element.prototype.setDataAttribute = function(name, value) {
	if ( value !== undefined ) return this.setAttribute('data-'+name, value);
	else return this.removeDataAttribute(name);
};
Element.prototype.removeDataAttribute = function(name) {
	return this.removeAttribute('data-'+name);
};
Element.prototype.setDataAttributes = function(items) {
	if ( items instanceof Object ) {
		for (attr in items) if ( items.hasOwnProperty(attr) ) this.setDataAttribute(attr, items[attr]);
	}
};
if ( !Element.prototype.__lookupGetter__("dataset") ) {
	Element.prototype.__defineGetter__("dataset", function() {
	  try { // simulate DOMStringMap w/accessor support
	    var getter_test = {};
	    getter_test.__defineGetter__("test", function(){}); // test setting accessor on normal object
	    delete getter_test;
	    var HTML5_DOMStringMap = {};
	  } catch(e) { var HTML5_DOMStringMap = document.createElement("div") } // use a DOM object for IE8
	  function lambda(o) { return function(){return o} };
	  function dataSetterFunc(ref_el, attrName) { return function(val){ return ref_el.setDataAttribute(attrName, val) } };
	  for ( attr in this.attributes ) {
		if ( this.attributes.hasOwnProperty(attr) && this.attributes[attr].name && /^data-[a-z_\-\d]*$/i.test(this.attributes[attr].name) ) {
			var attrName = this.attributes[attr].name.substr(5), attrVal = this.attributes[attr].value;
			try {
				HTML5_DOMStringMap.__defineGetter__(attrName, lambda(attrVal || '') );
				HTML5_DOMStringMap.__defineSetter__(attrName, dataSetterFunc(this, attrName) );
			}
			catch (e) { HTML5_DOMStringMap[attrName] = attrVal } // if accessors are not working
		}
	  }
	  return HTML5_DOMStringMap;
	});
}

