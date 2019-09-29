#%%
# from .db import Db
import datetime
from pprint import pprint
import pandas as pd

#%%
# users_list=Db.get_users_db()
# lectures_=Db.get_lectures_db()

#%%
users_list = [{
    "_id": "1",
    "connections": {
        "line": {
            "user_id": "Uc2f8ef784a2ad05",
            "follow_time": 1569421368.1030498,
            "display_name": "しょう",
            "status_message": "hoge",
            "last_message_time": 1569454268.465282
        },
        "length": 3,
        "email": {
            "email_addr": "shosatojp2001@gmail.com",
            "referrer": "line",
            "verified": "true"
        },
        "google": {
            "email": "shosatojp2001@gmail.com",
            "name": "佐藤翔",
            "given_name": "翔",
            "family_name": "佐藤",
            "locale": "ja",
        }
    },
    "lectures": [
        {
            "periods": [
                1,
                2
            ],
            "dayofweek": 3,
            "teachers": "千葉"
        },
        {
            "periods": [2],
            "dayofweek": 2,
            "teachers": "くとう・りくな 雄一"
        }
    ],
    "notifies": [
        {
            # 講義日の朝0時が基準
            "type": "day",
            "offset": -7200
        },
        {
            # 講義時間が基準
            "type": "lecture",
            "offset": -3600
        },
        {
            # 休講情報を見つけた時間が基準 即時
            "type": "scraping",
            "offset": 0
        }
    ]
},
{
    "_id": "2",
    "connections": {
        "line": {
            "user_id": "Uc2f8ef784a2ad05",
            "follow_time": 1569421368.1030498,
            "display_name": "しょう",
            "status_message": "hoge",
            "last_message_time": 1569454268.465282
        },
        "length": 3,
        "email": {
            "email_addr": "shosatojp2001@gmail.com",
            "referrer": "line",
            "verified": "true"
        },
        "google": {
            "email": "shosatojp2001@gmail.com",
            "name": "佐藤翔",
            "given_name": "翔",
            "family_name": "佐藤",
            "locale": "ja",
        }
    },
    "lectures": [
        {
            "periods": [
                3
            ],
            "dayofweek": 1,
            "teachers": "りくな 雄一"
        }
    ],
    "notifies": [
        {
            # 講義日の朝0時が基準
            "type": "day",
            "offset": -7200
        },
        {
            # 講義時間が基準
            "type": "lecture",
            "offset": -3600
        },
        {
            # 休講情報を見つけた時間が基準 即時
            "type": "scraping",
            "offset": 0
        }
    ]
},
{
    "_id": "3",
    "connections": {
        "line": {
            "user_id": "Uc2f8ef784a2ad05",
            "follow_time": 1569421368.1030498,
            "display_name": "しょう",
            "status_message": "hoge",
            "last_message_time": 1569454268.465282
        },
        "length": 3,
        "email": {
            "email_addr": "shosatojp2001@gmail.com",
            "referrer": "line",
            "verified": "true"
        },
        "google": {
            "email": "shosatojp2001@gmail.com",
            "name": "佐藤翔",
            "given_name": "翔",
            "family_name": "佐藤",
            "locale": "ja",
        }
    },
    "lectures": [
        {
            "periods": [2],
            "dayofweek": 2,
            "teachers": "くとう"
        }
    ],
    "notifies": [
        {
            # 講義日の朝0時が基準
            "type": "day",
            "offset": -7200
        },
        {
            # 講義時間が基準
            "type": "lecture",
            "offset": -3600
        },
        {
            # 休講情報を見つけた時間が基準 即時
            "type": "scraping",
            "offset": 0
        }
    ]
}]

#%%
lectures_list = [{
    "_id":"5d89a8fafa3e02f3fe8102ac",
    "date":1570028400,
    "teachers":"千葉",
    "periods":[1, 2, 3],
    "class":"2年昼",
    "subject":"中国語運用演習",
    "remark":"",
    "hash":"6f4179738fbf83f4b7009736a39cf0f43a7a94d18f960a21123bc014dea22f6e"
},
{
    "_id":"5d89a8fafa3e02f3fe8102ac",
    "date":1570028400-86400,
    "teachers":"○くとう・りくな(雄)",
    "periods":[1, 2, 3],
    "class":"2年昼",
    "subject":"中国語運用演習",
    "remark":"",
    "hash":"6f4179738fbf83f4b7009736a39cf0f43a7a94d18f960a21123bc014dea22f6e"
},
{
    "_id":"5d89a8fafa3e02f3fe8102ac",
    "date":1570028400-86400*2,
    "teachers":"りくな(雄)",
    "periods":[1, 2, 3],
    "class":"2年昼",
    "subject":"中国語運用演習",
    "remark":"",
    "hash":"6f4179738fbf83f4b7009736a39cf0f43a7a94d18f960a21123bc014dea22f6e"
}]

