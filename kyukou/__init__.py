print('Kyukou Bot started')

from .settings import *
load_settings('config.yml')

from . import db
db.init(get_settings()["mongo_url"])

from .server import run_server
from .routes import *

import sys
sys.stdout.flush()


from . import scheduler
scheduler.init(tick_interval_sec=1)

__all__ = ['run_server']
