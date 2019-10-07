import os
from operator import getitem
from pprint import pprint
import hmac
import hashlib
from datetime import datetime
import time
import json
import base64
import requests
import urllib
from bson.objectid import ObjectId
from urllib.parse import urlencode, quote, quote_plus, parse_qs, unquote
isinpackage = not __name__ in ['twitter_api', '__main__']
if isinpackage:
    from . import util
    from . import twitter
    from .settings import settings
    from . import util
    from .util import Just,log
    from .db import get_collection
    from .import certificate
    users_db = get_collection('users')
else:
    import util
    from settings import settings
TOKENS_FILE = os.path.join(os.path.dirname(__file__), 'tokens')

# https://docs.python.org/ja/3/library/urllib.parse.html#urllib.parse.urlencode


def generate_signature(method, raw_url, raw_params, raw_key):
    param_string = quote(urlencode(sorted(raw_params.items(), key=lambda e: e[0]), quote_via=quote, safe=''), safe='')
    url = quote(raw_url, safe='')
    signature_base_string = '&'.join([method, url, param_string]).encode()
    signing_key = raw_key.encode()
    digest = hmac.new(signing_key, signature_base_string, hashlib.sha1).digest()
    return base64.b64encode(digest)


def get_access_token(oauth_token, oauth_verifier):
    url = f'https://api.twitter.com/oauth/access_token?oauth_verifier={oauth_verifier}'
    tokens = load_tokens()
    res = post(url, oauth_token, tokens['oauth_token_secret'])
    if res.status_code == 200:
        return parse_query(res.text)
    else:
        return None


def parse_query(src):
    try:
        r = {}
        for e in src.split('&'):
            s = e.split('=')
            r[unquote(s[0])] = unquote(s[1])
        return r
    except:
        return None


def http(method, method_function, baseurl, oauth_token, oauth_token_secret, d={}, nonce='hogehogehoge', headers={}, data=''):
    url = f'{baseurl}{"?"if d else ""}{urlencode(d,quote_via=quote)}'
    raw_params = {
        'oauth_callback': settings.url_prefix()+settings.twitter.callback_path(),
        "oauth_consumer_key": settings.twitter.consumer_key(),
        "oauth_signature_method": 'HMAC-SHA1',
        "oauth_timestamp": time.time(),
        "oauth_nonce": nonce,
        "oauth_version": "1.0",
        "oauth_token": oauth_token
    }
    params = dict(raw_params)
    for k, v in d.items():
        params[k] = v
    raw_key = settings.twitter.consumer_key_secret()+'&'+oauth_token_secret
    raw_params['oauth_signature'] = generate_signature(method, baseurl, params, raw_key)
    default_headers = {
        'Authorization': f'OAuth {urlencode(raw_params,quote_via=quote).replace("&",",")}'
    }
    default_headers.update(headers)
    res= method_function(url, headers=default_headers, data=data)
    if res.status_code!=200:
        log(__name__,res.text)
    return res


def post(baseurl, oauth_token, oauth_token_secret, d={}, nonce='hogehogehoge', headers={}, data=''):
    return http('POST', requests.post, baseurl, oauth_token, oauth_token_secret, d, nonce, headers, data)


def put(baseurl, oauth_token, oauth_token_secret, d={}, nonce='hogehogehoge', headers={}, data=''):
    return http('PUT', requests.put, baseurl, oauth_token, oauth_token_secret, d, nonce, headers, data)


def store_tokens(o):
    with open(TOKENS_FILE, 'wt', encoding='utf-8') as f:
        json.dump(o, f)


def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'rt', encoding='utf-8') as f:
            return json.load(f)
    else:
        return None


def get_redirect_url():
    raw_url = 'https://api.twitter.com/oauth/request_token'
    res = post(raw_url, settings.twitter.access_token(), settings.twitter.access_token_secret())
    print(res.text)
    query = parse_query(res.text)
    store_tokens(query)
    return 'https://api.twitter.com/oauth/authenticate?oauth_token='+query['oauth_token']


