import os
import yaml

from google.appengine.api import memcache

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

