import os
import yaml
import logging

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms
from django import forms

if 'SERVER_SOFTWARE' in os.environ:
  PROD = not os.environ['SERVER_SOFTWARE'].startswith('Development')
else:
  PROD = True

def get_profiles():
  profiles = memcache.get('profiles')
  if profiles is None:

    profiles = dict()
    query = Author.all()

    for profile in query:
      id = profile.key().name()
      profiles[id] = profile
      profiles[id].id = id

    memcache.set('profiles', profiles)

  return profiles

def get_sorted_profiles():
  return sorted(get_profiles().values(),
                key=lambda profile:profile.family_name)

def get_profile_amount():
  return len(get_profiles())

class Author(db.Model):
  """Container for author information.
  """

  given_name = db.StringProperty(required=True)
  family_name = db.StringProperty(required=True)
  org = db.StringProperty(required=True)
  unit = db.StringProperty(required=True)
  city = db.StringProperty(required=True)
  state = db.StringProperty(required=True)
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

  def __init__(self, *args, **keyargs):
    super(AuthorForm, self).__init__(*args, **keyargs)

    for field in self.fields:
      if (self.Meta.model.properties()[field].required):
        self.fields[field].widget.attrs['required'] = 'required'
