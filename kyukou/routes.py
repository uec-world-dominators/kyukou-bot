import urllib
from .route import *
from pprint import pprint
from . import line_api
from . import email_api
from . import google_api
from . import line_notify_api
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


@route('get', '/api/v1/line/notify/redirect_link')
def line_notify_redirect_link(environ):
    realid = get_query(environ).get('realid')
    if realid:
        return redirect(line_notify_api.get_redirect_link(realid))
    else:
        return status(400)


@route('get', '/api/v1/line/notify')
def line_notify(environ):
    q = get_query(environ)
    data = certificate.validate_state(q['state'], 'line_notify_oauth')
    if data:
        tokens = line_notify_api.code_to_access_token(q['code'])
        if tokens:
            line_notify_api.append(data['realid'], tokens)
            return file('/')
    return status(400)


def get_query(environ):
    try:
        src = urllib.parse.unquote(environ['QUERY_STRING'])
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
    data = certificate.validate_token('line_email', q['realid'], q['token'])
    if data:
        email_api.append({
            'email_addr': data['email_addr'],
            'real_user_id': q['realid'],
            'referrer': 'line'
        })
        return file('/c/validated')
    else:
        return status(400)


@route('head', '/api/v1/upload/validate')
def validate_upload_token(environ):
    realid, token = environ.get("HTTP_X_KYUKOU_REALID"), environ.get("HTTP_X_KYUKOU_TOKEN")
    if realid and token and certificate.validate_token('csv_upload', realid, token, expire=False):
        return status(200)
    else:
        return status(403)


@route('post', '/api/v1/upload')
def upload_csv(environ):
    realid, token = environ.get("HTTP_X_KYUKOU_REALID"), environ.get("HTTP_X_KYUKOU_TOKEN")
    if realid and token and certificate.validate_token('csv_upload', realid, token):
        line_user_id = line_api.get_line_user_id(realid)
        line_api.push(line_user_id, [
            'おめでとうございます！CSVファイルがアップロードされました！',
            '休講情報を配信するためにLINE Notifyの連携をお願いします。これが最後のステップです',
            line_notify_api.get_redirect_link(realid)
        ])
        return text(f'validated. user={line_user_id}')
    else:
        return status(403)


@route('get', '/oauth/google/redirect_link')
def google_oauth_start_auth(environ):
    return redirect(google_api.get_redirect_link())


@route('get', '/oauth/google/redirect')
def google_oauth_redirect(environ):
    q = get_query(environ)
    data = certificate.validate_state(q['state'], 'google_oauth')
    if data:
        profile, tokens = google_api.code_to_refresh_token(q['code'])
        google_api.register(profile, tokens, data['realid'])
        return status(200)
    else:
        return status(400)


@route('post', '/api/v1/email/register')
def email(environ):
    if email_api.register(get_body_json(environ)):
        certificate.generate_token()
    return status(200)


@route(re.compile('.*'), '/')
def fallback(environ):
    return file(environ["PATH_INFO"])
