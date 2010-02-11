#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Standard Imports
import os
import logging

# Google App Engine Imports
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

class ContentHandler(webapp.RequestHandler):
  def render(self, data={}, template_path={}, status=None, message=None):
    if status is not None and status != 200:
      logging.error(message)
      self.response.set_status(status, message)
      self.response.out.write(message)
      return 

    self.response.headers.add_header('Content-Type', 'text/html;charset=UTF-8')
    self.response.out.write(webapp.template.render(template_path, data))

  def get(self, relpath):
    basedir = os.path.dirname(__file__)
    logging.info(relpath)

    if relpath == "" or relpath[-1:] == '/':
      path = os.path.join(basedir, "content", relpath, 'index.html')
    else:
      path = os.path.join(basedir, "content", relpath)
      
    logging.info(path)
    if os.path.exists(path):
      self.render(template_path=path)
    else:
      self.render(status=404, message="Sample not found")

class MainHandler(webapp.RequestHandler):
  def get(self):
    self.redirect('/samples/', False)   # Not permanent redirect


def main():
  application = webapp.WSGIApplication([
    ('/samples/(.*)', ContentHandler),
    ('/.*', MainHandler),
  ], debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
