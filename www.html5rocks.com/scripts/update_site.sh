#!/bin/bash
#
# Runs compress_js_css.sh before uploading the app to App Engine.
# 
# Note: This script should be used in place of using appcfg.py update directly
# to update the application on App Engine.
#
# Copyright 2011 Eric Bidelman <ericbidelman@chromium.org>

./compress_js_css.sh
appcfg.py update ../
