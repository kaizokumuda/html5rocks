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

# Use Django 1.2.
from google.appengine.dist import use_library
use_library('django', '1.2')

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_settings'

from django import http
from django.conf import settings
from django.utils import feedgenerator
from django.utils import translation
from django.utils.translation import ugettext as _

# Google App Engine Imports
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import common

template.register_template_library('templatetags.templatefilters')

class ContentHandler(webapp.RequestHandler):
  def get_language(self):
    lang_match = re.match("^/(\w{2,3})(?:/|$)", self.request.path)
    self.locale = lang_match.group(1) if lang_match else settings.LANGUAGE_CODE
    logging.info("Set Language as %s" % self.locale)
    translation.activate( self.locale )
    return self.locale if lang_match else None

  def browser(self):
    return str(self.request.headers['User-Agent'])

  def is_awesome_mobile_device(self):
    browser = self.browser()
    return browser.find('Android') != -1 or browser.find('iPhone') != -1

  def get_toc(self, path):
    if not (re.search('', path) or re.search('/mobile/', path)):
      return ''

    toc = memcache.get('toc|%s' % path)
    if toc is None or not self.request.cache:
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
    if articles is None or not self.request.cache:
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

    # Strip out language code from path. Urls changed for i18n work and correct
    # disqus comment thread won't load with the changed urls.
    path_no_lang = re.sub('^\/\w{2,3}\/', '', self.request.path, 1)

    template_data = {
      'toc' : self.get_toc(template_path),
      'self_url': self.request.url,
      'host': '%s://%s' % (self.request.scheme, self.request.host),
      'is_mobile': self.is_awesome_mobile_device(),
      'current': current,
      'prod': common.PROD
    }

    template_data['disqus_url'] = template_data['host'] + '/' + path_no_lang

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

  def post(self, relpath):
    if (relpath == 'database/submit'):
      try:
        sample = common.Author(key_name = self.request.get('key_name'),
                               given_name = self.request.get('given_name'),
                               family_name = self.request.get('family_name'),
                               org = self.request.get('org'),
                               unit = self.request.get('unit'),
                               city = self.request.get('city'),
                               state = self.request.get('state'),
                               country = self.request.get('country'),
                               geo_location = self.request.get('geo_location') or None,
                               homepage = self.request.get('homepage') or None,
                               google_account = self.request.get('google_account') or None,
                               twitter_account = self.request.get('twitter_account') or None,
                               email = self.request.get('email') or None,
                               lanyrd = self.request.get('lanyrd') == 'on')
        sample.put()
      except db.Error:
        pass
      else:
        return self.redirect('/database/edit')

  def get(self, relpath):

    # Render uncached verion of page with ?cache=1
    if self.request.get('cache', default_value='1') == '1':
      self.request.cache = True
    else:
      self.request.cache = False

    # Handle humans before locale, to prevent redirect to /en/
    # (but still ensure it's dynamic, ie we can't just redirect to a static url)
    if (relpath == 'humans.txt'):
      self.response.headers['Content-Type'] = 'text/plain'
      return self.render(data={'sorted_profiles': common.get_sorted_profiles(),
                               'profile_amount': common.get_profile_amount() },
                         template_path='content/humans.txt',
                         relpath=relpath)

    elif (relpath == 'database/load_author_information'):
      self.addAuthorInformations()
      return self.redirect('/database/edit')

    elif (relpath == 'database/new'):
      # adds a new author information into DataStore
      return self.render(data={'author_form': common.AuthorForm()},
                         template_path='database/author_new.html',
                         relpath=relpath)

    elif (relpath == 'database/edit'):
      if common.PROD:
        datastore_console_url = 'https://appengine.google.com/datastore/admin?&app_id=%s&version_id=%s' % (os.environ['APPLICATION_ID'], os.environ['CURRENT_VERSION_ID'])
      else:
        datastore_console_url = 'http://%s/_ah/admin/datastore' % os.environ['HTTP_HOST']

      return self.redirect(datastore_console_url, permanent=True)

    # Get the locale: if it's "None", redirect to English
    locale = self.get_language()
    if not locale:
      return self.redirect( "/en/%s" % relpath, permanent=True)

    basedir = os.path.dirname(__file__)

    # Strip off leading `/[en|de|fr|...]/`
    relpath = re.sub('^/?\w{2,3}/', '', relpath)

    # Are we looking for a feed?
    is_feed = self.request.path.endswith('.xml')

    logging.info('relpath: ' + relpath)

    # Setup handling of redirected article URLs: If a user tries to access an
    # article from a non-supported language, we'll redirect them to the English
    # version (assuming it exists), with a `redirect_from_locale` GET param.
    redirect_from_locale = self.request.get('redirect_from_locale', '')
    if not re.match('[a-zA-Z]{2,3}$', redirect_from_locale):
      redirect_from_locale = False
    else:
      translation.activate(redirect_from_locale)
      redirect_from_locale = {
        'lang': redirect_from_locale,
        'msg': _("Sorry, this article isn't available in your native language; we've redirected you to the English version.")
      }
      translation.activate(locale);

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
      self.render(data={'sorted_profiles': common.get_sorted_profiles() },
                  template_path='content/profiles.html', relpath=relpath)

    elif re.search('tutorials/casestudies', relpath) and not is_feed:
      # Case Studies look like this on the filesystem:
      #
      #   .../tutorials +
      #                 |
      #                 +-- casestudies   +
      #                 |                 |
      #                 |                 +-- en  +
      #                 |                 |       |
      #                 |                 |       +-- case_study_name.html
      #                 ...
      #
      # So, to determine if an HTML page exists for the requested language
      # `split` the file's path, add in the locale, and check existance:
      logging.info('Building request for casestudy `%s` in locale `%s`', path, locale)
      potentialfile = re.sub('tutorials/casestudies',
                             'tutorials/casestudies/%s' % locale,
                             path)
      englishfile = re.sub('tutorials/casestudies',
                           'tutorials/casestudies/%s' % 'en',
                           path)
      logging.info(englishfile)
      if os.path.isfile(potentialfile):
        logging.info('Rendering in native: %s' % potentialfile)

        self.render(template_path=potentialfile,
                    data={'redirect_from_locale': redirect_from_locale},
                    relpath=relpath)

      # If the localized file doesn't exist, and the locale isn't English, look
      # for an english version of the file, and redirect the user there if
      # it's found:
      elif os.path.isfile( englishfile ):
        return self.redirect( "/en/%s?redirect_from_locale=%s" % (relpath, locale) )


    elif ((re.search('tutorials/.+', relpath) or re.search('mobile/.+', relpath))
          and not is_feed):
      # If no trailing / (e.g. /tutorials/blah/blah), append index.html file.
      if (relpath[-1] != '/' and not relpath.endswith('.html')):
        path += '/index.html'

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
        self.render(template_path=os.path.join( dir, locale, filename ),
                    data={'redirect_from_locale': redirect_from_locale},
                    relpath=relpath)

      # If the localized file doesn't exist, and the locale isn't English, look
      # for an english version of the file, and redirect the user there if
      # it's found:
      elif os.path.isfile( os.path.join( dir, "en", filename ) ):
        return self.redirect( "/en/%s?redirect_from_locale=%s" % (relpath, locale) )
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

  def addAuthorInformations(self):
    sample = common.Author(key_name = 'hanrui', given_name = u'Hanrui', family_name = u'Gao',
                           org = u'Google', unit = u'Developer Relations',
                           city = u'Beijing', state = u'Beijing', country = u'China',
                           google_account = u'hanrui.gao', twitter_account = u'hanruigao',
                           email = 'hanrui@google.com')
    sample.put()

    sample = common.Author(key_name = 'ebidelman', given_name = u'Eric', family_name = u'Bidelman',
                           org = u'Google', unit = u'Developer Relations',
                           city = u'Mountain View', state = u'California', country = u'USA',
                           geo_location = '37.42192,-122.087824', homepage = 'http://ebidel.com',
                           google_account = u'ebidel', twitter_account = u'ebidel',
                           email = 'e.bidelman@google.com')
    sample.put()

    sample = common.Author(key_name = 'ernestd', given_name = u'Ernest', family_name = u'Delgado',
                           org = u'Google', unit = u'Developer Relations',
                           city = u'Mountain View', state = u'California', country = u'USA',
                           geo_location = '37.42192,-122.087824', homepage = 'http://ernestdelgado.com/',
                           google_account = u'ernestd', twitter_account = u'edr',
                           email = 'ernestd@google.com')
    sample.put()

    sample = common.Author(key_name = 'paulkinlan', given_name = u'Paul', family_name = u'Kinlan',
                           org = u'Google', unit = u'Developer Relations',
                           city = u'London', state = u'London', country = u'UK',
                           geo_location = '51.4948,-0.1467', homepage = 'http://paul.kinlan.me',
                           google_account = u'paul.kinlan', twitter_account = u'paul_kinlan',
                           email = 'paul.kinlan@google.com', lanyrd = True)
    sample.put()

    sample = common.Author(key_name = 'michaeldewey', given_name = u'Mike', family_name = u'Dewey',
                           org = u'deviantART', unit = u'Muro',
                           city = u'Oakland', state = u'California', country = u'USA',
                           geo_location = '37.8043637,-122.2711137')
    sample.put()

def main():
  application = webapp.WSGIApplication([
    ('/(.*)', ContentHandler)
  ], debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
