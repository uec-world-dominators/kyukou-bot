#%%
from .db import Db
import datetime
import pandas as pd

#%%
users_db=Db.get_users_db()
lectures_db=Db.get_lectures_db()

#%%
# users = [
#     {
#         "user_id": "091234jv094hg904jvl4389c",
#         "reply_token": "k;54bl2k46hlk25jh6l42k5j6",
#         "follow_time": 1568792293.934327,
#         "last_message_time": 1568792293.944138,
#         "lectures": [
#             {
#                 "periods": [
#                     1,
#                     2
#                 ],
#                 "dayofweek": 3,
#                 "teachers": "千葉"
#             },
#             {
#                 "periods": [
#                     3
#                 ],
#                 "dayofweek": 4,
#                 "teachers": "牧"
#             },
#             {
#                 "periods": [
#                     2
#                 ],
#                 "dayofweek": 3,
#                 "teachers": "前川"
#             },
#             {
#                 "periods": [
#                     3
#                 ],
#                 "dayofweek": 4,
#                 "teachers": "安井"
#             }
#         ],
#         "notifies": [
#             {
#                 "offset": -1440
#             }
#         ]
#     },
#     {
#         "user_id": "091234jv094hg904jvl4389c",
#         "reply_token": "k;54bl2k46hlk25jh6l42k5j6",
#         "follow_time": 1568792293.934327,
#         "last_message_time": 1568792293.944138,
#         "lectures": [
#             {
#                 "periods": [
#                     1,
#                     2
#                 ],
#                 "dayofweek": 3,
#                 "teachers": "加藤"
#             },
#             {
#                 "periods": [
#                     3
#                 ],
#                 "dayofweek": 4,
#                 "teachers": "秋田"
#             }
#         ],
#         "notifies": [
#             {
#                 "offset": -1440
#             }
#         ]
#     }
# ]

#%%
# canceled = [
#     {
#         "periods": [
#             1,
#             2
#         ],
#         "date": 20191003,
#         "teachers": "千葉",
#         "dayofweek": 4,
#         "subject": "数学",
#         "targets": "1年昼"
#     },
#     {
#         "periods": [
#             3
#         ],
#         "date": 20191004,
#         "teachers": "牧",
#         "dayofweek": 4,
#         "subject": "数学",
#         "targets": "1年昼"
#     }
# ]

#%%
for user in users_db.find({}):
    for lecture in user["lectures"]
        for canceled_lecture in lectures_db.find({}):
            periods = (set(lecture["periods"]) <= set(canceled_lecture["periods"]))
            dayofweek = (lecture["dayofweek"] == canceled_lecture["dayofweek"])
            teachers = (lecture["teachers"] == canceled_lecture["teachers"])
            if periods and dayofweek and teachers:
                return "通知"


#%%
import pandas as pd
a = pd.read_csv("RSReferCsv.csv", encoding="ANSI", names=[i for i in range(7)], dtype="object")
a = a.drop([i for i in range(4)], axis=0)
a = a.drop([i for i in range(26, a.index.max()+1)])
a.columns = a.iloc[0, :]
a.drop(4, axis=0)
a
index = []
a
#%%
for i in range(1, 8):
    index.append("{}限_科目名".format(i))
    index.append("{}限_教員名".format(i))
time_table = pd.DataFrame(columns=[i for i in range(0, 7)], index=index)
time_table