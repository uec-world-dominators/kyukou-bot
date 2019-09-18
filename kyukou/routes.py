from .route import *
from pprint import pprint
from . import line_api
from . import email_api
import re

# 上から順に優先

# LINE botからイベントがあったときに来る
@route('post', '/api/v1/line/webhook')
def line_webhook(environ):
    body = get_body(environ)
    o = body_to_json(body)
    if line_api.validate(environ, body):
        line_api.parse(o)
        return status(200)
    else:
        return status(403)


@route('post', '/api/v1/upload')
def upload_csv(environ):
    print(get_body(environ))
    return status(200)


@route('post', '/api/v1/email/register')
def email(environ):
    email_api.register(get_body_json(environ))
    return status(200)


@route(re.compile('.*'), '/')
def fallback(environ):
    return file(environ["PATH_INFO"])