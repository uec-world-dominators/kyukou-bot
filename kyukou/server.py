from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

import json
from .route import Router


def app(environ, start_response):
    status, headers, ret = Router.search({
        "method": environ['REQUEST_METHOD'],
        "path": environ['PATH_INFO']
    })(environ)
    start_response(status, headers)
    return ret


def run_server(port=8000):
    with make_server('', port, app) as httpd:
        print(f'listen on port {port}.')
        httpd.serve_forever()
