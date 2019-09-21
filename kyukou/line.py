import re
import time
from .db import get_collection
from . import line_api
import json
from . import certificate
from .util import Just
import sys
import codecs
from .procedure import Procedure, ProcedureSelector, process
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

users_db = get_collection('users')


def follow(user_id):
    print(f'followed by {user_id}')
    line_api.reply(user_id, ['こんにちは！！\n休講ボットにようこそ。', 'あなたに合わせた休講情報をお届けするには履修情報の登録が必要です。「csv」とメッセージを送ってアップロードリンクを取得してください。'])


def unfollow(user_id):
    print(f'unfollowed by {user_id}')


email_procedure = Procedure(lambda user_id, msg_text: msg_text == 'mail')
@process(email_procedure, 0)
def please_enter_email(user_id, msg_text):
    line_api.reply(user_id, ['メールアドレスを入力してください'])
    email_procedure.set_progress(user_id, 0)


@process(email_procedure, 1)
def validate_email(user_id, msg_text):
    if re.match('.*@.*', msg_text):
        line_api.reply(user_id, ['メールアドレスを登録しました。'])
        email_procedure.set_progress(user_id, 1)
    else:
        line_api.reply(user_id, ['メールアドレスの書式が間違っています。もう一度入力してください'])
        email_procedure.set_progress(user_id, 0)


ps = ProcedureSelector([email_procedure])

def message(user_id, msg_text):
    msg = msg_text.strip().lower()
    if msg == 'end':
        ps.end(user_id)
        return
    if ps.run(user_id, msg):
        return
    p = users_db.find_one({"connections.line.user_id": user_id})
    if msg == 'csv':
        real_user_id, token = certificate.generate_token(line_api.get_real_user_id(user_id))
        link = f'https://kyukou.shosato.jp/c/uploadcsv/?token={token}&realid={real_user_id}'
        line_api.reply(user_id, [link, 'このリンクからCSVファイルをアップロードしてください。リンクの有効期限は1時間です。以前取得したリンクは無効化されます。'])
    else:
        line_api.reply(user_id, [msg_text])
