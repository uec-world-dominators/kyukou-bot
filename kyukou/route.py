import json as pkg_json


class Route():
    def __init__(self, func, args):
        self.method = args['method'].lower()
        self.path = args['path'].lower()
        self.func = func

    def match(self, args):
        return self.method == args['method'].lower() and args['path'].lower().startswith(self.path)

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


def json(obj):
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    return status, headers, [pkg_json.dumps(obj).encode('utf-8')]
