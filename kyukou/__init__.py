import sys
from .settings import *
load_settings('config.yml')
settings=get_settings()


from .util import log
log(__name__,f'Kyukou Bot started at: "{settings.url_prefix()}"',5)

from . import db
db.init(settings.mongo_url())

from .server import run_server
from .routes import *
from . import scryping

sys.stdout.flush()

from . import scheduler
scheduler.init(tick_interval_sec=1)

from . import search

__all__ = ['run_server']
