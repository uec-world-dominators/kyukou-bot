#%%
# from .db import Db
import datetime
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
            "teachers": "りくな"
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
    "teachers":"くとう",
    "periods":[1, 2, 3],
    "class":"2年昼",
    "subject":"中国語運用演習",
    "remark":"",
    "hash":"6f4179738fbf83f4b7009736a39cf0f43a7a94d18f960a21123bc014dea22f6e"
},
{
    "_id":"5d89a8fafa3e02f3fe8102ac",
    "date":1570028400-86400*2,
    "teachers":"りくな",
    "periods":[1, 2, 3],
    "class":"2年昼",
    "subject":"中国語運用演習",
    "remark":"",
    "hash":"6f4179738fbf83f4b7009736a39cf0f43a7a94d18f960a21123bc014dea22f6e"
}]

#%%
weekday = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
#%%
# users_dict = users_db.find({})
# lectures_dict = lectures_list.find({})

def notify(line_user_id,msg_texts=[]):
    # line_api.push(line_user_id,msg_texts)
    print(f'Notify for "{line_user_id}"')
    for msg_text in msg_texts:
        print(msg_text)
    # print(f'Notify for "{line_user_id}"',msg_texts)

#%%
for user in users_list:
    user_lectures = user["lectures"]
    msg_texts = []
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
            teachers = user_lecture["teachers"] == canceled_lecture["teachers"]
            # print(periods, dayofweek, teachers)
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
                # msg_textsに追加
                msg_texts.append(
                    f"""
【休講情報】
月日: {msg_texts_date}({msg_texts_weekday})
時限: {msg_texts_periods}
科目: {msg_texts_subject}
教員: {msg_texts_teachers}
備考: {msg_texts_remark}""")
    notify(user["_id"], msg_texts)



# #%%
# import pandas as pd
# a = pd.read_csv("RSReferCsv.csv", encoding="ANSI", names=[i for i in range(7)], dtype="object")
# a = a.drop([i for i in range(4)], axis=0)
# a = a.drop([i for i in range(26, a.index.max()+1)])
# a.columns = a.iloc[0, :]
# a.drop(4, axis=0)
# a
# index = []
# a
# #%%
# for i in range(1, 8):
#     index.append("{}限_科目名".format(i))
#     index.append("{}限_教員名".format(i))
# time_table = pd.DataFrame(columns=[i for i in range(0, 7)], index=index)
# time_table