#%%
weekday = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
period = {1:datetime.timedelta(hours=9), 2:datetime.timedelta(hours=10, minutes=40), 3:datetime.timedelta(hours=13), 4:datetime.timedelta(hours=14, minutes=40), 5:datetime.timedelta(hours=16, minutes=15)}
#%%
# users_dict = users_db.find({})
# lectures_dict = lectures_list.find({})

def notify_func(line_user_id, notifies, msg_texts=[]):
    # line_api.push(line_user_id,msg_texts)
    print(f'Notify for "{line_user_id}"', end="")
    for msg_text in msg_texts:
        print(msg_text)
    for notify in notifies:
        print(f'type: {notify["type"]}, offset:{notify["offset"]}')
    print("")


#%%
def make_dict(scraping_hash, message, end, dest, user_id, time):
    output_dict = {
        "hash": scraping_hash,
        "message": message,
        "end": end,
        "dest": dest,
        "user_id": user_id,
        "time": time
    }
    return output_dict

#%%
def make_notification_dict():
    for user in users_list:
        user_lectures = user["lectures"]
        for canceled_lecture in sorted(lectures_list, key=lambda x: x["date"]):
            for user_lecture in user_lectures:
                # 受講科目の時限と休講科目の時限の積集合
                periods = set(user_lecture["periods"]) & set(canceled_lecture["periods"])
                # 休講科目からdatetimeオブジェクトを作成
                date = datetime.date.fromtimestamp(canceled_lecture["date"])
                # 休講科目のdatetimeオブジェクトから曜日を作る
                dayofweek = date.weekday()
                # 受講科目と休講科目の曜日の判定
                dayofweek = user_lecture["dayofweek"] == dayofweek
                # 受講科目と休講科目の教員の判定
                teachers = user_lecture["teachers"].replace("○", "").replace("（", "(").replace("）", ")").split("・")
                teachers_list = []
                for teacher in teachers:
                    if " " in teacher:
                        tmp = teacher.split(" ")
                        tmp2 = "(" + tmp[1][0] + ")"
                        teacher = tmp[0] + tmp2
                    teachers_list.append(teacher)
                teachers = set(teachers_list) & set(canceled_lecture["teachers"].replace("○", "").replace("（", "(").replace("）", ")").split("・")) or False
                if periods and dayofweek and teachers:
                    # ○月○日に変更
                    msg_texts_date = date.strftime('%m月%d日'.encode('unicode-escape').decode()).encode().decode("unicode-escape")
                    # 曜日を取り出す
                    msg_texts_weekday = weekday[date.weekday()][0]
                    # periods(積集合)を「・」でくっつける
                    msg_texts_periods = "・".join((map(str, periods)))
                    # 科目名
                    msg_texts_subject = canceled_lecture["subject"]
                    # 教員名
                    msg_texts_teachers = user_lecture["teachers"]
                    # 備考
                    msg_texts_remark = canceled_lecture["remark"] or "無し"
                    # notifyのリスト
                    notify_list = user["notifies"]
                    scraping_hash = canceled_lecture["hash"]
                    message = f"""【休講情報】
    月日: {msg_texts_date}({msg_texts_weekday})
    時限: {msg_texts_periods}
    科目: {msg_texts_subject}
    教員: {msg_texts_teachers}
    備考: {msg_texts_remark}"""
                    end = datetime.datetime.timestamp(datetime.datetime.combine(date, datetime.time()) + period[min(periods)])
                    dest = "ほげ"
                    user_id = user["_id"]
                    for notify_dict in notify_list:
                        if notify_dict["type"] == "day":
                            notify_day = datetime.datetime.combine(date, datetime.time()) + datetime.timedelta(seconds=notify_dict["offset"])
                            time_day = datetime.datetime.timestamp(notify_day)
                            make_dict(scraping_hash, message, end, dest, user_id,time_day)
                        if notify_dict["type"] == "lecture":
                            notify_lecture = datetime.datetime.combine(date, datetime.time()) + period[min(periods)] + datetime.timedelta(seconds=notify_dict["offset"])
                            time_lecture = datetime.datetime.timestamp(notify_lecture)
                            make_dict(scraping_hash, message, end, dest, user_id, time_lecture)
                        if notify_dict["type"] == "scraping":
                            time_scraping = "スクレイピングした時間"
                            make_dict(scraping_hash, message, end, dest, user_id, time_scraping)