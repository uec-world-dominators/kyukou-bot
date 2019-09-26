#%%
# from .db import Db
import datetime
import pandas as pd

#%%
# users_list=Db.get_users_db()
# lectures_=Db.get_lectures_db()

#%%
users_list = [{
    "_id": "5d8b78381767e99c915e8e9f",
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
            "teachers": "○千葉"
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
    "teachers":"○千葉",
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
    print(f'Notify for "{line_user_id}"',msg_texts)

#%%
for user in users_list:
    user_lectures = user["lectures"]
    for user_lecture in user_lectures:
        msg_texts = []
        for canceled_lecture in lectures_list:
            periods = set(user_lecture["periods"]) <= set(canceled_lecture["periods"])
            dayofweek = datetime.date.fromtimestamp(canceled_lecture["date"]).weekday()
            dayofweek = user_lecture["dayofweek"] == dayofweek
            teachers = user_lecture["teachers"] == canceled_lecture["teachers"]
            print(periods, dayofweek, teachers)
            if periods and dayofweek and teachers:
                msg_texts_weekday = weekday[user_lecture["dayofweek"]]
                mapped_periods = map(str, user_lecture["periods"])
                msg_texts_lectures = "・".join(mapped_periods)
                msg_texts_teachers = user_lecture["teachers"]
                msg_texts.append(f"{msg_texts_weekday}の{msg_texts_lectures}限目({msg_texts_teachers})は休講です")
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