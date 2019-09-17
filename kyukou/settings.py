import os
import yaml

settings = {}
env_mark = '__ENV__'


def load_settings(relative_path):
    path = os.path.join(os.path.dirname(__file__), relative_path)
    with open(path, 'rt', encoding='utf-8') as f:
        settings = yaml.load(f, Loader=yaml.SafeLoader)
        settings = resolve_env(settings)
        print(settings["line"]["__ENV__access_token"])


def resolve_env(d):
    for key in d.keys():
        value = d[key]
        if isinstance(value, dict):
            d[key] = resolve_env(value)
        else:
            if key.startswith(env_mark):
                d[key] = os.environ.get(value)
    return d
