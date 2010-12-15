import os
import yaml

def load_profiles():
  basedir = os.path.dirname(__file__)
  f = file(basedir + '/profiles.yaml', 'r')
  profiles = dict()
  for profile in yaml.load_all(f):
    profiles[profile['id']] = profile
  f.close()
  return profiles