def register(user_id, data, realid=None):
    data['follow_time'] = time.time()
    default_notify = settings.default_notify()
    default_notify.update({'dest': 'twitter'})
    if realid:  # 連携追加
        users_db.update_one({'_id': ObjectId(realid)}, {
            '$set': {
                'connections.twitter': data
            },
            'notifies': [settings.default_notify()]
        })
    elif users_db.find_one({'connections.twitter.id': user_id}):  # ツイッターデータ上書き
        users_db.update_one({'connections.twitter.id': user_id}, {
            '$set': {
                'connections.twitter': data
            }
        })
    else:  # 新規登録
        users_db.insert_one({
            'connections': {
                'twitter': data
            },
            'notifies': [settings.default_notify()]
        })


def get_real_user_id(user_id):
    return Just(users_db.find_one({"connections.twitter.id": user_id}))._id[lambda e:None if e == None else str(e)]()


def get_twitter_user_id(real_user_id):
    return Just(users_db.find_one({"_id": ObjectId(real_user_id)})).connections.twitter.id()


def parse(o):
    data = Just(o)
    # direct messsage event
    event = data.direct_message_events[lambda l:l[0]]
    if event():
        user_id = event.message_create.sender_id()
        if user_id != load_tokens()['user_id']:
            msg_text = event.message_create.message_data.text()
            if not get_real_user_id(user_id): # いきなりDMが来たとき
                register(user_id, data.users[user_id])
                twitter.follow(user_id)
            twitter.direct_message(user_id, msg_text)
            return
        else:
            return
    # follow event
    event = data.follow_events[lambda l:l[0]]
    if event():
        user_id = event.source.id()
        register(user_id, event.source())
        twitter.follow(user_id)
        return
    # dm indicate typing event
    event = data.direct_message_indicate_typing_events[lambda l:l[0]]
    if event():
        user_id = event.message_create.sender_id()
        if not get_real_user_id(user_id):
            register(user_id, data.users[user_id])
            twitter.follow(user_id)
        return
    # tweet delete event
    event = data.tweet_delete_events[lambda l:l[0]]
    if event():
        return
    # favorite event
    event = data.favorite_events[lambda l:l[0]]
    if event():
        return
    # tweet create event
    event = data.tweet_create_events[lambda l:l[0]]
    if event():
        return

    print(o)


def sends(user_id, msg_texts):
    for msg_text in msg_texts:
        send(user_id, msg_text)


def send(user_id, msg_text):
    url = 'https://api.twitter.com/1.1/direct_messages/events/new.json'
    data = {
        'event': {
            'type': 'message_create',
            'message_create': {
                'target': {
                    'recipient_id': user_id,
                },
                'message_data': {
                    'text': f'{msg_text} [{util.generate_id(2)}]',
                }
            }
        }
    }
    tokens = load_tokens()
    res = post(url, tokens['oauth_token'], tokens['oauth_token_secret'], headers={
        'content-type': 'application/json'
    }, data=json.dumps(data))
    return res.status_code == 200


def tweet_basic(msg, oauth_token, oauth_token_secret):
    url = f'https://api.twitter.com/1.1/statuses/update.json'
    res = post(url, oauth_token, oauth_token_secret, {
        'status': msg
    })

    if res.status_code != 200:
        log(__name__, res.text)
    return res


def tweet(msg):
    tokens = load_tokens()
    return tweet_basic(msg, tokens['oauth_token'], tokens['oauth_token_secret'])


def validate_webhook():
    url = f'https://api.twitter.com/1.1/account_activity/all/{settings.twitter.account_activity_api_env()}/webhooks.json'  # ?url={settings.url_prefix()}{settings.twitter.callback_path()}'
    return post(url, settings.twitter.access_token(), settings.twitter.access_token_secret(), {
        'url': f'{settings.url_prefix()}{settings.twitter.webhook_path()}'
    })


def subscribe_user(webhook_id, oauth_token, oauth_token_secret):
    url = f'https://api.twitter.com/1.1/account_activity/all/{settings.twitter.account_activity_api_env()}/subscriptions.json'
    res = post(url, oauth_token, oauth_token_secret, headers={
        'content-type': 'application/json'
    }, data=json.dumps({
        'webhook_id': webhook_id
    }))
    print(res.status_code, res.status_code == 204)
