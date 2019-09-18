from .route import *
from pprint import pprint
from . import line_api
import re

# 上から順に優先

# LINE botからイベントがあったときに来る
@route('post', '/api/line/webhook')
def line_webhook(environ):
    body = get_body(environ)
    o = body_to_json(body)
    if line_api.validate(environ, body):
        line_api.parse(o)
        return status(200)
    else:
        return status(400)


@route(re.compile('.*'), '/')
def fallback(environ):
    return text('This is fallback')
