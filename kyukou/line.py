import time
from .db import Db
from . import line_api
import json
from . import upload

import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def follow(user_id):
    print(f'followed by {user_id}')
    line_api.reply(user_id, ['こんにちは'])


def unfollow(user_id):
    print(f'unfollowed by {user_id}')


def message(user_id, msg_text):
    if msg_text.strip().lower() == 'csv':
        link = upload.generate_upload_link(line_api.get_real_user_id(user_id))
        line_api.reply(user_id, [link,'このリンクからCSVファイルをアップロードしてください。リンクの有効期限は1時間です。'])
    else:
        print(f'message from {user_id}: {msg_text}')
        line_api.reply(user_id, [msg_text])
