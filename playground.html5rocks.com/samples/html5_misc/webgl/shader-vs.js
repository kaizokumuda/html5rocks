// if you insert this content inline it makes more sense to put it
// as non-string content of the script tag
var shader-vs = 'attribute vec3 aVertexPosition;'+
'attribute vec2 aTextureCoord;'+
'uniform mat4 uMVMatrix;'+
'uniform mat4 uPMatrix;'+
'varying vec2 vTextureCoord;'+
'void main(void) {'+
  'gl_Position = uPMatrix * uMVMatrix * vec4(aVertexPosition, 1.0);'+
  'vTextureCoord = aTextureCoord;'+
'}';