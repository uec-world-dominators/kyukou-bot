import os
import yaml

settings = {}

def load_settings(relative_path):
    path = os.path.join(os.path.dirname(__file__), relative_path)
    with open(path, 'rt', encoding='utf-8') as f:
        settings = yaml.load(f, Loader=yaml.SafeLoader)
