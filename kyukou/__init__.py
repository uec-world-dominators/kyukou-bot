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
from .route import Router
from . import scryping

sys.stdout.flush()

from . import scheduler
from . import publish
from . import search
scheduler.init(0.1)
scheduler.add_task(3600, scryping.run)
scheduler.add_task(1, search.make_notification_dict)
scheduler.add_task(2, publish.publish_all)

__all__ = ['run_server','Router','log']
