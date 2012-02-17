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

import os
import tempfile
import unittest

from localize_articles import TextProcessor, Article, Localizer

TEST_ROOT = os.path.abspath(os.path.dirname(__file__))

class TestTextProcessor(unittest.TestCase):
  def test_identity(self):
    text = 'Test.'
    self.assertEqual(text, TextProcessor.django_to_html(text))

  def test_tag(self):
    text = '{% tag %}'
    expected = r'%s{%% tag %%}%s' % (TextProcessor.UNTRANSLATABLE_BEGIN,
                                     TextProcessor.UNTRANSLATABLE_END)
    self.assertEqual(expected, TextProcessor.django_to_html(text))
    self.assertEqual(text, TextProcessor.html_to_django(expected))

  def test_tags(self):
    text = '{% tag1 %}{% tag2 %}'
    expected = '{0}{{% tag1 %}}{1}{0}{{% tag2 %}}{1}'.format(
        TextProcessor.UNTRANSLATABLE_BEGIN,
        TextProcessor.UNTRANSLATABLE_END)
    self.assertEqual(expected, TextProcessor.django_to_html(text))
    self.assertEqual(text, TextProcessor.html_to_django(expected))

  def test_content(self):
    text = '{% block content %}'
    expected = TextProcessor.CONTENT_BEGIN
    self.assertEqual(expected, TextProcessor.django_to_html(text))
    self.assertEqual(text, TextProcessor.html_to_django(expected))

  def test_content_end(self):
    text = '{% block content %}\n{% endblock %}'
    expected = '%s%s' % (TextProcessor.CONTENT_BEGIN,
                         TextProcessor.CONTENT_END)
    self.assertEqual(expected, TextProcessor.django_to_html(text))
    self.assertEqual(text, TextProcessor.html_to_django(expected))

  def test_endblock_outside_content(self):
    text = '{% endblock %}'
    expected = r'%s{%% endblock %%}%s' % (TextProcessor.UNTRANSLATABLE_BEGIN,
                                          TextProcessor.UNTRANSLATABLE_END)
    self.assertEqual(expected, TextProcessor.django_to_html(text))
    self.assertEqual(text, TextProcessor.html_to_django(expected))

  def test_untranslated_tags(self):
    text = '<pre>'
    expected = '<pre>%s' % TextProcessor.UNTRANSLATABLE_BEGIN
    self.assertEqual(expected, TextProcessor.django_to_html(text))
    self.assertEqual(text, TextProcessor.html_to_django(expected))
    text = '<script>'
    expected = '<script>%s' % TextProcessor.UNTRANSLATABLE_BEGIN
    self.assertEqual(expected, TextProcessor.django_to_html(text))
    self.assertEqual(text, TextProcessor.html_to_django(expected))
    text = '<style>'
    expected = '<style>%s' % TextProcessor.UNTRANSLATABLE_BEGIN
    self.assertEqual(expected, TextProcessor.django_to_html(text))
    self.assertEqual(text, TextProcessor.html_to_django(expected))

  def test_untranslated_tags_end(self):
    text = '</pre>'
    expected = '%s</pre>' % TextProcessor.UNTRANSLATABLE_END
    self.assertEqual(expected, TextProcessor.django_to_html(text))
    self.assertEqual(text, TextProcessor.html_to_django(expected))
    text = '</script>'
    expected = '%s</script>' % TextProcessor.UNTRANSLATABLE_END
    self.assertEqual(expected, TextProcessor.django_to_html(text))
    self.assertEqual(text, TextProcessor.html_to_django(expected))
    text = '</style>'
    expected = '%s</style>' % TextProcessor.UNTRANSLATABLE_END
    self.assertEqual(expected, TextProcessor.django_to_html(text))
    self.assertEqual(text, TextProcessor.html_to_django(expected))

class TestArticleLocales(unittest.TestCase):
  ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

  def test_article_locales_none(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales_none'))
    self.assertEqual([], temp.locales)

  def test_article_locales_files(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales_files'))
    self.assertEqual([], temp.locales)

  def test_article_locales_single(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales_single'))
    self.assertEqual(['en'], temp.locales)

  def test_article_locales_multiple(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales_multiple'))
    self.assertEqual(['de', 'en', 'es'], temp.locales)

  def test_article_locales_multiple_no_index(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_locales_multiple_no_index'))
    self.assertEqual(['de', 'es'], temp.locales)

class TestArticlePaths(unittest.TestCase):
  ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

  def setUp(self):
    # A little bit of monkey patching never hurt nobody.
    Article.ROOT = TEST_ROOT

  def test_article_path(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures', 'article_path'))
    expected = os.path.join(Article.UNLOCALIZED_ROOT,
                            Article.PATH_DELIMITER.join(
                                ['test_fixtures', 'article_path']))
    self.assertEqual(expected, temp.localizable_file_path)

  def test_article_multiple(self):
    temp = Article(os.path.join(TEST_ROOT, 'test_fixtures',
                                'article_path_multiple', 'path1', 'path2'))
    expected = os.path.join(Article.UNLOCALIZED_ROOT,
                            Article.PATH_DELIMITER.join(
                                ['test_fixtures', 'article_path_multiple',
                                 'path1', 'path2']))
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
                                'article_locales_single'))
    self._created_file = temp.generate_localizable_file()
    self.assertEqual(temp.localizable_file_path, self._created_file)
    self.assertTrue(os.path.exists(temp.localizable_file_path))
    self.assertTrue(os.path.isfile(temp.localizable_file_path))

class TestLocalizerIndex(unittest.TestCase):
  def test_simple(self):
    l7r = Localizer(original_root=os.path.join(TEST_ROOT, 'test_fixtures',
                                               'localizer_simple'))
    self.assertEqual(3, len(l7r.original_articles))
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_simple', 'article1'),
                     l7r.original_articles[0].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_simple', 'article2'),
                     l7r.original_articles[1].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_simple', 'article3'),
                     l7r.original_articles[2].path)

  def test_deeper(self):
    l7r = Localizer(original_root=os.path.join(TEST_ROOT, 'test_fixtures',
                                               'localizer_deeper'))
    self.assertEqual(6, len(l7r.original_articles))
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path1', 'path2',
                                  'article1'),
                     l7r.original_articles[0].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path1', 'path2',
                                  'article2'),
                     l7r.original_articles[1].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path1', 'path2',
                                  'article3'),
                     l7r.original_articles[2].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path3', 'path4',
                                  'article4'),
                     l7r.original_articles[3].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path3', 'path4',
                                  'article5'),
                     l7r.original_articles[4].path)
    self.assertEqual(os.path.join(TEST_ROOT, 'test_fixtures',
                                  'localizer_deeper', 'path3', 'path4',
                                  'article6'),
                     l7r.original_articles[5].path)

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
    for article in l7r.original_articles:
      self._created_files.append(article.localizable_file_path)
      self.assertTrue(os.path.exists(article.localizable_file_path))
      self.assertTrue(os.path.isfile(article.localizable_file_path))

if __name__ == '__main__':
  unittest.main()
