import os
import logging

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms
from django import forms

if 'SERVER_SOFTWARE' in os.environ:
  PROD = not os.environ['SERVER_SOFTWARE'].startswith('Development')
else:
  PROD = True

def get_profiles(update_cache=False):
  profiles = memcache.get('profiles')
  if profiles is None or update_cache:
    profiles = {}
    authors = Author.all()

    for author in authors:
      author_id = author.key().name()
      profiles[author_id] = author.to_dict()
      profiles[author_id]['id'] = author_id

    memcache.set('profiles', profiles)

  return profiles

def get_sorted_profiles(update_cache=False):
  return sorted(get_profiles(update_cache).values(),
                key=lambda profile:profile['family_name'])


class DictModel(db.Model):
  def to_dict(self):
    #unicode(getattr(self, p)) if p is not None else None
    return dict([(p, getattr(self, p)) for p in self.properties()])


class Author(DictModel):
  """Container for author information."""

  given_name = db.StringProperty(required=True)
  family_name = db.StringProperty(required=True)
  org = db.StringProperty(required=True)
  unit = db.StringProperty(required=True)
  city = db.StringProperty()
  state = db.StringProperty()
  country = db.StringProperty(required=True)
  geo_location = db.GeoPtProperty()
  homepage = db.LinkProperty()
  google_account = db.StringProperty()
  twitter_account = db.StringProperty()
  email = db.EmailProperty()
  lanyrd = db.BooleanProperty(default=False)


class AuthorForm(djangoforms.ModelForm):
  class Meta:
    model = Author
    # exlucde geo_location field from form. Handle lat/lon separately
    exclude = ['geo_location']

  def __init__(self, *args, **keyargs):
    super(AuthorForm, self).__init__(*args, **keyargs)

    for field in self.fields:
      if (self.Meta.model.properties()[field].required):
        self.fields[field].widget.attrs['required'] = 'required'


class Resource(DictModel):
  """Container for all kinds of resource."""

  title = db.StringProperty(required=True)
  description = db.StringProperty()
  author = db.ReferenceProperty(Author)
  url = db.StringProperty()
  browser_support = db.StringListProperty()
  update_date = db.DateProperty()
  publication_date = db.DateProperty()
  #generic tags and html5 feature group tags('offline', 'multimedia', etc.)
  tags = db.StringListProperty()
