import os
import logging

# Use Django 1.2.
from google.appengine.dist import use_library
use_library('django', '1.2')

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_settings'

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
  author = db.ReferenceProperty(Author, collection_name='author_one_set')
  second_author = db.ReferenceProperty(Author, collection_name='author_two_set')
  url = db.StringProperty()
  browser_support = db.StringListProperty()
  update_date = db.DateProperty()
  publication_date = db.DateProperty()
  #generic tags and html5 feature group tags('offline', 'multimedia', etc.)
  tags = db.StringListProperty()

  @classmethod
  def get_all(self):
    tutorials_query = memcache.get('tutorials')
    if tutorials_query is None:
      tutorials_query = self.all()
      memcache.set('tutorials', tutorials_query)

    return tutorials_query

  @classmethod
  def get_tutorials_by_author(self, author_id):
    tutorials_by_author = memcache.get('tutorials_by_' + author_id)
    if tutorials_by_author is None:
      tutorials_by_author1 = Author.get_by_key_name(author_id).author_one_set
      tutorials_by_author2 = Author.get_by_key_name(author_id).author_two_set

      tutorials_by_author = [x for x in tutorials_by_author1]
      temp2 = [x for x in tutorials_by_author2]
      tutorials_by_author.extend(temp2)

      # Order by published date. Latest first.
      tutorials_by_author.sort(key=lambda x: x.publication_date, reverse=True)

      memcache.set('tutorials_by_' + author_id, tutorials_by_author)

    return tutorials_by_author


class TutorialForm(djangoforms.ModelForm):
  import datetime

  class Meta:
    model = Resource
    #exclude = ['update_date']
    #fields = ['title', 'url', 'author', 'description', 'tags']

  sorted_profiles = get_sorted_profiles(update_cache=True)
  author = forms.ChoiceField(choices=[(p['id'],
      '%s %s' % (p['given_name'], p['family_name'])) for p in sorted_profiles])
  second_author = author

  browsers = ['Chrome', 'FF', 'Safari', 'Opera', 'IE']
  browser_support = forms.MultipleChoiceField(
      widget=forms.CheckboxSelectMultiple, choices=[(b,b) for b in browsers])

  tags = forms.CharField(
      help_text='Comma separated list (e.g. offline, performance, demo, ...)')
  description = forms.CharField(
      widget=forms.Textarea(attrs={'rows': 5, 'cols': 20}),
      help_text=('Description for this resource. If tutorial, a summary of the '
                 'tutorial. <br>Can include markup.'))
  publication_date = forms.DateField(label='Publish date',
                                     initial=datetime.date.today)
  update_date = forms.DateField(label='Updated date')#,initial=datetime.date.today)
  url = forms.CharField(label='URL',
      help_text='An abs. or relative url (e.g. /tutorials/feature/something)')

  def __init__(self, *args, **keyargs):
    super(TutorialForm, self).__init__(*args, **keyargs)

    for field in self.fields:
      if self.Meta.model.properties()[field].required and field != 'browser_support':
        self.fields[field].widget.attrs['required'] = 'required'
