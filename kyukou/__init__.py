if 1:
    import sys
    from .settings import *
    load_settings('config.yml')
    settings = get_settings()

    from .util import log, ignore_error
    log(__name__, f'Kyukou Bot started at: "{settings.url_prefix()}"', 5)

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
    from . import info
    from . import procedure
    scheduler.init(0.1)
    scheduler.add_task(3600, ignore_error([(scryping.run,), (info.create_md,)]))
    # scheduler.add_task(3600, ignore_error([(info.create_md,)]))
    scheduler.add_task(60, search.search_lectures)
    scheduler.add_task(5, publish.publish_all)
    scheduler.add_task(60, certificate.delete_expired)
    scheduler.add_task(60, procedure.ProcedureSelectorDB.clear_all)

__all__=['run_server', 'Router', 'log']
