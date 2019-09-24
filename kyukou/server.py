from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler

import json
from .route import Router

import sys
from .util import log
from .settings import settings
import subprocess

import json
import time


def app(environ, start_response):
    status, headers, ret = Router.do(environ)
    log(__name__, f'{environ["HTTP_X_FORWARDED_FOR"].ljust(15)}  |  {status.ljust(15)}  [{environ["REQUEST_METHOD"].ljust(5)}] {environ["PATH_INFO"]}  ({environ["SERVER_PROTOCOL"]})')
    start_response(status, headers)
    sys.stdout.flush()
    return ret


class NoLoggingWSGIRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        pass


def run_server():
    port = settings["port"]
    try:
        subprocess.check_call(['bash', '-c', f'kill -9 `lsof -t -i:{port}`'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except:
        pass
    finally:
        time.sleep(1)
    with make_server('', port, app, handler_class=NoLoggingWSGIRequestHandler) as httpd:
        log(__name__, f'Listen on port: {port}')
        httpd.serve_forever()
