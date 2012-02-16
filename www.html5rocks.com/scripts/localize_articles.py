#!/usr/bin/python
# Copyright 2011 Google Inc. All Rights Reserved.
# -*- coding: utf-8 -*-
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

"""Generates HTML from Django, and Django from HTML for localization."""

from __future__ import with_statement

__author__ = ('mkwst@google.com (Mike West)')

import optparse
import os
import re

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

class TextProcessor(object):
  """A singleton that provides text processing methods to move from Django
     templates to localizable HTML, and from localized HTML to Django template
     format.
  """
  
  UNTRANSLATABLE_BEGIN = r'<!--DO_NOT_TRANSLATE_BLOCK>'
  UNTRANSLATABLE_END = r'</DO_NOT_TRANSLATE_BLOCK-->'

  CONTENT_BEGIN = """
<!--CONTENT_BLOCK ***********************************************************-->
"""
  CONTENT_END = """
<!--/END_CONTENT_BLOCK ******************************************************-->
"""

  def django_to_html(self, text):
    """Given a Django template's content, return HTML suitable for l10n.

    Args:
      text: The text to convert from Django to HTML.

    Returns:
      A string containing the newly HTMLized content.

      * Django tags like `{% tag %}` will be rendered inside an HTML comment:
        `<!--DO_NOT_TRANSLATE_BLOCK>{% tag %}</DO_NOT_TRANSLATE_BLOCK-->`.

      * `pre`, `script`, and `style` tags' content will be likewise wrapped:
        `<pre><!--DO_NOT_TRANSLATE_BLOCK>Text!</DO_NOT_TRANSLATE_BLOCK-->`.

      * The article's content will be wrapped:

        <!--CONTENT_BLOCK ***********************************************************-->
        Content goes here!
        <!--END_CONTENT_BLOCK *******************************************************-->
    """
    UNESCAPED_DJANGO = r'(?P<tag>{%.+?%})'
    ESCAPED_DJANGO = r'%s\g<tag>%s' % (self.UNTRANSLATABLE_BEGIN,
                                       self.UNTRANSLATABLE_END,)

    UNESCAPED_UNTRANSLATABLE = r'(?P<tag><(?:pre|script|style)[^>]*?>)'
    ESCAPED_UNTRANSLATABLE = r'\g<tag>%s' % self.UNTRANSLATABLE_BEGIN

    UNESCAPED_UNTRANSLATABLE_END = r'(?P<tag></(?:pre|script|style)[^>]*?>)'
    ESCAPED_UNTRANSLATABLE_END = r'%s\g<tag>' % self.UNTRANSLATABLE_END

    CONTENT_BEGIN = r'{% block content %}'
    CONTENT_END = r'{% endblock %}'
   
    # Walk the given text line by line
    to_return = []
    in_content = False
    for line in text.splitlines(True):
      # Process Django tags
      line = re.sub(UNESCAPED_DJANGO, ESCAPED_DJANGO, line)
      # Preprocess script/pre/style blocks
      line = re.sub(UNESCAPED_UNTRANSLATABLE, ESCAPED_UNTRANSLATABLE, line)
      line = re.sub(UNESCAPED_UNTRANSLATABLE_END,
                    ESCAPED_UNTRANSLATABLE_END,
                    line)
      # Preprocess content block
      if re.search(CONTENT_BEGIN, line):
        line = self.CONTENT_BEGIN
        in_content = True
      elif re.search(CONTENT_END, line) and in_content:
        line = self.CONTENT_END
        in_content = False

      to_return.append(line)

    return ''.join(to_return)

  def html_to_django(self, text):
    """Given localized HTML, return text formatted as a Django template.

    Args:
      text: The text to convert from HTML to Django.

    Returns:
      A string containing the newly Djangoized content, stripped of leading
      and trailing whitespace.

      See the documentation for `django_to_html` and imagine the inverse. :)
    """
    # Strip UNTRANSLATABLE_BEGIN and UNTRANSLATABLE_END comments.
    text = text.replace(self.UNTRANSLATABLE_BEGIN, '')
    text = text.replace(self.UNTRANSLATABLE_END, '')

    # Replace CONTENT_BEGIN with `{% block content %}` and CONTENT_END with
    # `{% endblock %}`.
    text = text.replace(self.CONTENT_BEGIN, '{% block content %}\n')
    text = text.replace(self.CONTENT_END, '{% endblock %}')

    # Return the result, stripped of leading/training whitespace.
    return text.strip()

class ArticleException(Exception):
  pass

