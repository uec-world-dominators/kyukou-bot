from .route import route, text


@route('get', '/hoge')
def hoge(environ):
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    return status, headers, text('hello hoge')


@route('get', '/hige')
def hoge(environ):
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    return status, headers, text('hello hige')
