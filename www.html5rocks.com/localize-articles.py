# -*- coding: utf-8 -*-
# Copyright 2011 Google Inc.
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
from __future__ import with_statement

__author__ = ('mkwst@google.com (Mike West)')

import os
import re
from optparse import OptionParser

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

class Article(object):
  DJANGO_ROOT = os.path.join(ROOT_DIR, 'content', 'tutorials')
  HTML_ROOT = os.path.join(ROOT_DIR, '_to_localize')

  def __init__(self, django=None, html=None):
    self.django_ = os.path.abspath(django) if django else ""
    self.html_ = os.path.abspath(html) if html else ""
    self.normalizePaths_()

  def normalizePaths_(self):
    if not self.django_:
      self.django_ = re.sub(r'^%s' % Article.HTML_ROOT,
                            Article.DJANGO_ROOT,
                            self.html_) 
    if not self.html_:
      self.html_ = re.sub(r'^%s' % Article.DJANGO_ROOT,
                          Article.HTML_ROOT,
                          self.django_)

  def generateHTML(self):
    try:
      os.makedirs(os.path.dirname(self.html_))
    except os.error:
      pass
    with open(self.html_, 'w') as outfile:
      print "* `%s`" % self.html_
      with open(self.django_, 'r') as infile:
        for line in infile:
          outfile.write(re.sub(r'({%.+?%})',
                               r'<!--DJANGO>\1</DJANGO-->',
                               line))

  def generateDjango(self):
    with open(self.html_, 'r') as infile:
      with open(self.django_, 'w') as outfile:
        for line in infile:
          outfile.write(re.sub(r'<!--DJANGO>({%.+?%}</DJANGO-->',
                               r'\1',
                               line))



  def __str__(self):
    return """Article:
- HTML Path:   `%s`
- Django Path: `%s`""" % (self.html_, self.django_)

class Localizer(object):
  def __init__(self, root):
    self.root_ = root
    self.articles_ = []

  def scan(self):
    self.articles_ = []
    for root, dirs, files in os.walk(Article.DJANGO_ROOT):
      for name in files:
        if not name == '.DS_Store' and re.search(r'\/en$', root):
          self.articles_.append(Article(django=os.path.join(root,name)))

  def htmlize(self):
    print """
Generating Localizable HTML
===========================
"""
    for article in self.articles_:
      article.generateHTML()

  def djangoize(self):
    # TODO(mkwst): I should implement this function. :)
    print "Not finished yet. Come back later."

def main():
  parser = OptionParser()
  parser.add_option('--generate_html', dest="generate_html",
                    help="Generate HTML from Django templated articles.",
                    default=False, action="store_true")
  parser.add_option('--generate_django', dest="generate_django",
                    help="Generate Django templates from localized HTML articles.",
                    default=False, action="store_true")

  (options, args) = parser.parse_args()
  if not options.generate_html or options.generate_django:
    parser.error("You must specify either `--generate_html` or `--generate_django`.")

  l10n = Localizer(ROOT_DIR)
  l10n.scan()
  if options.generate_html:
    l10n.htmlize()
  if options.generate_django:
    l10n.djangoize()

if (__name__ == "__main__"):
  main()
