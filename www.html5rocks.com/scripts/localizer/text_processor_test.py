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

__author__ = ('mkwst@google.com (Mike West)')

"""Unit Tests for the article l10n script."""

import os
import tempfile
import unittest

from text_processor import TextProcessor
from text_processor import CONTENT_BEGIN
from text_processor import CONTENT_END
from text_processor import UNTRANSLATABLE_BEGIN
from text_processor import UNTRANSLATABLE_END

TEST_ROOT = os.path.abspath(os.path.dirname(__file__))

class TestTextProcessor(unittest.TestCase):
  def assertHtmlDjango(self, html, django):
    from_html = TextProcessor(html=html)
    from_django = TextProcessor(django=django)
    self.assertEqual(html, from_django.html)
    self.assertEqual(django, from_html.django)

  def test_identity(self):
    text = 'Test.'
    self.assertHtmlDjango(text, text)

  def test_tag(self):
    django = '{% tag %}'
    html = r'%s{%% tag %%}%s' % (UNTRANSLATABLE_BEGIN,
                                 UNTRANSLATABLE_END)
    self.assertHtmlDjango(html, django)

  def test_tags(self):
    django = '{% tag1 %}{% tag2 %}'
    html = '{0}{{% tag1 %}}{1}{0}{{% tag2 %}}{1}'.format(
        UNTRANSLATABLE_BEGIN,
        UNTRANSLATABLE_END)
    self.assertHtmlDjango(html, django)

  def test_content(self):
    django = '{% block content %}'
    html = CONTENT_BEGIN
    self.assertHtmlDjango(html, django)

  def test_content_end(self):
    django = '{% block content %}\n{% endblock %}'
    html = '%s%s' % (CONTENT_BEGIN,
                     CONTENT_END)
    self.assertHtmlDjango(html, django)

  def test_endblock_outside_content(self):
    django = '{% endblock %}'
    html = r'%s{%% endblock %%}%s' % (UNTRANSLATABLE_BEGIN,
                                      UNTRANSLATABLE_END)
    self.assertHtmlDjango(html, django)

  def test_untranslated_tags(self):
    django = '<pre>'
    html = '<pre>%s' % UNTRANSLATABLE_BEGIN
    self.assertHtmlDjango(html, django)
    django = '<script>'
    html = '<script>%s' % UNTRANSLATABLE_BEGIN
    self.assertHtmlDjango(html, django)
    django = '<style>'
    html = '<style>%s' % UNTRANSLATABLE_BEGIN
    self.assertHtmlDjango(html, django)

  def test_untranslated_tags_end(self):
    django = '</pre>'
    html = '%s</pre>' % UNTRANSLATABLE_END
    self.assertHtmlDjango(html, django)
    django = '</script>'
    html = '%s</script>' % UNTRANSLATABLE_END
    self.assertHtmlDjango(html, django)
    django = '</style>'
    html = '%s</style>' % UNTRANSLATABLE_END
    self.assertHtmlDjango(html, django)


if __name__ == '__main__':
  unittest.main()
