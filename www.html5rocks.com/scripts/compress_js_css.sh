#!/bin/bash
#
# Runs YUI Compressor on the css and js of the entire site.
#
# Copyright 2011 Eric Bidelman <ericbidelman@chromium.org>

CSS_EXT=css
JS_EXT=js
CSSDIR='../static/css'
JSDIR='../static/js'

YUI_COMPRESSOR=yuicompressor-2.4.4.jar

JS_FILES=("${JSDIR}/profiles.${JS_EXT}" "${JSDIR}/prettify.${JS_EXT}" "${JSDIR}/feature.${JS_EXT}")

#if [[ "$1" == "" ]]; then
#  echo 'Usage '$0' <inputfile.js|css>' >&2
#  exit
#fi

# Remove existing *.min.css files.
rm ${CSSDIR}/*.min.$CSS_EXT

for i in $CSSDIR/*.$CSS_EXT; do
  # $1=./path/to/file.css -> filename=file.css, name=file, ext=css, dir=./path/to
  filename=`basename $i`
  name=`basename ${filename%%.*}`
  ext=`basename ${filename##*.}`
  dir=`dirname $i`
  java -jar ${YUI_COMPRESSOR} -v $i -o $dir/$name.min.$ext
done

for i in ${JS_FILES[*]}; do
  filename=`basename $i`
  name=`basename ${filename%%.*}`
  ext=`basename ${filename##*.}`
  dir=`dirname $i`
  java -jar ${YUI_COMPRESSOR} -v $i -o $dir/$name.min.$ext
done
