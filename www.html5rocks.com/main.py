# -*- coding: utf-8 -*-
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

__author__ = ('kurrik@html5rocks.com (Arne Kurrik) ',
              'ericbidelman@html5rocks.com (Eric Bidelman)')


from google.appengine.dist import use_library
use_library('django', '1.2')

# Standard Imports
import datetime
import logging
import os
import re
import yaml

# Libraries
import html5lib
from html5lib import treebuilders, treewalkers, serializer
from html5lib.filters import sanitizer

# Hack to fix templating issue in django 1.2.
from django.conf import settings
settings.configure(INSTALLED_APPS=('nothing',))

# i18n Configuration
from django.utils import translation
from django.utils.translation import ugettext as _
settings.LANGUAGE_CODE = 'en'
settings.USE_I18N = True
settings.ROOT_DIR = os.path.abspath( os.path.dirname( __file__ ) )
settings.LOCALE_PATHS = ( 
  os.path.join( settings.ROOT_DIR, 'conf', 'locale' ),
)

# Google App Engine Imports
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api import memcache

from django.utils import feedgenerator

import common

template.register_template_library('templatetags.templatefilters')

class ContentHandler(webapp.RequestHandler):
  def get_language(self):
    lang_match = re.match( "^/(\w{2,3})(?:/|$)", self.request.path )
    self.locale = lang_match.group(1) if lang_match else settings.LANGUAGE_CODE
    logging.info( "Set Language as %s" % self.locale )
    translation.activate( self.locale )
    return self.locale

  def browser(self):
    return str(self.request.headers['User-Agent'])

  def is_awesome_mobile_device(self):
    browser = self.browser()
    return browser.find('Android') != -1 or browser.find('iPhone') != -1

  def get_toc(self, path):
    toc = memcache.get('toc|%s' % path)
    if toc is None or self.request.cache == False:
      template_text = template.render(path, {});
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

  def get_feed(self, path):
    articles = memcache.get('feed|%s' % path)
    if articles is None or self.request.cache == False:
      template_text = template.render(path, {});
      parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
      dom_tree = parser.parse(template_text)
      walker = treewalkers.getTreeWalker("dom")
      stream = walker(dom_tree)

      def __get_attr(element, attr):
        for a in element['data']:
          if a[0] == attr:
            return a[1]
        return None

      articles = []
      article = None

      for element in stream:
        if element['type'] == 'StartTag':
          if element['name'] in ['h2']:
            article = {}
            article['id'] = __get_attr(element, 'id')
            article['pubdate'] = __get_attr(element, 'data-pubdate')
            if article['pubdate'] is not None:
              article['pubdate'] = datetime.datetime.strptime(
                  article['pubdate'], '%Y-%m-%d')
          if element['name'] == 'a' and article is not None:
            article['href'] = __get_attr(element, 'href')
        elif element['type'] == 'Characters' and article is not None:
          article['title'] = element['data']
        elif element['type'] == 'EndTag' and article is not None:
          articles.append(article)
          article = None

      logging.info(articles)
      memcache.set('feed|%s' % path, articles, 3600)

    return articles

  def render(self, data={}, template_path=None, status=None, message=None, relpath=None):
    if status is not None and status != 200:
      self.response.set_status(status, message)

      # Check if we have a customize error page (template) to display.
      if template_path is None:
        logging.error(message)
        self.response.set_status(status, message)
        self.response.out.write(message)
        return

    current = ''
    if relpath is not None:
      current = relpath.split('/')[0].split('.')[0]

    template_data = {
      'toc' : self.get_toc(template_path),
      'self_url': self.request.url,
      'host': '%s://%s' % (self.request.scheme, self.request.host),
      'is_mobile': self.is_awesome_mobile_device(),
      'current': current,
      'prod': common.PROD
    }

    # Request was for an Atom feed. Render one!
    if self.request.path.endswith('.xml'):
      self.render_atom_feed(template_path, self.get_feed(template_path))
      return

    template_data.update(data)
    if not 'category' in template_data:
      template_data['category'] = 'this feature'

    # Add CORS support entire site.
    self.response.headers.add_header('Access-Control-Allow-Origin', '*')
    self.response.headers.add_header('X-UA-Compatible', 'IE=Edge,chrome=1')
    self.response.out.write(template.render(template_path, template_data))

  def render_atom_feed(self, template_path, data):
    prefix = '%s://%s' % (self.request.scheme, self.request.host)
    logging.info(prefix)

    feed = feedgenerator.Atom1Feed(
        title=u'HTML5Rocks - Tutorials',  # TODO: make generic for any page.
        link=prefix,
        description=u'Take a guided tour through code that uses HTML5.',
        language=u'en'
        )
    for tutorial in data:
      feed.add_item(
          title=tutorial['title'],
          link=prefix + tutorial['href'],
          description=u'',  # TODO: parse this out out of the html and fill it.
          pubdate=tutorial['pubdate']
          )
    self.response.headers.add_header('Content-Type', 'application/atom+xml')
    self.response.out.write(feed.writeString('utf-8'))

  def get(self, relpath):
    locale = self.get_language()

    if self.request.get('cache', '1') == '0':
      self.request.cache = False
    else:
      self.request.cache = True

    basedir = os.path.dirname(__file__)

    logging.info('relpath: ' + relpath)

    # Strip off leading `/[en|de|fr|...]/`
    relpath = re.sub( '^/?\w{2,3}/?', '', relpath )

    # Landing page or /tutorials|features|mobile\/?
    if ((relpath == '' or relpath[-1] == '/') or  # Landing page.
       (relpath in ['mobile', 'tutorials', 'features'] and relpath[-1] != '/')):
      path = os.path.join(basedir, 'content', relpath, 'index.html')
    else:
      path = os.path.join(basedir, 'content', relpath)

    # Render the .html page if it exists. Otherwise, check that the Atom feed
    # the user is requesting has a corresponding .html page that exists.

    if (relpath == 'profiles' or relpath == 'profiles/'):
      # Setup caching layer for this file i/o.
      profiles = common.get_profiles()
      sorted_profiles = sorted(profiles.values(),
                               key=lambda profile:profile['name']['family'])
      self.render(data={'sorted_profiles': sorted_profiles},
                  template_path='content/profiles.html', relpath=relpath)

    if (relpath == 'tutorials' or relpath == 'tutorials'):
      # Tutorials look like this on the filesystem:
      #
      #   .../tutorials +
      #                 |
      #                 +-- article-slug  +
      #                 |                 |
      #                 |                 +-- en  +
      #                 |                 |       |
      #                 |                 |       +-- index.html
      #                 ...
      #
      # So, to determine if an HTML page exists for the requested language
      # `split` the file's path, add in the locale, and check existance:
      logging.info('Building request for `%s` in locale `%s`', path, locale)
      (dir, filename) = os.path.split(path)
      if os.path.isfile( os.path.join( dir, locale, filename ) ):
        self.render(template_path=os.path.join( dir, locale, filename ))

      # If the localized file doesn't exist, and the locale isn't English, look
      # for an english version of the file, and redirect the user there if
      # it's found:
      elif os.path.isfile( os.path.join( dir, "en", filename ) ):
        self.redirect( "/en/%s?redirect_from_locale=%s" % (relpath, locale) )
    elif os.path.isfile(path):
      self.render(data={}, template_path=path, relpath=relpath)
    elif os.path.isfile(path[:path.rfind('.')] + '.html'):
      self.render(data={}, template_path=path[:path.rfind('.')] + '.html',
                  relpath=relpath)
    elif os.path.isfile(path + '.html'):
      self.render(data={'category': relpath.replace('features/', '')},
                  template_path=path + '.html', relpath=relpath)
    else:
      self.render(status=404, message='Page Not Found',
                  template_path=os.path.join(basedir, 'templates/404.html'))


def main():
  application = webapp.WSGIApplication([
    ('/(.*)', ContentHandler)
  ], debug=False)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
