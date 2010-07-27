// if you insert this content inline it makes more sense to put it
// as non-string content of the script tag
var shader-fs = 'varying vec2 vTextureCoord;'+
'uniform sampler2D uSampler;'+
'void main(void) {'+
'gl_FragColor = texture2D(uSampler, vec2(vTextureCoord.s, 1.0 - vTextureCoord.t));'+
'}';