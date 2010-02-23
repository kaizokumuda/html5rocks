import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import django
import django.template

register = webapp.template.create_template_register()

def render_toc(toc):
  logging.warning("TOC: %s" % toc)
  return {'toc' : toc}

class TOCNode(django.template.Node):
  def render(self, context):
    logging.warning(context)
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

basedir = os.path.dirname(__file__)
toc_template_path = os.path.join(basedir, "content", "toc.html")
register.inclusion_tag(toc_template_path)(render_toc)
register.tag('toc', do_toc)