class Article(object):
  """Represents an article.
  
  Articles live at `{Article.ROOT}/path/to/article`, and can have one or more
  localizations, which live at `{Article.ROOT}/path/to/article/{locale}`. This
  class allows a mapping between a single article in three states:
  
  1. An article's finished localizations.
  2. An unlocalized representation of the article in HTML format.
  3. A newly localized instance of the article in a specific locale.

  Attributes:
    path: The path to the article's root: `{Article.ROOT}/path/to/article`.
    locales: The article's available completed localizations.
  """

  def __init__(self, path):
    if not os.path.exists(path):
      raise ArticleException('`%s` does not exist.' % path)

    self.path = path


  @property
  def locales(self):





# class Article(object):
  # """Represents an article, and maps back and forth between Django and HTML.

  # Attributes:
    # DJANGO_ROOT: The root directory in which Django templates are found.
    # UNLOCALIZED_ROOT: The root directory in which unlocalized files are found .
    # django_: The absolute path to a specific Django template.
  # """
  # DJANGO_ROOT = os.path.abspath(os.path.join(ROOT_DIR, '..', 'content'))
  # UNLOCALIZED_ROOT = os.path.abspath(os.path.join(ROOT_DIR, '..', '_to_localize'))
  # LOCALIZED_ROOT = os.path.abspath(os.path.join(ROOT_DIR, '..', '_localized'))


  # PATH_DELIMITER = """___---___"""

  # def __init__(self, original_file=None):
    # """Creates an Article object.

    # Args:
      # file: The path to either a Django file, or a localized template.
    # """
    # if original_file.startswith(Article.DJANGO_ROOT):
      # # We've been given a Django file, s
      # self.original_type_ = Article.DJANGO
    # elif original_file.startswith(Article.LOCALIZED_ROOT):
      # self.original_type_ = Article.LOCALIZED

  # def GetUnlocalizedPath(self, django_path):
    # """Given the path to a Django template, returns the path to a corresponding
       # unlocalized file.

    # Args:
      # django_file: The path to a Django template.
    # """
    # temp = re.sub(r'^%s/' % Article.DJANGO_ROOT, '', django_path)
    # temp = re.sub(r'/', Article.PATH_DELIMITER, temp)
    # return os.path.abspath(os.path.join(Article.UNLOCALIZED_ROOT, temp))

  # def GetLocalizedPath(self, locale, html_path):
    # """Given the path to a localized HTML file, returns the path to a
       # corresponding Django file.

    # Args"""

  # def GenerateHTML(self):
    # """Generates a localizable HTML file from a Django template.

    # This function will also create the HTML file's directory if it doesn't
    # already exist.
    # """
    # try:
      # os.makedirs(os.path.dirname(self.html_))
    # except os.error:
      # pass
    # print '* Generating `%s`' % self.html_
    # with open(self.html_, 'w') as outfile:
      # with open(self.django_, 'r') as infile:
        # in_content = False
        # for line in infile:
          # (line, in_content) = self._HtmlizeLine(line, in_content)
          # outfile.write(line)

  # def _HtmlizeLine(self, line, in_content):
    # """Given a line of a Django template, returns the corresponding HTML line

    # * Replaces Django tags with comments in the form:
        # <!--DO_NOT_TRANSLATE_BLOCK-->{DJANGO_TAG}<!--/DO_NOT_TRANSLATE_BLOCK-->

    # * Replaces script/style/pre tags with comments in the form:
        # <TAG_GOES_HERE><!--DO_NOT_TRANSLATE_BLOCK-->
        # ...
        # <!--/DO_NOT_TRANSLATE_BLOCK--></TAG_GOES_HERE>
    # """

    # UNESCAPED_DJANGO = r'(?P<tag>{%.+?%})'
    # ESCAPED_DJANGO = r'%s\g<tag>%s' % (Article.UNTRANSLATABLE_LABEL,
                                       # Article.UNTRANSLATABLE_END_LABEL,)

    # UNESCAPED_UNTRANSLATABLE = r'(?P<tag><(?:pre|script|style)[^>]*?>)'
    # ESCAPED_UNTRANSLATABLE = r'\g<tag>%s' % Article.UNTRANSLATABLE_LABEL

    # UNESCAPED_UNTRANSLATABLE_END = r'(?P<tag></(?:pre|script|style)[^>]*?>)'
    # ESCAPED_UNTRANSLATABLE_END = r'%s\g<tag>' % Article.UNTRANSLATABLE_END_LABEL

    # UNESCAPED_CONTENT = r'{% block content %}'
    # UNESCAPED_CONTENT_END = r'{% endblock %}'

    # # Preprocess Django tags
    # line = re.sub(UNESCAPED_DJANGO, ESCAPED_DJANGO, line)
    # # Preprocess script/pre/style blocks
    # line = re.sub(UNESCAPED_UNTRANSLATABLE, ESCAPED_UNTRANSLATABLE, line)
    # line = re.sub(UNESCAPED_UNTRANSLATABLE_END,
                  # ESCAPED_UNTRANSLATABLE_END,
                  # line)
    # # Preprocess content block
    # if not in_content and re.search(UNESCAPED_CONTENT, line):
      # line = Article.CONTENT_LABEL
      # in_content = True
    # if in_content and re.search(UNESCAPED_CONTENT_END, line):
      # line = Article.CONTENT_LABEL_END
      # in_content = False
    # return (line, in_content)

  # def GenerateDjango(self):
    # """Generates a Django template from a localized HTML file.

    # Implemented trivially by stripping comments in the form:
    # `<!--DJANGO>...</DJANGO-->`. This function will also create the Django
    # template's directory if it doesn't already exist.
    # """
    # try:
      # os.makedirs(os.path.dirname(self.django_))
    # except os.error:
      # pass
    # with open(self.html_, 'r') as infile:
      # with open(self.django_, 'w') as outfile:
        # for line in infile:
          # # Preprocess Django tags
          # line = re.sub(Article.ESCAPED_DJANGO, Article.UNESCAPED_DJANGO, line)
          # # Preprocess script blocks
          # line = line.replace(Article.ESCAPED_SCRIPT, Article.UNESCAPED_SCRIPT)
          # line = line.replace(Article.ESCAPED_SCRIPT_END,
                              # Article.UNESCAPED_SCRIPT_END)
          # # Preprocess style blocks
          # line = line.replace(Article.ESCAPED_STYLE, Article.UNESCAPED_STYLE)
          # line = line.replace(Article.ESCAPED_STYLE_END,
                              # Article.UNESCAPED_STYLE_END)
          # outfile.write(line)


  # def __str__(self):
    # """String representation of an Article."""

    # return ('Article:\n'
            # '- HTML Path:   `%s`\n'
            # '- Django Path: `%s`\n') % (self.html_, self.django_)


