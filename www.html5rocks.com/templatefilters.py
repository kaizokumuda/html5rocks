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
        output += "</ul></li>"
      else:
        output += "</li>"
      level = entry['level']
      output += "<li><a href='#%s'>%s</a>" % (entry['id'], entry['text'])
    
    output += "</li></ul>" * level
    return output

def do_toc(parser, token):
  return TOCNode()

register.tag('toc', do_toc)