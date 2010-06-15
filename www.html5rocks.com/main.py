# Copyright 2010 Google Inc.
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

# Libraries
import html5lib
from html5lib import treebuilders, treewalkers, serializer
from html5lib.filters import sanitizer

# Google App Engine Imports
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

webapp.template.register_template_library('templatefilters')


class ContentHandler(webapp.RequestHandler):
  def get_toc(self, path):
    toc = memcache.get('toc|%s' % path)
    if toc is None or self.request.cache == False:
      template_text = webapp.template.render(path, {});
      parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
      dom_tree = parser.parse(template_text)
      walker = treewalkers.getTreeWalker("dom")
      stream = walker(dom_tree)
      toc = []
      current = None
      for element in stream:
        if element['type'] == 'StartTag':
          if element['name'] in ['h2', 'h3', 'h4']:
            for attr in element['data']:
              if attr[0] == 'id':
                current = {
                  'level' : int(element['name'][-1:]) - 1,
                  'id' : attr[1]
                }
        elif element['type'] == 'Characters' and current is not None:
          current['text'] = element['data']
        elif element['type'] == 'EndTag' and current is not None:
          toc.append(current)
          current = None
      memcache.set('toc|%s' % path, toc, 3600)
    return toc

  def render(self, data={}, template_path=None, status=None, message=None):
    if status is not None and status != 200:
      logging.error(message)
      self.response.set_status(status, message)
      self.response.out.write(message)
      return 

    template_data = {
      'toc' : self.get_toc(template_path)
    }
    template_data.update(data)
    self.response.headers.add_header('Content-Type', 'text/html;charset=UTF-8')
    self.response.out.write(webapp.template.render(template_path, template_data))

  def get(self, relpath):
    if self.request.get('cache', '1') == '0':
      self.request.cache = False
    else:
      self.request.cache = True
    
    basedir = os.path.dirname(__file__)

    logging.info(relpath)

    if relpath == "" or relpath[-1:] == '/':
      path = os.path.join(basedir, 'content', relpath, 'index.html')  # Landing page.
    else:
      path = os.path.join(basedir, 'content', relpath)

    logging.info(path)
    if os.path.isfile(path):
      self.render(template_path=path)
    else:
      self.render(status=404, message='Sample not found')


def main():
  application = webapp.WSGIApplication([
    ('/(.*)', ContentHandler)
  ], debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
