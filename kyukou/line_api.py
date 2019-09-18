
import requests
from .settings import settings
import hmac
import hashlib
import base64
from . import line
from .db import Db
import time


def validate(environ, body):
    if "HTTP_X_LINE_SIGNATURE" in environ:
        xsignature = environ["HTTP_X_LINE_SIGNATURE"].encode('utf-8')
        channel_secret = settings["line"]["channel_secret"].encode('utf-8')
        digest = hmac.new(channel_secret, body, hashlib.sha256).digest()
        base64_digest = base64.b64encode(digest)
        return xsignature == base64_digest
    else:
        return False


{
    "user_id": "",
    "reply_token": "",
    "follow_time": 000000000,
    "last_message_time": 0000000000,
    "lectures": []
}

users_db = Db.get_users_db()


def parse(o):
    try:
        for event in o["events"]:
            _type = event["type"]
            _user_id = event["source"]["userId"]
            if _type == 'follow':
                _reply_token = event["replyToken"]
                users_db.insert_one({
                    "user_id": _user_id,
                    "reply_token": _reply_token,
                    "follow_time": time.time()
                })
                line.follow(_user_id)
            elif _type == 'unfollow':
                users_db.delete_one({"user_id": _user_id})
                line.unfollow(_user_id)
            elif _type == 'message':
                _msg_type = event["message"]["type"]
                if _msg_type == 'text':
                    _reply_token = event["replyToken"]
                    _msg_text = event["message"]["text"]
                    if not users_db.find_one({"user_id": _user_id}):
                        users_db.insert_one({
                            "user_id": _user_id,
                            "reply_token": _reply_token,
                            "follow_time": time.time()
                        })
                    users_db.update_one({"user_id": _user_id, }, {
                        "$set": {
                            "reply_token": _reply_token,
                            "last_message_time": time.time()
                        }
                    })
                    line.message(_user_id, _msg_text)
                else:
                    pass
            else:
                pass
    except KeyError:
        pass


def reply(user_id, msg_texts):
    data = users_db.find_one({
        "user_id": user_id
    })
    if data:
        url = 'https://api.line.me/v2/bot/message/reply'
        res = requests.post(url, json={
            "replyToken": data["reply_token"],
            "messages": [{"type": "text", "text": text}for text in msg_texts]
        }, headers={
            'content-type': 'application/json',
            'authorization': f'Bearer {settings["line"]["access_token"]}'
        })
        return res.status_code
    else:
        raise RuntimeError


def push(user_id, msg_texts):
    data = users_db.find_one({
        "user_id": user_id
    })
    url = 'https://api.line.me/v2/bot/message/push'
    res = requests.post(url, json={
        "to": user_id,
        "messages": [{"type": "text", "text": text}for text in msg_texts]
    }, headers={
        'content-type': 'application/json',
        'authorization': f'Bearer {settings["line"]["access_token"]}'
    })
    return res.status_code


def broadcast(msg_texts):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    res = requests.post(url, json={
        "messages": [{"type": "text", "text": text}for text in msg_texts]
    }, headers={
        'content-type': 'application/json',
        'authorization': f'Bearer {settings["line"]["access_token"]}'
    })
    return res.status_code


def multicast(user_ids, msg_texts):
    url = 'https://api.line.me/v2/bot/message/multicast'
    res = requests.post(url, json={
        "to": user_ids,
        "messages": [{"type": "text", "text": text}for text in msg_texts]
    }, headers={
        'content-type': 'application/json',
        'authorization': f'Bearer {settings["line"]["access_token"]}'
    })
    return res.status_code
