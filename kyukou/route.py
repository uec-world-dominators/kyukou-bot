import json as pkg_json
from typing import Pattern


class Route():
    def __init__(self, func, args):
        self.method = args['method'] if isinstance(args['method'], Pattern) else args['method'].lower()
        self.path = args['path'] if isinstance(args['path'], Pattern) else args['path'].lower()
        self.func = func

    def match(self, args):
        r = True
        r &= bool(self.method.match(args['method'].lower())) if isinstance(self.method, Pattern) else args['method'].lower() == self.method
        r &= bool(self.method.match(args['path'].lower())) if isinstance(self.path, Pattern) else args['path'].lower().startswith(self.path)
        return r

    def get_func(self):
        return self.func


class Router():
    routes = []

    @classmethod
    def append_route(cls, func, args):
        cls.routes.append(Route(func, args))

    @classmethod
    def search(cls, args):
        for route in cls.routes:
            if route.match(args):
                return route.get_func()


def route(method, path, **kwargs):
    def wrapper(func):
        def _wrapper():
            return func('environ')
        kwargs.update(method=method, path=path)
        Router.append_route(func, kwargs)
        return _wrapper
    return wrapper


def text(text):
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    return status, headers, [text.encode('utf-8')]


def status(n):
    return str(n).ljust(4), [], []


def json(obj):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=utf-8')]
    return status, headers, [pkg_json.dumps(obj).encode('utf-8')]


def get_body(environ):
    wsgi_input = environ["wsgi.input"]
    content_length = int(environ["CONTENT_LENGTH"])
    return wsgi_input.read(content_length)


def get_body_utf8(environ):
    return get_body(environ).decode('utf-8')


def get_body_json(environ):
    return pkg_json.loads(get_body_utf8(environ))


def body_to_utf8(body):
    return body.decode('utf-8')


def body_to_json(body):
    return pkg_json.loads(body_to_utf8(body))
