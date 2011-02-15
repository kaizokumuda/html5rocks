import os
import yaml
import logging

from google.appengine.api import memcache

if 'SERVER_SOFTWARE' in os.environ:
  PROD = not os.environ['SERVER_SOFTWARE'].startswith('Development')
else:
  PROD = True

def get_profiles():
  profiles = memcache.get('profiles')
  if profiles is None:
    basedir = os.path.dirname(__file__)
    f = file(basedir + '/profiles.yaml', 'r')

    profiles = dict()
    for profile in yaml.load_all(f):
      profiles[profile['id']] = profile

    f.close()
    memcache.set('profiles', profiles)

  return profiles

