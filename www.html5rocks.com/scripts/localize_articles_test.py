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

import unittest
import os
from localize_articles import TextProcessor

class TestTextProcessor(unittest.TestCase):
  def setUp(self):
    self._proc = TextProcessor()

  def test_identity(self):
    text = 'Test.'
    self.assertEqual(text, self._proc.django_to_html(text))

  def test_tag(self):
    text = '{% tag %}'
    expected = r'%s{%% tag %%}%s' % (TextProcessor.UNTRANSLATABLE_BEGIN,
                                     TextProcessor.UNTRANSLATABLE_END)
    self.assertEqual(expected, self._proc.django_to_html(text))
    self.assertEqual(text, self._proc.html_to_django(expected))

  def test_tags(self):
    text = '{% tag1 %}{% tag2 %}'
    expected = '{0}{{% tag1 %}}{1}{0}{{% tag2 %}}{1}'.format(
        TextProcessor.UNTRANSLATABLE_BEGIN,
        TextProcessor.UNTRANSLATABLE_END)
    self.assertEqual(expected, self._proc.django_to_html(text))
    self.assertEqual(text, self._proc.html_to_django(expected))

  def test_content(self):
    text = '{% block content %}'
    expected = TextProcessor.CONTENT_BEGIN
    self.assertEqual(expected, self._proc.django_to_html(text))
    self.assertEqual(text, self._proc.html_to_django(expected))

  def test_content_end(self):
    text = '{% block content %}\n{% endblock %}'
    expected = '%s%s' % (TextProcessor.CONTENT_BEGIN,
                         TextProcessor.CONTENT_END)
    self.assertEqual(expected, self._proc.django_to_html(text))
    self.assertEqual(text, self._proc.html_to_django(expected))

  def test_endblock_outside_content(self):
    text = '{% endblock %}'
    expected = r'%s{%% endblock %%}%s' % (TextProcessor.UNTRANSLATABLE_BEGIN,
                                          TextProcessor.UNTRANSLATABLE_END)
    self.assertEqual(expected, self._proc.django_to_html(text))
    self.assertEqual(text, self._proc.html_to_django(expected))

  def test_untranslated_tags(self):
    text = '<pre>'
    expected = '<pre>%s' % TextProcessor.UNTRANSLATABLE_BEGIN
    self.assertEqual(expected, self._proc.django_to_html(text))
    self.assertEqual(text, self._proc.html_to_django(expected))
    text = '<script>'
    expected = '<script>%s' % TextProcessor.UNTRANSLATABLE_BEGIN
    self.assertEqual(expected, self._proc.django_to_html(text))
    self.assertEqual(text, self._proc.html_to_django(expected))
    text = '<style>'
    expected = '<style>%s' % TextProcessor.UNTRANSLATABLE_BEGIN
    self.assertEqual(expected, self._proc.django_to_html(text))
    self.assertEqual(text, self._proc.html_to_django(expected))

  def test_untranslated_tags_end(self):
    text = '</pre>'
    expected = '%s</pre>' % TextProcessor.UNTRANSLATABLE_END
    self.assertEqual(expected, self._proc.django_to_html(text))
    self.assertEqual(text, self._proc.html_to_django(expected))
    text = '</script>'
    expected = '%s</script>' % TextProcessor.UNTRANSLATABLE_END
    self.assertEqual(expected, self._proc.django_to_html(text))
    self.assertEqual(text, self._proc.html_to_django(expected))
    text = '</style>'
    expected = '%s</style>' % TextProcessor.UNTRANSLATABLE_END
    self.assertEqual(expected, self._proc.django_to_html(text))
    self.assertEqual(text, self._proc.html_to_django(expected))

if __name__ == '__main__':
    unittest.main()
