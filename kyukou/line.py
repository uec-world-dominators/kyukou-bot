from bson.objectid import ObjectId
from . import user_data
from . import publish
from .util import log
import traceback
from . import util
from . import scheduler
from . import email_api
import json
import re
import time
import sys
import codecs
from datetime import datetime
isinpackage = not __name__ in ['line', '__main__']

if isinpackage:
    from . import notify
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

if hasattr(sys.stdout, 'detach'):
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def follow(user_id):
    print(f'followed by {user_id}')
    real_user_id = line_api.get_real_user_id(user_id)
    token = certificate.generate_token(real_user_id, 'csv_upload', {'referrer': 'line'})
    link = f'{settings.url_prefix()}/c/uploadcsv/?token={token}&realid={real_user_id}'
    line_api.reply(user_id, [
        'こんにちは！！\n休講ボットにようこそ。',
        'あなたに合わせた休講情報をお届けするには履修情報の登録が必要です。',
        link,
        'このリンクからCSVファイルをアップロードしてください。リンクの有効期限は1時間です。'
    ])


def unfollow(user_id):
    log(__name__, f'unfollowed by {user_id}')


csv_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'csv', 'csv')


@process(csv_procedure, 0)
def reply_csv_upload_link(user_id, msg_text):
    real_user_id = line_api.get_real_user_id(user_id)
    token = certificate.generate_token(real_user_id, 'csv_upload', {'referrer': 'line'})
    link = f'{settings.url_prefix()}/c/uploadcsv/?token={token}&realid={real_user_id}'
    line_api.reply(user_id, [link, 'このリンクからCSVファイルをアップロードしてください。リンクの有効期限は1時間です。以前取得したリンクは無効化されます。'])
    csv_procedure.set_progress(user_id, 0)


time_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'time', 'time')


@process(time_procedure, 0)
def validate_input(user_id, msg_text):
    line_api.reply(user_id, ['通知の形式を選択し、対応する「数字」を入力してください。\n'
                             + '【 1 】休講情報を見つけたら即時通知する\n'
                             + '【 2 】休講日の何日前、何時間前など、通知時間を細かく設定する\n'
                             + '尚、この通知設定は複数追加できます。'])
    time_procedure.set_progress(user_id, 0)


@process(time_procedure, 1)
def validate_num(user_id, msg_text):
    if msg_text == '1':
        realid = line_api.get_real_user_id(user_id)
        if notify.add_notify(realid, {'type': 'scraping', 'offset': 0, 'dest': 'line'}):
            publish.remove_queue(realid)
            line_api.reply(user_id, ['登録完了です。休講情報を見つけたらすぐ通知します。'])
        else:
            line_api.reply(user_id, ['通知が最大数10に達したか、すでに同じものがあるため追加できません'])
        time_procedure.set_progress(user_id, 3)
    elif msg_text == '2':
        line_api.reply(user_id, ['休講の何日前に通知しますか？\n当日の場合は【 0 】"、前日の場合は【 1 】、2日前の場合は【 2 】...のように入力してください。'])
        time_procedure.set_progress(user_id, 1)
    else:
        line_api.reply(user_id, ['数値の形式が間違っています。もう一度入力してください。'])
        time_procedure.set_progress(user_id, 0)


@process(time_procedure, 2)
def please_enter_time(user_id, msg_text):
    m = re.match(r'^(\d{1,2})$', msg_text)
    if m:
        d = int(m.group(1))
        if 0 <= d <= 30:
            time_procedure.set_info(user_id, 'day', d)
            line_api.reply(user_id, ['その日の何時に通知しますか？\n"6:30"、"23:00"のように"時:分"となるよう24時間表記で送信してください。'])
            time_procedure.set_progress(user_id, 2)
            return
    line_api.reply(user_id, ['数値の形式が間違っています。もう一度入力してください。'])
    time_procedure.set_progress(user_id, 1)


@process(time_procedure, 3)
def validate_time(user_id, msg_text):
    try:
        dayoffset = time_procedure.get_info(user_id).get('day', 0)
        time_data = datetime.strptime(msg_text, '%H:%M')
        realid = line_api.get_real_user_id(user_id)
        if notify.add_notify(realid, {'type': 'day', 'offset': notify.day_hour_minute_to_day_offset(dayoffset, time_data.hour, time_data.minute), 'dest': 'line'}):
            publish.remove_queue(realid)
            line_api.reply(user_id, ['通知時間を登録しました。'])
        else:
            line_api.reply(user_id, ['通知が最大数10に達したか、すでに同じものがあるため追加できません'])
        time_procedure.set_progress(user_id, 3)
    except ValueError:
        line_api.reply(user_id, ['数値の形式が間違っています。もう一度入力してください'])
        time_procedure.set_progress(user_id, 2)
    except:
        log(__name__, traceback.format_exc())
        line_api.reply(user_id, ['不明なエラーが発生しました。申し訳ありませんが、最初からやり直してください。'])
        time_procedure.set_progress(user_id, 3)


