from . import twitter_api
from .db import get_collection
from . import line_api
from . import google_api
from . import line_notify_api
from . import certificate
from .util import Just
from . import email_api
from .settings import settings
from .procedure import *

csv_procedure = ProcedureDB(lambda user_id, msg_text: msg_text == 'csv', 'twitter_csv')


@process(csv_procedure, 0)
def reply_csv_upload_link(user_id, msg_text):
    real_user_id = twitter_api.get_real_user_id(user_id)
    token = certificate.generate_token(real_user_id, 'csv_upload',{'referrer':'twitter'})
    link = f'{settings.url_prefix()}/c/uploadcsv/?token={token}&realid={real_user_id}'
    twitter_api.send(user_id, link)
    twitter_api.send(user_id, 'このリンクからCSVファイルをアップロードしてください。リンクの有効期限は1時間です。以前取得したリンクは無効化されます。')
    csv_procedure.set_progress(user_id, 0)


ps = ProcedureSelectorDB(csv_procedure)


def direct_message(user_id, msg_text):
    msg = msg_text.strip().lower()
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
