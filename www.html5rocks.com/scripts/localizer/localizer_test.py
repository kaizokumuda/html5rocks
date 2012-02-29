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

from localizer import Localizer
from article import Article

TEST_ROOT = os.path.abspath(os.path.dirname(__file__))

class TestLocalizerIndex(unittest.TestCase):
  def test_simple(self):
    l7r = Localizer(original_root=os.path.join(TEST_ROOT, 'test_fixtures',
                                               'localizer_simple'))
    self.assertEqual(3, len(l7r.articles))
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_simple', 'article1'),
                     l7r.articles[0].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_simple', 'article2'),
                     l7r.articles[1].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_simple', 'article3'),
                     l7r.articles[2].path)

  def test_deeper(self):
    l7r = Localizer(original_root=os.path.join(TEST_ROOT, 'test_fixtures',
                                               'localizer_deeper'))
    self.assertEqual(6, len(l7r.articles))
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path1', 'path2',
                                  'article1'),
                     l7r.articles[0].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path1', 'path2',
                                  'article2'),
                     l7r.articles[1].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path1', 'path2',
                                  'article3'),
                     l7r.articles[2].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path3', 'path4',
                                  'article4'),
                     l7r.articles[3].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path3', 'path4',
                                  'article5'),
                     l7r.articles[4].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path3', 'path4',
                                  'article6'),
                     l7r.articles[5].path)

class TestLocalizerLocalizableFileGeneration(unittest.TestCase):
  def setUp(self):
    # A little bit of monkey patching never hurt nobody.
    Article.ROOT = TEST_ROOT
    Article.UNLOCALIZED_ROOT = tempfile.mkdtemp(prefix='Unlocalized_')
    self._created_files = []

  def tearDown(self):
    for file in self._created_files:
      os.remove(file)
    os.removedirs(Article.UNLOCALIZED_ROOT)

  def test_simple(self):
    l7r = Localizer(original_root=os.path.join(TEST_ROOT, 'test_fixtures',
                                               'localizer_simple'))
    l7r.generate_localizable_files()
    for article in l7r.articles:
      self._created_files.append(article.localizable_file_path)
      self.assertTrue(os.path.exists(article.localizable_file_path))
      self.assertTrue(os.path.isfile(article.localizable_file_path))


if __name__ == '__main__':
  unittest.main()
