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