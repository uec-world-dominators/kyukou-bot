from .server import run_server
from .routes import *
from .settings import load_settings
load_settings('config.yml')

__all__ = ['run_server']
