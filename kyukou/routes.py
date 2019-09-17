from .route import *
from pprint import pprint
from . import line
import re

# 上から順に優先

# LINE botからイベントがあったときに来る
@route('post', '/api/line/webhook')
def line_webhook(environ):
    body = get_body(environ)
    o = body_to_json(body)
    print(o)
    if line.validate(environ, body):
        line.reply(o)
        return status(200)
    else:
        return status(400)


@route(re.compile('.*'), '/')
def fallback(environ):
    return text('This is fallback')
