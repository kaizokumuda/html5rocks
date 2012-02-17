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
import shutil
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

class Integration(unittest.TestCase):
  def setUp(self):
    self.TEMP_ROOT = tempfile.mkdtemp(prefix='Integration_')
    Article.ROOT = os.path.join(self.TEMP_ROOT, 'article_root')
    Article.UNLOCALIZED_ROOT = os.path.join(self.TEMP_ROOT, 'unlocalized_root')
    Article.LOCALIZED_ROOT = os.path.join(self.TEMP_ROOT, 'localized_root')
    os.mkdir(Article.UNLOCALIZED_ROOT)
    os.mkdir(Article.LOCALIZED_ROOT)
    # Populate a single article.
    article_dir = os.path.join(Article.ROOT, 'article1', 'en')
    os.makedirs(article_dir)
    with open(os.path.join(article_dir, 'index.html'), 'w') as f:
      f.write("{% tag %}Example")

  def tearDown(self):
    shutil.rmtree(self.TEMP_ROOT)

  def test_new_localization_workflow(self):
    # Write a new localization.
    article_dir = os.path.join(Article.LOCALIZED_ROOT, 'de')
    os.makedirs(article_dir)
    with open(os.path.join(article_dir, 'article1.html'), 'w') as f:
      text = r'%s{%% tag %%}%sBeispiel' % (TextProcessor.UNTRANSLATABLE_BEGIN,
                                           TextProcessor.UNTRANSLATABLE_END)
      f.write(text)

    l7r = Localizer(original_root=Article.ROOT,
                    localized_root=Article.LOCALIZED_ROOT)

    self.assertEqual(1, len(l7r.articles))
    
    # Test writing localizable HTML
    l7r.generate_localizable_files()
    self.assertTrue(os.path.exists(l7r.articles[0].localizable_file_path))
    self.assertTrue(os.path.isfile(l7r.articles[0].localizable_file_path))
    
    # Test importataion.
    l7r.import_localized_files()
    self.assertEqual([], l7r.articles[0].new_localizations)
    self.assertTrue(os.path.exists(l7r.articles[0].original_file_path('en')))
    self.assertTrue(os.path.isfile(l7r.articles[0].original_file_path('en')))
    self.assertTrue(os.path.exists(l7r.articles[0].original_file_path('de')))
    self.assertTrue(os.path.isfile(l7r.articles[0].original_file_path('de')))

    # Verify contents
    with open(l7r.articles[0].original_file_path('de'), 'r') as infile:
      contents = infile.read()
      self.assertEqual("{% tag %}Beispiel", contents)

if __name__ == '__main__':
  unittest.main()
