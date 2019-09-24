from .settings import *
load_settings('config.yml')
settings=get_settings()

from .util import log
log(__name__,f'Kyukou Bot started at: "{settings.url_prefix()}"')

from . import db
db.init(settings.mongo_url())

from .server import run_server
from .routes import *
from . import scryping

import sys
sys.stdout.flush()


from . import scheduler
scheduler.init(tick_interval_sec=1)

__all__ = ['run_server']
