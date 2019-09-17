from .route import route, text, json

# 上から順に優先

@route('get', '/hoge')
def hoge(environ):
    return text('hello hoge')


@route('get', '/hige')
def hige(environ):
    return json({"hoge": 47563})


@route('get', '/')
def fallback(environ):
    return text('This is fallback')
