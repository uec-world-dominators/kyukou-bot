from .route import *
from pprint import pprint
from . import line_api
from . import email_api
from . import google_api
import re
from . import certificate
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


def get_query(environ):
    try:
        src = environ['QUERY_STRING']
        r = {}
        for e in src.split('&'):
            s = e.split('=')
            r[s[0]] = s[1]
        return r
    except:
        return None


@route('get', '/api/v1/line/email')
def line_email_validation(environ):
    q = get_query(environ)
    data = certificate.validate_token(q['realid'], 'line_email', q['token'])
    if data:
        print(data['email_addr'])

    return status(200)


@route('head', '/api/v1/upload/validate')
def validate_upload_token(environ):
    realid, token = environ.get("HTTP_X_KYUKOU_REALID"), environ.get("HTTP_X_KYUKOU_TOKEN")
    if realid and token and certificate.validate_token(realid, token, 'csv_upload', expire=False):
        return status(200)
    else:
        return status(403)


@route('post', '/api/v1/upload')
def upload_csv(environ):
    realid, token = environ.get("HTTP_X_KYUKOU_REALID"), environ.get("HTTP_X_KYUKOU_TOKEN")
    if realid and token and certificate.validate_token(realid, token):
        line_user_id = line_api.get_line_user_id(realid)
        line_api.push(line_user_id, ['CSVファイルがアップロードされました'])
        return text(f'validated. user={line_user_id}')
    else:
        return status(403)


@route('get', '/oauth/google/redirect_link')
def google_oauth_start_auth(environ):
    return text(google_api.get_redirect_link())


@route('get', '/oauth/google/redirect')
def google_oauth_redirect(environ):
    pass


@route('post', '/api/v1/email/register')
def email(environ):
    if email_api.register(get_body_json(environ)):
        certificate.generate_token()
    return status(200)


@route(re.compile('.*'), '/')
def fallback(environ):
    return file(environ["PATH_INFO"])
