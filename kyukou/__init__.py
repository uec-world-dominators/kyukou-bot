print('Kyukou Bot started')

from .settings import *
load_settings('config.yml')

from .db import Db
Db.init(get_settings()["mongo_url"])

from .server import run_server
from .routes import *


__all__ = ['run_server']
