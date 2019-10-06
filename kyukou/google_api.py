import datetime
from datetime import datetime, timedelta
import time
import json
import base64
import requests
from bson.objectid import ObjectId
import urllib
isinpackage = not __name__ in ['google_api', '__main__']
if isinpackage:
    from .settings import settings
    from . import util
    from .util import Just
    from .db import get_collection
    from .import certificate
else:
    from settings import settings
    # import util
    from util import Just
    from db import get_collection
    # import certificate


users_db = get_collection('users')


client_id = settings.google.client_id()
redirect_uri = f'{settings.url_prefix()}/api/v1/oauth/google/redirect'
scope = urllib.parse.quote(settings.google.scope(), safe='')
access_type = settings.google.access_type()
prompt = settings.google.prompt()
response_type = settings.google.response_type()


def get_certs_keys(kid):
    url = 'https://www.googleapis.com/oauth2/v3/certs'
    data = requests.get(url).json()['keys']
    return next(filter(lambda e: kid == e['kid']), None)


def get_redirect_link(realid=None):
    state = util.generate_id(50)
    certificate.register_state(state, "google_oauth", {"realid": realid})
    return 'https://accounts.google.com/o/oauth2/v2/auth?' \
        + f"client_id={client_id}&" \
        + f"include_granted_scopes={'true'}&" \
        + f"redirect_uri={redirect_uri}&" \
        + f"scope={scope}&" \
        + f"access_type={access_type}&" \
        + f"state={state}&" \
        + f"prompt={prompt}&" \
        + f"response_type={response_type}"


def code_to_refresh_token(code):
    endpoint = 'https://oauth2.googleapis.com/token'
    tokens = requests.post(endpoint, {
        'code': code,
        'client_id': client_id,
        'client_secret': settings.google.google_client_secret(),
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }).json()
    header, profile = decode_id_token(tokens['id_token'])
    return profile, tokens


def decode_base64_padding(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4)).decode()


def decode_id_token(id_token):
    s = id_token.split('.')
    header = json.loads(decode_base64_padding(s[0]))
    payload = json.loads(decode_base64_padding(s[1]))
    # key = get_certs_keys(header['kid'])
    return header, payload


def register(profile, tokens, realid=None):
    profile.update(tokens)
    user = users_db.find_one({'_id': ObjectId(realid), 'connections.google.sub': profile['sub']})
    if realid:
        users_db.update_one({'_id': ObjectId(realid)}, {
            '$set': {
                'connections.google': profile,
            },
            '$inc': {
                'connections.length': 0 if user else 1
            }
        })
        print('add google info')
    else:
        users_db.insert_one({
            'connections': {
                'google': profile,
                'length': 1
            }
        })
        print('connect with google')


def refresh_token(refresh_token):
    endpoint = 'https://oauth2.googleapis.com/token'
    return requests.post(endpoint, {
        'client_id': client_id,
        'client_secret': settings.google.google_client_secret(),
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).json()


def verify_access_token(access_token):
    url = f'https://oauth2.googleapis.com/tokeninfo?access_token={access_token}'
    return requests.get(url).status_code == 200


def get_access_token(google_user_id):
    data = Just(users_db.find_one({'connections.google.sub': google_user_id}))
    access_token = data.connections.google.access_token()
    _refresh_token = data.connections.google.refresh_token()
    assert _refresh_token
    if access_token and verify_access_token(access_token):
        return access_token
    else:
        return Just(refresh_token(_refresh_token)).access_token()


def get_real_user_id(user_id):
    return str(users_db.find_one({"connections.google.sub": user_id})["_id"])


def get_google_user_id(real_user_id):
    data = Just(users_db.find_one({"_id": ObjectId(real_user_id)}))
    if data() and ('line' in data.connections()):
        return data.connections.google.sub()
    else:
        raise RuntimeError


def add_event(real_user_id, start, end, options={
    'summary': '',
    'description': ''
}):
    endpoint = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
    d = {
        'end': {
            'dateTime': end,
            'timeZone': 'Asia/Tokyo'
        },
        'start': {
            'dateTime': start,
            'timeZone': 'Asia/Tokyo'
        },
    }
    d.update(options)
    res = requests.post(endpoint, json=d, headers={
        'content-type': 'application/json',
        'authorization': f'Bearer {get_access_token(get_google_user_id(real_user_id))}'
    })
    r = res.status_code == 200
    if not r:
        print(res.text)
    return r
