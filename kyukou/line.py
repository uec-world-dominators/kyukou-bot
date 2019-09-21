import time
from .db import get_collection
from . import line_api
import json
from . import certificate
from .util import Just
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

users_db = get_collection('users')


def follow(user_id):
    print(f'followed by {user_id}')
    line_api.reply(user_id, ['こんにちは！！\n休講ボットにようこそ。', 'あなたに合わせた休講情報をお届けするには履修情報の登録が必要です。「csv」とメッセージを送ってアップロードリンクを取得してください。'])


def unfollow(user_id):
    print(f'unfollowed by {user_id}')


def message(user_id, msg_text):
    msg = msg_text.strip().lower()
    p = users_db.find_one({"connections.line.user_id": user_id})
    next_msg_type = Just(p).connections.line.next_msg_type()
    if next_msg_type == 'mail_addr':
        users_db.update({"connections.line.user_id": user_id}, {
            "$unset": {"connections.line.next_msg_type": None},
            "$set": {"connections.email.email_addr": msg_text}
        })
    elif msg == 'csv':
        real_user_id, token = certificate.generate_token(line_api.get_real_user_id(user_id))
        link = f'https://kyukou.shosato.jp/c/uploadcsv/?token={token}&realid={real_user_id}'
        line_api.reply(user_id, [link, 'このリンクからCSVファイルをアップロードしてください。リンクの有効期限は1時間です。以前取得したリンクは無効化されます。'])
    elif msg == 'mail':
        users_db.update({"connections.line.user_id": user_id}, {"$set": {"connections.line.next_msg_type": 'mail_addr'}})
        line_api.reply(user_id, ['メールアドレスを入力してください'])
    else:
        line_api.reply(user_id, [msg_text])
