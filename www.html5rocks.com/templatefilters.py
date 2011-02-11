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
import common

register = webapp.template.create_template_register()

class TOCNode(django.template.Node):
  def render(self, context):
    if not context.has_key('toc'):
      return ''
    toc = context['toc']
    output = ''
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
    self.profiles = common.get_profiles()

  def render(self, context):
    names = []
    for id in self.ids:
      if id in self.profiles:
        profile = self.profiles[id]
        names.append("<a href='/profiles/#!/%(id)s'>%(given)s %(family)s</a> - %(role)s, %(company)s" %
            {'id': profile['id'], 'given': profile['name']['given'],
             'family': profile['name']['family'], 'role': profile['org']['unit'],
             'company': profile['org']['name']})
    return ',<br> '.join(names)


def do_profile_links(parser, token):
  ids = token.split_contents()
  ids.pop(0)  # Remove tag name.
  return ProfileLink(ids)

register.tag('profilelinks', do_profile_links)


class ProfileLinkSimple(ProfileLink):
  def __init__(self, ids):
    ProfileLink.__init__(self, ids)

  def render(self, context):
    names = []
    for id in self.ids:
      if id in self.profiles:
        profile = self.profiles[id]
        names.append("<a href='/profiles/#!/%(id)s' data-id='%(id)s'>%(given)s %(family)s</a>" %
            {'id': profile['id'],
             'given': profile['name']['given'],
             'family': profile['name']['family']})
    return ', '.join(names)


def do_simple_profile_link(parser, token):
  ids = token.split_contents()
  ids.pop(0)  # Remove tag name.
  return ProfileLinkSimple(ids)

register.tag('simpleprofilelink', do_simple_profile_link)
