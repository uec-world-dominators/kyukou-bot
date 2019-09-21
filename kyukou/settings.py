import os
import yaml
from .util import Just

settings = {}
env_mark = '__ENV__'


def load_settings(relative_path):
    path = os.path.join(os.path.dirname(__file__), relative_path)
    with open(path, 'rt', encoding='utf-8') as f:
        global settings
        settings = yaml.load(f, Loader=yaml.SafeLoader)
        resolve_env(settings)
        settings = Just(settings)


def get_settings():
    return settings


def resolve_env(d):
    tmp = {}
    for key in d.keys():
        value = d[key]
        if isinstance(value, dict):
            resolve_env(value)
        else:
            if key.startswith(env_mark):
                name = key[len(env_mark):]
                tmp[name] = os.environ.get(value)
    d.update(**tmp)
