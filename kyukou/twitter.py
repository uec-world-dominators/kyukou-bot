from . import scheduler
from .log import log
from datetime import datetime
import traceback
import re
from . import notify
from . import util
from . import twitter_api
from .db import get_collection
from . import google_api
from . import certificate
from .util import Just
from . import email_api
from .settings import settings
from .procedure import *
from . import publish
from . import user_data
csv_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'csv', 'twitter_csv')


@process(csv_procedure, 0)
def reply_csv_upload_link(user_id, msg_text):
    real_user_id = twitter_api.get_real_user_id(user_id)
    token = certificate.generate_token(real_user_id, 'csv_upload', {'referrer': 'twitter'})
    link = f'{settings.url_prefix()}/c/uploadcsv/?token={token}&realid={real_user_id}'
    twitter_api.send(user_id, link)
    twitter_api.send(user_id, 'このリンクからCSVファイルをアップロードしてください。リンクの有効期限は1時間です。以前取得したリンクは無効化されます。')
    csv_procedure.set_progress(user_id, 0)


time_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'time', 'twitter_time')


@process(time_procedure, 0)
def validate_input(user_id, msg_text):
    twitter_api.sends(user_id, ['通知の形式を選択し、対応する「数字」を入力してください。\n'
                                + '【 1 】休講情報を見つけたら即時通知する\n'
                                + '【 2 】休講日の何日前、何時間前など、通知時間を細かく設定する\n'
                                + '尚、この通知設定は複数追加できます。'])
    time_procedure.set_progress(user_id, 0)


@process(time_procedure, 1)
def validate_num(user_id, msg_text):
    if msg_text == '1':
        realid=twitter_api.get_real_user_id(user_id)
        if notify.add_notify(realid, {'type': 'scraping', 'offset': 0, 'dest': 'twitter'}):
            publish.remove_queue(realid)
            twitter_api.sends(user_id, ['登録完了です。休講情報を見つけたらすぐ通知します。'])
        else:
            twitter_api.sends(user_id, ['通知が最大数10に達したか、すでに同じものがあるため追加できません'])
        time_procedure.set_progress(user_id, 3)
    elif msg_text == '2':
        twitter_api.sends(user_id, ['休講の何日前に通知しますか？\n当日の場合は【 0 】"、前日の場合は【 1 】、2日前の場合は【 2 】...のように入力してください。'])
        time_procedure.set_progress(user_id, 1)
    else:
        twitter_api.sends(user_id, ['数値の形式が間違っています。もう一度入力してください。'])
        time_procedure.set_progress(user_id, 0)


@process(time_procedure, 2)
def please_enter_time(user_id, msg_text):
    m = re.match(r'^(\d{1,2})$', msg_text)
    if m:
        d = int(m.group(1))
        if 0 <= d <= 30:
            time_procedure.set_info(user_id, 'day', d)
            twitter_api.sends(user_id, ['その日の何時に通知しますか？\n"6:30"、"23:00"のように"時:分"となるよう24時間表記で送信してください。'])
            time_procedure.set_progress(user_id, 2)
            return
    twitter_api.sends(user_id, ['数値の形式が間違っています。もう一度入力してください。'])
    time_procedure.set_progress(user_id, 1)


@process(time_procedure, 3)
def validate_time(user_id, msg_text):
    try:
        dayoffset = time_procedure.get_info(user_id).get('day', 0)
        time_data = datetime.strptime(msg_text, '%H:%M')
        realid=twitter_api.get_real_user_id(user_id)
        if notify.add_notify(realid, {'type': 'day', 'offset': notify.day_hour_minute_to_day_offset(dayoffset, time_data.hour, time_data.minute), 'dest': 'twitter'}):
            publish.remove_queue(realid)
            twitter_api.sends(user_id, ['通知時間を登録しました。'])
        else:
            twitter_api.sends(user_id, ['通知が最大数10に達したか、すでに同じものがあるため追加できません'])
        time_procedure.set_progress(user_id, 3)
    except ValueError:
        twitter_api.sends(user_id, ['数値の形式が間違っています。もう一度入力してください'])
        time_procedure.set_progress(user_id, 2)
    except:
        log(__name__, traceback.format_exc(),4)
        twitter_api.sends(user_id, ['不明なエラーが発生しました。申し訳ありませんが、最初からやり直してください。'])
        time_procedure.set_progress(user_id, 2)


google_oauth_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'google', 'twitter_google')
@process(google_oauth_procedure, 0)
def redirect_to_google_auth(user_id, msg_text):
    twitter_api.sends(user_id, [google_api.get_redirect_link(twitter_api.get_real_user_id(user_id))])


