# Copyright 2012 Google Inc.
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


import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import django.template

register = webapp.template.create_template_register()

GlobalSocialURL = ''

@register.tag
def social_url(parser, token):
  try:
    _, url = token.split_contents()
  except ValueError:
    url = '""'
  return SocialUrlNode(url[1:-1])


class SocialUrlNode(django.template.Node):
  def __init__(self, url):
    global GlobalSocialURL
    if url:
      GlobalSocialURL = url

  def render(self, context):
    return GlobalSocialURL if GlobalSocialURL else context['disqus_url']
