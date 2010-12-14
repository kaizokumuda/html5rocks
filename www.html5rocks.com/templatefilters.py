# Copyright 2010 Google Inc.
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
import django
import django.template
from common import load_profiles

register = webapp.template.create_template_register()

class TOCNode(django.template.Node):
  def render(self, context):
    if not context.has_key('toc'):
      return ""
    toc = context['toc']
    output = ""
    level = 0
    for entry in toc:
      if entry['level'] > level:
        output += "<ul>"
      elif entry['level'] < level:
        output += "</ul></li>" * (level - entry['level'])
      else:
        output += "</li>"
      level = entry['level']
      output += "<li><a href='#%s'>%s</a>" % (entry['id'], entry['text'])
    
    output += "</li></ul>" * level
    return output

def do_toc(parser, token):
  return TOCNode()

register.tag('toc', do_toc)

class ProfileLink(django.template.Node):
  def __init__(self, ids):
    self.ids = ids
    self.profiles = load_profiles()
  def render(self, context):
    names = []
    for id in self.ids:
      profile = self.profiles[id]
      names.append("<a href='/profiles#%(id)s'>%(name)s</a>" % {"id": profile["id"], "name": profile["name"]["given"] + " " + profile["name"]["family"] })
    return ', '.join(names)

def do_profile_links(parser, token):
  ids = token.split_contents()
  ids.pop(0) # remove tag name
  return ProfileLink(ids)

register.tag("profilelinks", do_profile_links)
