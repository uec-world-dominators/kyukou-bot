import re
import time
from .db import get_collection
from . import line_api
import json
from . import certificate
from .util import Just
import sys
import codecs
from . import email_api
from .procedure import Procedure, ProcedureSelector, process, ProcedureDB
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

users_db = get_collection('users')


def follow(user_id):
    print(f'followed by {user_id}')
    line_api.reply(user_id, ['こんにちは！！\n休講ボットにようこそ。', 'あなたに合わせた休講情報をお届けするには履修情報の登録が必要です。「csv」とメッセージを送ってアップロードリンクを取得してください。'])


def unfollow(user_id):
    print(f'unfollowed by {user_id}')


csv_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'csv')
@process(csv_procedure, 0)
def reply_csv_upload_link(user_id, msg_text):
    real_user_id = line_api.get_real_user_id(user_id)
    token = certificate.generate_token(real_user_id, 'csv_upload')
    link = f'https://kyukou.shosato.jp/c/uploadcsv/?token={token}&realid={real_user_id}'
    line_api.reply(user_id, [link, 'このリンクからCSVファイルをアップロードしてください。リンクの有効期限は1時間です。以前取得したリンクは無効化されます。'])


email_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'mail')
@process(email_procedure, 0)
def please_enter_email(user_id, msg_text):
    line_api.reply(user_id, ['メールアドレスを入力してください'])
    email_procedure.set_progress(user_id, 0)


@process(email_procedure, 1)
def validate_email(user_id, msg_text):
    if re.match('.*@.*', msg_text):
        real_user_id = line_api.get_real_user_id(user_id)
        link = f'https://kyukou.shosato.jp/api/v1/line/email/?token={certificate.generate_token(real_user_id, "line_email",{"email_addr":msg_text})}&realid={real_user_id}'
        print(link)
        email_api.send_mails([email_api.make_message(msg_text, '【私の休講情報】メールアドレスの確認', link)])
        line_api.reply(user_id, ['メールアドレスを登録しました。'])
        email_procedure.set_progress(user_id, 1)
    else:
        line_api.reply(user_id, ['メールアドレスの書式が間違っています。もう一度入力してください'])
        email_procedure.set_progress(user_id, 0)

##中井担当
time_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'time')
@process(time_procedure, 0)
def please_enter_day(user_id, msg_text):
    line_api.reply(user_id, ['休講の何日前に通知しますか？\n当日の場合は"0"、前日の場合は"1"、2日前の場合は"2"...のように入力してください。'])
    time_procedure.set_progress(user_id, 0)

@process(time_procedure, 1)
def please_enter_time(user_id, msg_text):
    if re.match("\d*", msg_text):
        line_api.reply(user_id, ['その日の何時に通知しますか？\n"6:30"、"23:00"のように"時:分"となるよう24時間表記で送信してください。'])
        time_procedure.set_progress(user_id, 1)
    else:
        line_api.reply(user_id, ['数値の形式が間違っています。もう一度入力してください。なお、全角数字は対応しておりません。'])
        email_procedure.set_progress(user_id, 0)

@process(time_procedure, 2)
def validate_time(user_id, msg_text):
    if re.match("\d*:\d*", msg_text):
        line_api.reply(user_id, ['通知時間を登録しました。']
        time_procedure.set_progress(user_id, 2)
    else:
        line_api.reply(user_id, ['数値の形式が間違っています。もう一度入力してください。'])
        time_procedure.set_progress(user_id, 1)


ps = ProcedureSelector(email_procedure, csv_procedure, time_procedure,)


def message(user_id, msg_text):
    msg = msg_text.strip().lower()
    if msg == 'end':
        ps.end(user_id)
        return
    if ps.run(user_id, msg):
        return
    line_api.reply(user_id, [msg_text])
