

class Route():
    def __init__(self, info):
        self.method = info['method']
        self.path = info['path']
        self.func = info['func']

    def match(self, info):
        return self.method == info['method'] and info['path'].startswith(self.path)

    def get_func(self):
        return self.func


class Router():
    routes = []

    def __init__(self):
        print('hoge')

    @classmethod
    def append_route(cls, info):
        cls.routes.append(Route(info))

    @classmethod
    def search(cls, info):
        for route in cls.routes:
            if route.match(info):
                return route.get_func()


def route(method, path):
    def wrapper(func):
        def _wrapper():
            return func('environ')
        Router.append_route({
            "method": method,
            "path": path,
            "func": func
        })
        return _wrapper
    return wrapper

def text(text):
    return [text.encode('utf-8')]