line_notify_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'notify', 'notify')


@process(line_notify_procedure, 0)
def get_line_notify_link(user_id, msg_text):
    line_api.reply(user_id, [line_notify_api.get_redirect_link(line_api.get_real_user_id(user_id)), 'このリンクからLINE Notifyの連携を行ってください！'])
    line_notify_procedure.set_progress(user_id, 0)


google_oauth_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'google', 'google')
@process(google_oauth_procedure, 0)
def redirect_to_google_auth(user_id, msg_text):
    line_api.reply(user_id, [google_api.get_redirect_link(line_api.get_real_user_id(user_id))])


status_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'status', 'status')


@process(status_procedure, 0)
def display_status(user_id, msg_text):
    s = notify.format_notifies(line_api.get_real_user_id(user_id))
    if s:
        line_api.reply(user_id, ['通知の登録情報を表示します。', s])
    else:
        line_api.reply(user_id, ['通知は設定されていません', '【time】と入力して設定してください'])
    status_procedure.set_progress(user_id, 0)


delete_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'delete', 'delete')


@process(delete_procedure, 0)
def delete_status(user_id, msg_text):
    s = notify.format_notifies(line_api.get_real_user_id(user_id))
    if s:
        line_api.reply(user_id, ['削除する番号を入力してください', s])
        delete_procedure.set_progress(user_id, 0)
    else:
        line_api.reply(user_id, ['通知は設定されていません'])
        delete_procedure.set_progress(user_id, 1)


@process(delete_procedure, 1)
def delete_notify(user_id, msg_text):
    try:
        realid = line_api.get_real_user_id(user_id)
        if 1 <= int(msg_text) <= len(notify.get_notifies(realid)):
            notify.delete_notify(realid, int(msg_text))
            line_api.reply(user_id, ['削除しました'])
            delete_procedure.set_progress(user_id, 1)
        else:
            line_api.reply(user_id, ['正しく入力してください'])
            delete_procedure.set_progress(user_id, 0)
    except:
        line_api.reply(user_id, ['正しく入力してください'])
        delete_procedure.set_progress(user_id, 0)


request_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'request', 'request')


@process(request_procedure, 0)
def get_request(user_id, msg_text):
    line_api.reply(user_id, ['このサービスに関して、何か要望があれば入力してください。やめるには【end】と入力します'])
    request_procedure.set_progress(user_id, 0)


@process(request_procedure, 1)
def send_request(user_id, msg_text):
    realid = line_api.get_real_user_id(user_id)
    msg = email_api.make_message(settings.admin_email_addr(), '【ご注文は休講情報ですか？】ユーザーからの問い合わせ', f'<h1>REAL_USER_ID={realid}, REF=LINE</h1><p>{msg_text}</p><p></p>')
    scheduler.pool.submit(email_api.send_mails, [msg])
    line_api.reply(user_id, ['ご協力ありがとうございました。'])
    request_procedure.set_progress(user_id, 1)


help_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'help', 'help')


@process(help_procedure, 0)
def display_help(user_id, msg_text):
    line_api.reply(user_id, ['電気通信大学・「個別配信型」休講情報ボット\n'
                             + f'{settings.url_prefix()}/#/\n\n'
                             + 'コマンドの一覧を表示します。以下のコマンドを送信することで対話的に設定できます。\n'
                             + '【csv】 : 履修登録のCSVファイルのアップロードリンクを取得します。\n'
                             + '【time】 : 休講の通知時間を設定します。\n'
                             + '【status】 : 設定した休講の通知時間の一覧を表示します。\n'
                             + '【delete】 : 設定した休講の通知時間を削除します。\n'
                             + '【notify】 : 休講情報の配信に使うLINE Notifyの連携を行います。\n'
                             + '【request】 : 運営に何か要望を送ることができます。\n'
                             + '【help】 : トークで使えるコマンドの一覧を表示します。\n'
                             + '【end】 : 上記のすべてのコマンドを終了させます。'])
    help_procedure.set_progress(user_id, 0)


cources_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'cources' or msg_text == 'cource', 'cources')


@process(cources_procedure, 0)
def get_request(user_id, msg_text):
    realid = line_api.get_real_user_id(user_id)
    line_api.reply(user_id, ['登録されている履修科目の一覧です', user_data.list_of_courses(realid)])
    cources_procedure.set_progress(user_id, 0)


ps = ProcedureSelectorDB(
    csv_procedure,
    time_procedure,
    line_notify_procedure,
    status_procedure,
    delete_procedure,
    help_procedure,
    request_procedure,
    cources_procedure
)


def message(user_id, msg_text):
    msg = msg_text.strip().lower().translate(util.trans)
    if msg == 'end':
        ps.end(user_id)
        return
    if ps.run(user_id, msg):
        return
    line_api.reply(user_id, [msg_text])
