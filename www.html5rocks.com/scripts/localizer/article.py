#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
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

__author__ = ('mkwst@google.com (Mike West)')

import codecs
import glob
import os

from text_processor import TextProcessor

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REQUIRED_LOCALES = ['de', 'en', 'es', 'ja', 'pt', 'ru', 'zh']


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
    available_localizations: The finished localizations available for this
        article (e.g. ['en', 'de', 'es'])
    completely_localized: Does the article have localizations for each of the
        expected language?
    locales: The article's completed localizations. (e.g. ['en', 'de'])
    localizable_file_path: The path to the article's localizable
        representation, living under `{Article.UNLOCALIZED_ROOT}`.
    new_localizations: Are new localizations available for this article?
    path: The path to the article's root: `{Article.ROOT}/path/to/article`.
  """

  ROOT = os.path.abspath(os.path.join(ROOT_DIR, 'content'))
  LOCALIZED_ROOT = os.path.abspath(os.path.join(ROOT_DIR, '_localized'))
  UNLOCALIZED_ROOT = os.path.abspath(os.path.join(ROOT_DIR, '_unlocalized'))
  PATH_DELIMITER = '___===___'

  def __init__(self, path):
    if not os.path.exists(path):
      raise ArticleException('`%s` does not exist.' % path)
    self.path = path
    self._locales = None
    self._available_localizations = None

  @property
  def locales(self):
    """Returns the article's localizations.

    We assume that each of the subdirectories under |path| that contain an
    `index.html` file are localizations. This getter scans the filesystem
    to generate that list, then caches it for future calls.

    Returns:
      A list of locales, e.g. ['de','en','es']
    """
    if not self._locales:
      self._locales = [directory
                       for directory in os.listdir(self.path)
                       if os.path.exists(os.path.join(self.path, directory,
                                                      'index.html'))]
    return self._locales

  @property
  def completely_localized(self):
    """Does the article have localizations for each expected language?

    Returns:
      True if the article has a localization for each of REQUIRED_LOCALES.
    """
    remaining = [locale
                 for locale in REQUIRED_LOCALES
                 if locale not in self.locales]
    return not remaining

  @property
  def localizable_file_path(self):
    """The path to an article's localizable representation.

    Unlocalized articles live under `{Article.UNLOCALIZED_ROOT}`, and are named
    by jamming the elements of the article's path together into one reversable
    string (the localization system doesn't like subdirectories).

    `{Article.ROOT}/path/to/article` would return
    `{Article.UNLOCALIZED_ROOT}/path__to__article.html` (where `__` represents
    `Article.PATH_DELIMITER`).

    Returns:
      An absolute path to the article's localizable representation.
    """
    temp = self.path
    if temp.startswith(self.ROOT):
      temp = temp.replace(r'%s/' % self.ROOT, '', 1)
    temp = temp.replace(r'/', self.PATH_DELIMITER)
    temp = '%s.html' % temp
    return os.path.abspath(os.path.join(self.UNLOCALIZED_ROOT, temp))

  def _index_available_localizations(self):
    """Populates a list of available localizations for this article.

    Indexes all files whose paths match
    `{Article.LOCALIZED_ROOT}/[locale]/path__to__article.html` (where `__`
    represents `Article.PATH_DELIMITER`), and stores them in
    self._available_localizations.

    Some articles have "static" directories that are used for all
    localizations. These are not counted as available localizations.
    """
    self._available_localizations = []
    matches = glob.glob(os.path.join(self.LOCALIZED_ROOT, '*',
                                     os.path.basename(
                                         self.localizable_file_path)))
    for match in matches:
      if match != "static":
        # The locale is the name of the directory in which the localized file
        # sits. `/path/to/article/en/article__is__here.html` has a locale of
        # "en". "static" is special-cased out.
        self._available_localizations.append(os.path.basename(os.path.dirname(
                                                                  match)))

  @property
  def available_localizations(self):
    """The finshed localizations available for this article.

    Returns:
      A list of locales, e.g. ['en', 'de', 'es']
    """
    if self._available_localizations is None:
      self._index_available_localizations()
    return self._available_localizations

  @property
  def new_localizations(self):
    """Determines whether a new localization for this article exists.

    This getter checks whether a file exists in `Article.LOCALIZED_ROOT` that
    matches this article in a locale that isn't already available.

    Returns:
      A list of new localizations available, e.g. ['de', 'es'].
    """
    return [locale
            for locale in self.available_localizations
            if locale not in self.locales]

  def original_file_path(self, locale):
    """Returns the path for a specific original file.

    This method just generates a path: it doesn't check that the file exists
    or that it's valid.

    Returns:
      The path to a potential original file.
    """
    return os.path.join(self.ROOT, self.path, locale, 'index.html')

  def localized_file_path(self, locale):
    """Returns the path for a specific localized file.

    This method just generates a path: it doesn't check that the file exists
    or that it's valid.

    Returns:
      The path to a potential localized file.
    """
    return os.path.join(self.LOCALIZED_ROOT, locale,
                        os.path.basename(self.localizable_file_path))

  def generate_localizable_file(self):
    """Generates a localizable representation of the article.

    This method grabs the English version of the article, runs the text through
    `TextProcessor`, and writes the result to `localizableFilePath`.

    Returns:
      An absolute path to the article's localizable representation.

    Raises:
      ArticleException: If no English version of an article is available.
    """
    if not 'en' in self.locales:
      error = """
ArticleException:
- path: %s
- locales: %s
- No English edition found.
"""
      raise ArticleException(error % (self.path, self.locales))

    original = self.original_file_path('en')
    with codecs.open(original, 'r', 'UTF-8') as infile:
      with codecs.open(self.localizable_file_path, 'w', 'UTF-8') as output:
        temp = TextProcessor(django=infile.read())
        output.write(temp.html)
    return self.localizable_file_path

  def import_localized_files(self):
    """If new localized files are available, import them.

    This method sifts through the available localized files, and imports each
    to the correct location under CONTENT_ROOT.
    """
    for locale in self.new_localizations:
      if os.path.isfile(self.localized_file_path(locale)):
        try:
          os.mkdir(os.path.dirname(self.original_file_path(locale)))
        except OSError:
          pass
        in_path = self.localized_file_path(locale)
        out_path = self.original_file_path(locale)
        with codecs.open(in_path, 'r', 'UTF-8') as infile:
          with codecs.open(out_path, 'w', 'UTF-8') as outfile:
            temp = TextProcessor(html=infile.read())
            outfile.write(temp.django)
    self._available_localizations = []
    self._locales = []
