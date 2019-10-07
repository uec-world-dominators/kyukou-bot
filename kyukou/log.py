import sys
import datetime
import os
from threading import Lock
import requests
isinpackage = not __name__ in ['log', '__main__']
if isinpackage:
    from .settings import settings
else:
    from settings import settings

log_lock = Lock()
log_file = None


def log(__name__, message, log_level=2):
    '''
    ## log level
    5 = FATAL
    4 = ERROR
    3 = WARN
    2 = INFO (default)
    1 = DEBUG
    0 = TRACE
    '''
    global log_file
    log_file = log_file or os.path.join(os.path.dirname(__file__), settings.logfile())
    msg = f'{datetime.now()}  |  [{__name__.ljust(20)}]  {message}'
    with log_lock:
        if log_level >= settings.log_level(0):
            sys.stdout.write(msg)
            sys.stdout.write('\n')
            sys.stdout.flush()
        if settings.log.slack() and log_level >= settings.log.slack.log_level_gt():
            log_with_slack(msg)
        with open(log_file, 'at', encoding='utf-8') as f:
            f.write(msg+'\n')


def log_with_slack(message):
    res = requests.post(settings.log.slack.slack_webhook(), json={
        'text': message
    })
    return res.status_code == 200
