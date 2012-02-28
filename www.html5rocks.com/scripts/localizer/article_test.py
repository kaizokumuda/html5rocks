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

"""Unit Tests for the article l10n script."""

__author__ = ('mkwst@google.com (Mike West)')

import os
import tempfile
import unittest

from article import Article
from article import ArticleException

TEST_ROOT = os.path.abspath(os.path.dirname(__file__))

class TestArticleLocales(unittest.TestCase):
  ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

  def test_article_locales_none(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales', 'none'))
    self.assertEqual([], temp.locales)

  def test_article_locales_files(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales', 'files'))
    self.assertEqual([], temp.locales)

  def test_article_locales_single(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales', 'single'))
    self.assertEqual(['en'], temp.locales)

  def test_article_locales_static(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales', 'single'))
    self.assertEqual(['en'], temp.locales)

  def test_article_locales_multiple(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales', 'multiple'))
    self.assertEqual(['de', 'en', 'es'], temp.locales)

  def test_article_locales_multiple_no_index(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales', 'multiple_no_index'))
    self.assertEqual(['de', 'es'], temp.locales)

class TestArticlePaths(unittest.TestCase):
  ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

  def setUp(self):
    # A little bit of monkey patching never hurt nobody.
    Article.ROOT = TEST_ROOT

  def test_nonexistent_path(self):
    path = os.path.join(TEST_ROOT, 'test_fixtures', 'article_path',
                        'does_not_exist')
    self.assertRaises(ArticleException, Article, path)

  def test_article_path(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures', 'article_path'))
    expected = os.path.join(Article.UNLOCALIZED_ROOT,
                            Article.PATH_DELIMITER.join(
                                ['test_fixtures', 'article_path']))
    expected = '%s.html' % expected
    self.assertEqual(expected, temp.localizable_file_path)

  def test_article_multiple(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_path_multiple', 'path1', 'path2'))
    expected = os.path.join(Article.UNLOCALIZED_ROOT,
                            Article.PATH_DELIMITER.join(
                                ['test_fixtures', 'article_path_multiple',
                                 'path1', 'path2']))
    expected = '%s.html' % expected
    self.assertEqual(expected, temp.localizable_file_path)


class TestArticleUnlocalizedGeneration(unittest.TestCase):
  def setUp(self):
    # A little bit of monkey patching never hurt nobody.
    Article.ROOT = TEST_ROOT
    Article.UNLOCALIZED_ROOT = tempfile.mkdtemp(prefix='Unlocalized_')
    self._created_file = None

  def tearDown(self):
    if self._created_file:
      os.remove(self._created_file)
    os.removedirs(Article.UNLOCALIZED_ROOT)

  def test_simple(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales', 'single'))
    self._created_file = temp.generate_localizable_file()
    self.assertEqual(temp.localizable_file_path, self._created_file)
    self.assertTrue(os.path.exists(temp.localizable_file_path))
    self.assertTrue(os.path.isfile(temp.localizable_file_path))

class TestArticleLocalizedFiles(unittest.TestCase):
  def setUp(self):
    # A little bit of monkey patching never hurt nobody.
    Article.ROOT = os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_localizations', 'article_root')
    Article.LOCALIZED_ROOT = os.path.join(Article.ROOT, '..', 'localized_root')

  def test_available_localizations_none(self):
    temp = Article(os.path.join(Article.ROOT, 'none'))
    self.assertEqual([], temp.available_localizations)
    self.assertEqual([], temp.new_localizations)

  def test_available_localizations_static(self):
    temp = Article(os.path.join(Article.ROOT, 'none'))
    self.assertEqual([], temp.available_localizations)
    self.assertEqual([], temp.new_localizations)

  def test_available_localizations_only_english(self):
    temp = Article(os.path.join(Article.ROOT, 'only_english'))
    self.assertEqual(['en'], temp.available_localizations)
    self.assertEqual([], temp.new_localizations)

  def test_available_localizations_one_new(self):
    temp = Article(os.path.join(Article.ROOT, 'one_new'))
    self.assertEqual(['de', 'en'], temp.available_localizations)
    self.assertEqual(['de'], temp.new_localizations)


if __name__ == '__main__':
  unittest.main()