status_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'status', 'twitter_status')


@process(status_procedure, 0)
def display_status(user_id, msg_text):
    s = notify.format_notifies(twitter_api.get_real_user_id(user_id))
    if s:
        twitter_api.sends(user_id, ['通知の登録情報を表示します。', s])
    else:
        twitter_api.sends(user_id, ['通知は設定されていません', '【time】と入力して設定してください'])
    status_procedure.set_progress(user_id, 0)


delete_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'delete', 'delete')


@process(delete_procedure, 0)
def delete_status(user_id, msg_text):
    s = notify.format_notifies(twitter_api.get_real_user_id(user_id))
    if s:
        twitter_api.sends(user_id, ['削除する番号を入力してください', s])
        delete_procedure.set_progress(user_id, 0)
    else:
        twitter_api.sends(user_id, ['通知は設定されていません'])
        delete_procedure.set_progress(user_id, 1)

import re
@process(delete_procedure, 1)
def delete_notify(user_id, msg_text):
    try:
        realid=twitter_api.get_real_user_id(user_id)
        if 1<= int(msg_text) <=len(notify.get_notifies(realid)):
            notify.delete_notify(realid, int(msg_text))
            twitter_api.sends(user_id, ['削除しました'])
            delete_procedure.set_progress(user_id, 1)
        else:
            twitter_api.sends(user_id, ['正しく入力してください'])
            delete_procedure.set_progress(user_id, 0)
    except:
        twitter_api.sends(user_id, ['正しく入力してください'])
        delete_procedure.set_progress(user_id, 0)


request_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'request', 'twitter_request')


@process(request_procedure, 0)
def get_request(user_id, msg_text):
    twitter_api.sends(user_id, ['このサービスに関して、何か要望があれば入力してください。やめるには【end】と入力します'])
    request_procedure.set_progress(user_id, 0)


@process(request_procedure, 1)
def send_request(user_id, msg_text):
    msg = email_api.make_message(settings.admin_email_addr(), '【ご注文は休講情報ですか？】ユーザーからの問い合わせ', f'<h1>REAL_USER_ID={twitter_api.get_real_user_id(user_id)}, REF=TWITTER</h1><p>{msg_text}</p>')
    scheduler.pool.submit(email_api.send_mails, [msg])
    twitter_api.sends(user_id, ['ご協力ありがとうございました。'])
    request_procedure.set_progress(user_id, 1)


help_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'help', 'twitter_help')


@process(help_procedure, 0)
def display_help(user_id, msg_text):
    twitter_api.sends(user_id, ['電気通信大学・「個別配信型」休講情報ボット\n'
                                + f'{settings.url_prefix()}/#/\n\n'
                                + 'コマンドの一覧を表示します。以下のコマンドを送信することで対話的に設定できます。\n'
                                + '【csv】 : 履修登録のCSVファイルのアップロードリンクを取得します。\n'
                                + '【time】 : 休講の通知時間を設定します。\n'
                                + '【status】 : 設定した休講の通知時間の一覧を表示します。\n'
                                + '【delete】 : 設定した休講の通知時間を削除します。\n'
                                + '【request】 : 運営に何か要望を送ることができます。\n'
                                + '【help】 : トークで使えるコマンドの一覧を表示します。\n'
                                + '【end】 : 上記のすべてのコマンドを終了させます。'])
    help_procedure.set_progress(user_id, 0)


cources_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'cources' or msg_text == 'cource', 'twitter_cources')

@process(cources_procedure, 0)
def get_request(user_id, msg_text):
    realid = twitter_api.get_real_user_id(user_id)
    cources=user_data.list_of_courses(realid)
    twitter_api.sends(user_id,  ['登録されている履修科目の一覧です', cources] if cources else ['登録されている履修科目はありません','【csv】と入力して履修情報のアップロードリンクを取得してください'])
    cources_procedure.set_progress(user_id, 0)

ps = ProcedureSelectorDB(
    csv_procedure,
    time_procedure,
    status_procedure,
    delete_procedure,
    help_procedure,
    request_procedure,
    cources_procedure
)



def direct_message(user_id, msg_text):
    msg = msg_text.strip().lower().translate(util.trans)
    if msg == 'end':
        ps.end(user_id)
        return
    if ps.run(user_id, msg):
        return
    twitter_api.send(user_id, msg_text)


def follow(user_id):
    print(f'Followed by {user_id}')
    twitter_api.send(user_id, 'フォローありがとうございます！！！')
    twitter_api.send(user_id, f'「csv」とメッセージを送信して、履修情報のアップロード用リンクを取得してください！ \n参考：{settings.url_prefix()}/#/how-to-upload-csv')
