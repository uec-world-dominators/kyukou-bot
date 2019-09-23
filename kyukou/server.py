from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

import json
from .route import Router

import sys
from .util import log
from .settings import settings


def app(environ, start_response):
    status, headers, ret = Router.do(environ)
    start_response(status, headers)
    sys.stdout.flush()
    return ret


def run_server():
    port = settings["port"]
    with make_server('', port, app) as httpd:
        log(__name__,f'Listen on port: {port}')
        httpd.serve_forever()