# class Localizer(object):
  # """Implements the HTML5Rocks article localization workflow.

  # Given a root directory, Localizer looks for article files (defined as pretty
  # much anything living directly under an `en` directory (which is very fragile
  # and assumes we'll never have articles written first in languages other than
  # English (which is probably accurate, but not something we should hard-code)))
  # and converts the Django templates into HTML files that can be
  # passed into a translation system (by commenting out all the Django bits).

  # Localizer also goes in the other direction, converting localized HTML files
  # into Django-template counterparts that can be rendered as part of HTML5Rocks.

  # Attributes:
    # root_: The root directory from which Localizer scans
    # articles_: A list of Article objects found during a scan.
  # """

  # def __init__(self, root):
    # """Constructs a Localizer object.

    # Args:
      # root: The root directory from which Localizer should scan.
    # """
    # self.root_ = root
    # self.articles_ = []

  # def IndexEnglishArticles(self):
    # """Scans the root directory for English articles.

    # Populates `self.articles_` with a list of Article objects representing
    # each.

    # Returns:
        # list of Article objects
    # """
    # self.articles_ = []
    # for root, _, files in os.walk(Article.DJANGO_ROOT):
      # for name in files:
        # if not name == '.DS_Store' and re.search(r'\/en$', root):
          # self.articles_.append(Article(django=os.path.join(root,
                                                            # name)))
    # return self.articles_

  # def Htmlize(self):
    # """Generates localizable HTML from Django templates."""

    # print ('Generating Localizable HTML\n'
           # '===========================\n')
    # for article in self.articles_:
      # article.GenerateHTML()

  # def Djangoize(self):
    # """Generates Django templates from localized HTML."""

    # # TODO(mkwst): I should implement this function. :)
    # print 'Not finished (read: started) yet. Come back later.'


# def main():
  # parser = optparse.OptionParser()
  # parser.add_option('--generate_html', dest='generate_html',
                    # default=False, action='store_true',
                    # help='Generate HTML from Django templated articles.')
  # parser.add_option('--generate_django', dest='generate_django',
                    # default=False, action='store_true',
                    # help=('Generate Django templates from localized '
                          # 'HTML articles.'))

  # options = parser.parse_args()[0]
  # if not options.generate_html or options.generate_django:
    # parser.error('You must specify either `--generate_html`'
                 # 'or `--generate_django`.')

  # l10n = Localizer(Article.DJANGO_ROOT)
  # if options.generate_html:
    # l10n.IndexEnglishArticles()
    # l10n.Htmlize()
  # if options.generate_django:
    # l10n.Djangoize()

if __name__ == '__main__':
  main()
