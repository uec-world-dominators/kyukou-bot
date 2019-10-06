import json
import re
import time
import sys
import codecs
from datetime import datetime
isinpackage = not __name__ in ['line', '__main__']

if isinpackage:
    from . import line_api
    from . import google_api
    from . import line_notify_api
    from . import certificate
    from . import email_api
    from .db import get_collection
    from .util import Just
    from .settings import settings
    from .procedure import *
    users_db = get_collection('users')
else:
    from procedure import *
    import line_api

if hasattr(sys.stdout, 'detach'):
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def follow(user_id):
    print(f'followed by {user_id}')
    line_api.reply(user_id, [
        'こんにちは！！\n休講ボットにようこそ。',
        'あなたに合わせた休講情報をお届けするには履修情報の登録が必要です。「csv」とメッセージを送ってアップロードリンクを取得してください。',
    ])


def unfollow(user_id):
    print(f'unfollowed by {user_id}')


if isinpackage:
    csv_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'csv', 'csv')
else:
    csv_procedure = Procedure(lambda user_id, msg_text: msg_text == 'csv', 'csv')


@process(csv_procedure, 0)
def reply_csv_upload_link(user_id, msg_text):
    real_user_id = line_api.get_real_user_id(user_id)
    token = certificate.generate_token(real_user_id, 'csv_upload', {'referrer': 'line'})
    link = f'{settings.url_prefix()}/c/uploadcsv/?token={token}&realid={real_user_id}'
    line_api.reply(user_id, [link, 'このリンクからCSVファイルをアップロードしてください。リンクの有効期限は1時間です。以前取得したリンクは無効化されます。'])
    csv_procedure.set_progress(user_id, 0)


if isinpackage:
    email_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'mail', 'mail')
else:
    email_procedure = Procedure(lambda user_id, msg_text: msg_text == 'mail', 'mail')


@process(email_procedure, 0)
def please_enter_email(user_id, msg_text):
    line_api.reply(user_id, ['メールアドレスを入力してください'])
    email_procedure.set_progress(user_id, 0)


@process(email_procedure, 1)
def validate_email(user_id, msg_text):
    if re.match('.*@.*', msg_text):
        real_user_id = line_api.get_real_user_id(user_id)
        link = f'{settings.url_prefix()}/api/v1/line/email/?token={certificate.generate_token(real_user_id, "line_email",{"email_addr":msg_text})}&realid={real_user_id}'
        email_api.send_mails([email_api.make_message(msg_text, '【ご注文は休講情報ですか？】メールアドレスの確認', '<h1>メールアドレスを検証するために以下のリンクをクリックしてください。</h1><p>このメールに心当たりが無い場合はリンクをクリックしないでください。</p>'+link)])
        line_api.reply(user_id, [f'入力されたメールアドレスを検証するために、{msg_text}にメールを送信しました。ご確認ください。'])
        email_procedure.set_progress(user_id, 1)
    else:
        line_api.reply(user_id, ['メールアドレスの書式が間違っています。もう一度入力してください'])
        email_procedure.set_progress(user_id, 0)


if isinpackage:
    time_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'time', 'time')
else:
    time_procedure = Procedure(lambda user_id, msg_text: msg_text == 'time', 'time')

@process(time_procedure, 0)
def add_notice(user_id, msg_text):
    line_api.reply(user_id, ['通知時間を追加しますか？追加する場合は"y"、終了する場合は"end"と入力してください。'])
    time_procedure.set_progress(user_id, 0)

@process(time_procedure, 1)
def validate_input(user_id, msg_text): 
    if msg_text == 'y':
        time_procedure.set_progress(user_id, 1)
    else:
        line_api.reply(user_id, ['入力が間違っています。もう一度入力してください。'])
        time_procedure.set_progress(user_id, 0)

@process(time_procedure, 2)
def select_notice_time(user_id, msg_text):
    line_api.reply(user_id, ['通知の形式を選択し、対応する数字を入力してください。\n\
        ・休講情報を見つけたら即時通知する: 1 \n\
            ・休講日の何日前、何時間前など、通知時間を細かく設定する: 2\
                尚、この通知設定は複数追加できます。'])
    time_procedure.set_progress(user_id, 2)

#process4かprocess11に分岐
@process(time_procedure, 3)
def validate_num(usr_id, msg_text):
    if msg_text == '1':
        time_procedure.set_progress(user_id, 10)
    elif msg_text == '2':
        time_procedure.set_progress(user_id, 3)
    else:
        line_api.reply(user_id, ['数値の形式が間違っています。もう一度入力してください。なお、全角数字は対応しておりません。'])
        time_procedure.set_progress(user_id, 2)

@process(time_procedure, 4)
def please_enter_day(user_id, msg_text):
    line_api.reply(user_id, ['休講の何日前に通知しますか？\n当日の場合は"0"、前日の場合は"1"、2日前の場合は"2"...のように入力してください。'])
    time_procedure.set_progress(user_id, 4)

@process(time_procedure, 5)
def please_enter_time(user_id, msg_text):
    if re.match("\d*", msg_text):
        line_api.reply(user_id, ['その日の何時に通知しますか？\n"6:30"、"23:00"のように"時:分"となるよう24時間表記で送信してください。'])
        time_procedure.set_info(user_id, 'day', msg_text)
        time_procedure.set_progress(user_id, 5)
    else:
        line_api.reply(user_id, ['数値の形式が間違っています。もう一度入力してください。なお、全角数字は対応しておりません。'])
        email_procedure.set_progress(user_id, 4)

@process(time_procedure, 6)
def validate_time(user_id, msg_text):
    try:
        time_data = datetime.strptime(msg_text, '%H:%M')
        line_api.reply(user_id, ['通知時間を登録しました。'])
        time_procedure.set_progress(user_id, 6)
    except ValueError:
        line_api.reply(user_id, ['数値の形式が間違っています。もう一度入力してください。なお、全角数字は対応しておりません。'])
        time_procedure.set_progress(user_id, 5)
    except:
        line_api.reply(user_id, ['不明なエラーが発生しました。申し訳ありませんが、最初からやり直してください。'])
        ps.end(user_id)

#分岐先のprocess11
@process(time_procedure, 11)
def kyuko_soku_tsuchi(user_id, msg_text):
    line_api.reply(user_id, ['登録完了です。休講情報を見つけたらすぐ通知します。'])


line_notify_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'notify', 'notify')


@process(line_notify_procedure, 0)
def get_line_notify_link(user_id, msg_text):
    line_api.reply(user_id, [line_notify_api.get_redirect_link(line_api.get_real_user_id(user_id)), 'このリンクからLINE Notifyの連携を行ってください！'])
    line_notify_procedure.set_progress(user_id, 0)


google_oauth_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'google','google')
@process(google_oauth_procedure, 0)
def redirect_to_google_auth(user_id, msg_text):
    line_api.reply(user_id, [google_api.get_redirect_link(line_api.get_real_user_id(user_id))])


def message(user_id, msg_text):
    msg = msg_text.strip().lower()
    if msg == 'end':
        ps.end(user_id)
        return
    if ps.run(user_id, msg):
        return
    line_api.reply(user_id, [msg_text])
    line_notify_api.send(line_api.get_real_user_id(user_id), msg_text)


if isinpackage:
    ps = ProcedureSelectorDB(email_procedure, csv_procedure, time_procedure, line_notify_procedure,google_oauth_procedure)
else:
    ps = ProcedureSelector(email_procedure, csv_procedure, time_procedure, line_notify_procedure)
    # ここでデバッグ
    ps.run('me', 'time')
    ps.run('me', '0')
    ps.run('me', '2:00')
