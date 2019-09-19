from .route import *
from pprint import pprint
from . import line_api
from . import email_api
import re
from . import upload
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
    realid, token = environ.get("HTTP_X_KYUKOU_REALID"), environ.get("HTTP_X_KYUKOU_TOKEN")
    if realid and token and upload.validate_token(realid, token):
        line_user_id = line_api.get_line_user_id(realid)
        line_api.push(line_user_id, ['CSVファイルがアップロードされました'])
        return text(f'validated. user={line_user_id}')
    else:
        return status(403)


@route('post', '/api/v1/email/register')
def email(environ):
    email_api.register(get_body_json(environ))
    return status(200)


@route(re.compile('.*'), '/')
def fallback(environ):
    return file(environ["PATH_INFO"])
