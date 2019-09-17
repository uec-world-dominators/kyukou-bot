from .settings import *
load_settings('config.yml')

from .server import run_server
from .routes import *

from .db import Db
Db.init(get_settings()["mongo_url"])

__all__ = ['run_server']
