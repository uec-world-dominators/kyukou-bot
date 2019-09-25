import json
import base64
from .settings import settings
import requests
from . import util
from .db import get_collection
import urllib
from .import certificate
from bson.objectid import ObjectId


users_db = get_collection('users')


client_id = '723530674332-g9bq3lq6e921pip895vk6mgg91fhui4l.apps.googleusercontent.com'
redirect_uri = f'{settings.url_prefix()}/oauth/google/redirect'
scope = 'email+profile+openid'
access_type = 'offline'
prompt = 'consent'  # 'select_account'
response_type = 'code'


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
