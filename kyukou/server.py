import asyncio
from socketserver import ThreadingMixIn
from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler

import json
from .route import Router

import sys
from .util import log, ignore_error
from .settings import settings
from concurrent.futures import ThreadPoolExecutor
import subprocess

import json
import time


def execute(environ, start_response):
    status, headers, ret = Router.do(environ)
    try:
        log(__name__, f'{environ["HTTP_X_REAL_IP"].ljust(15)}  |  {status.ljust(15)}  [{environ["REQUEST_METHOD"].ljust(5)}] {environ["PATH_INFO"]}  ({environ["SERVER_PROTOCOL"]}) {environ["HTTP_X_REQUEST_ID"]}')
    except:
        pass
    start_response(status, headers)
    sys.stdout.flush()
    return ret


pool = ThreadPoolExecutor(1000)


def app(environ, start_response):
    return pool.submit(execute, environ, start_response).result()


class NoLoggingWSGIRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        pass


class ThreadingWsgiServer(ThreadingMixIn, WSGIServer):
    pass


def run_server():
    port = settings["port"]
    try:
        subprocess.check_call(['bash', '-c', f'kill -9 `lsof -t -i:{port}`'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    finally:
        time.sleep(1)
    with make_server('localhost', port, app, ThreadingWsgiServer, handler_class=NoLoggingWSGIRequestHandler) as httpd:
        log(__name__, f'Listen on port: {port}')
        httpd.serve_forever()
