import traceback
import urllib
import mimetypes
import os
import json as pkg_json
import http.client
from ipaddress import IPv4Address, IPv4Network
from functools import reduce
from .util import log

if __name__ != '__main__':
    from typing import Pattern
    from . import util
    from .settings import settings


class Route():
    def __init__(self, func, args):
        self.args = args
        self.networks = list(map(IPv4Network, args['networks']))
        self.networks_len = len(self.networks)
        self.method = self._normalize_arg(args['method'])
        self.path = self._normalize_arg(args['path'])
        self.func = func

    def match(self, environ):
        args = {
            "method": environ['REQUEST_METHOD'],
            "path": environ['PATH_INFO']
        }
        return (not self.networks_len or not 'HTTP_X_REAL_IP' in environ or self._is_in_networks(environ['HTTP_X_REAL_IP']))\
            and (not self.method or self._match_regex_or('method', args, lambda key: args[key].lower() == self.__dict__[key]))\
            and (not self.path or self._match_regex_or('path', args, lambda key: args[key].lower().startswith(self.__dict__[key])))

    def get_func(self):
        return self.func

    def _is_in_networks(self, ip):
        for network in self.networks:
            if IPv4Address(ip) in network:
                return True
        return False

    def _normalize_arg(self, arg):
        return arg if (not arg or isinstance(arg, Pattern)) else arg.lower()

    def _match_regex_or(self, key, args, fn):
        return bool(self.__dict__[key].match(args[key].lower())) if isinstance(self.__dict__[key], Pattern) else fn(key)


class Router():
    routes = []

    @classmethod
    def append_route(cls, func, args):
        cls.routes.append(Route(func, args))

    @classmethod
    def search(cls, environ):
        for route in cls.routes:
            if route.match(environ):
                return route.get_func()

    @classmethod
    def do(cls, environ):
        try:
            return Router.search(environ)(environ)
        except Exception as e:
            log(__name__, traceback.format_exc())
            return status(500)


def route(method=None, path=None, networks=[], **kwargs):
    def wrapper(func):
        def _wrapper():
            return func
        kwargs.update(method=method, path=path, networks=networks)
        Router.append_route(func, kwargs)
        return _wrapper
    return wrapper


def status_message(code):
    return str(code).ljust(4)
    # return str(code)+' ' + http.client.responses[code]


def text(text, status=200, headers={}):
    default_headers = [('Content-type', 'text/plain; charset=utf-8')]
    return status_message(status), util.dict_to_tuples(headers) if len(headers) else default_headers, [text.encode('utf-8')]


def status(n, headers={}):
    return status_message(n), util.dict_to_tuples(headers), []


def redirect(url):
    return status(302, {'Location': url})


def json(obj, status=200, headers={}):
    default_headers = [('Content-type', 'application/json; charset=utf-8')]
    return status_message(status), util.dict_to_tuples(headers) if len(headers) else default_headers, [pkg_json.dumps(obj).encode('utf-8')]


def file(path):
    try:
        public_dir = settings["public_dir"]
        rootpath = os.path.abspath(public_dir)
        abspath = os.path.abspath(os.path.join(public_dir, path[1:]))
        if abspath.startswith(rootpath):
            if os.path.isdir(abspath):
                if not path.endswith('/'):
                    return redirect(path+'/')
                abspath = os.path.join(abspath, settings["index"])
            _type, _ = mimetypes.guess_type(abspath)
            if _type:
                default_headers = [('Content-type', _type)]
            else:
                raise FileNotFoundError
            with open(abspath, 'rb') as fp:
                return status_message(200), default_headers, [fp.read()]
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        return status(404)


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


def get_query(environ):
    try:
        src = urllib.parse.unquote(environ['QUERY_STRING'])
        r = {}
        for e in src.split('&'):
            s = e.split('=')
            r[s[0]] = s[1]
        return r
    except:
        return {}
