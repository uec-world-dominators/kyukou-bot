import re
import datetime
from pprint import pprint
isinpackage = not __name__ in ['search', '__main__']
if isinpackage:
    from .settings import settings
    from .user_data import default_notify_dest
    from .publish import try_add_notification
    from .db import get_collection
    from .log import log
    from .util import ldn, strip_brackets, remove_them,times_char
    from . import util
else:
    # from publish import try_add_notification
    from db import get_collection
    from log import log
    from util import ldn, strip_brackets, remove_them,times_char

weekday = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
period = {1: datetime.timedelta(hours=9), 2: datetime.timedelta(hours=10, minutes=40), 3: datetime.timedelta(hours=13),
          4: datetime.timedelta(hours=14, minutes=40), 5: datetime.timedelta(hours=16, minutes=15)}


def notify_func(line_user_id, notifies, msg_texts=[]):
    # line_api.push(line_user_id,msg_texts)
    print(f'Notify for "{line_user_id}"', end="")
    for msg_text in msg_texts:
        print(msg_text)
    for notify in notifies:
        print(f'type: {notify["type"]}, offset:{notify["offset"]}')
    print("")


def make_dict(scraping_hash, message, end, dest, user_id, time):
    output_dict = {
        "hash": scraping_hash,
        "message": message,
        "end": end,
        "dest": dest,
        "user_id": user_id,
        "time": time
    }
    try_add_notification(output_dict)


def teachers_similarity(x, y):
    def normarize(x):
        x = x.translate(util.trans)
        x = strip_brackets(x)
        x = x.lower()
        x = re.sub(r'(・|○|　)', ' ', x)
        x = x.strip()
        x = x.replace('  ', ' ')
        return x
    x, y = normarize(x).split(' '), normarize(y).split(' ')
    return int(not not set(x) & set(y))


def subject_similarity(x, y):
    def normarize(x):
        x = x.translate(util.trans)
        x = strip_brackets(x)
        x = x.lower()
        x = re.sub(r'(・|○|　)', ' ', x)
        x = times_char(x,'1234一二三四ⅠⅡⅢⅣabcd',4) # 数字記号の価値をN倍にする
        x = x.strip()
        x = x.replace('  ', ' ')
        return x
    x, y = normarize(x), normarize(y)
    return ldn(x, y)


def make_notification_dict():
    '''
    deprecated
    '''
    users_list = get_collection('users').find({})
    lectures_list = list(get_collection('lectures').find({}))

    for user in users_list:
        user_lectures = user.get('lectures')
        if not user_lectures:
            continue
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
                if periods and dayofweek\
                        and (subject_similarity(user_lecture['subject'], canceled_lecture['subject']) > .5)\
                        and (teachers_similarity(user_lecture['teachers'], canceled_lecture["teachers"]) > .5):
                    # ○月○日に変更
                    msg_texts_date = date.strftime('%m月%d日'.encode('unicode-escape').decode()).encode().decode("unicode-escape")
                    # 曜日を取り出す
                    msg_texts_weekday = weekday[date.weekday()][0]
                    # periods(積集合)を「・」でくっつける
                    msg_texts_periods = "・".join((map(str, periods)))
                    # 科目名
                    msg_texts_subject = canceled_lecture["subject"]
                    # 教員名
                    msg_texts_teachers = canceled_lecture["teachers"]
                    # 備考
                    msg_texts_remark = canceled_lecture.get("remark") or "なし"
                    # notifyのリスト
                    user_id = str(user["_id"])
                    notify_list = user.get('notifies', [])

                    scraping_hash = canceled_lecture["hash"]
                    message = f"""
【休講情報】
日付: {msg_texts_date}({msg_texts_weekday})
時限: {msg_texts_periods}
科目: {msg_texts_subject}
教員: {msg_texts_teachers}
備考: {msg_texts_remark}"""
                    end = datetime.datetime.timestamp(datetime.datetime.combine(date, datetime.time()) + period[min(periods)])
                    for notify_dict in notify_list:
                        dest = notify_dict.get('dest') or default_notify_dest(user_id)
                        if notify_dict["type"] == "day":
                            notify_day = datetime.datetime.combine(date, datetime.time()) + datetime.timedelta(seconds=notify_dict["offset"])
                            time_day = datetime.datetime.timestamp(notify_day)
                            make_dict(scraping_hash, message, end, dest, user_id, time_day)
                        if notify_dict["type"] == "lecture":
                            notify_lecture = datetime.datetime.combine(date, datetime.time()) + period[min(periods)] + datetime.timedelta(seconds=notify_dict["offset"])
                            time_lecture = datetime.datetime.timestamp(notify_lecture)
                            make_dict(scraping_hash, message, end, dest, user_id, time_lecture)
                        if notify_dict["type"] == "scraping":
                            notify_scraping = datetime.datetime.fromtimestamp(canceled_lecture['time'])+datetime.timedelta(seconds=notify_dict["offset"])
                            time_scraping = notify_scraping.timestamp()
                            make_dict(scraping_hash, message, end, dest, user_id, time_scraping)


def make_notification_dict2(user, user_lecture, canceled_lecture):
    '''
    検索済みのユーザー講義情報と休講情報から通知情報を作成する
    '''
    periods = canceled_lecture["periods"]
    date = datetime.date.fromtimestamp(canceled_lecture["date"])
    # ○月○日に変更
    msg_texts_date = date.strftime('%m月%d日'.encode('unicode-escape').decode()).encode().decode("unicode-escape")
    # 曜日を取り出す
    msg_texts_weekday = weekday[date.weekday()][0]
    # periods(積集合)を「・」でくっつける
    msg_texts_periods = "・".join((map(str, periods)))
    # 科目名
    msg_texts_subject = canceled_lecture["subject"]
    # 教員名
    msg_texts_teachers = canceled_lecture["teachers"]
    # 備考
    msg_texts_remark = canceled_lecture.get("remark") or "なし"
    user_id = str(user["_id"])
    # notifyのリスト
    notify_list = user.get('notifies', [settings.default_notify()])
    scraping_hash = canceled_lecture["hash"]
    message = f"""
【休講情報】
日付: {msg_texts_date}({msg_texts_weekday})
時限: {msg_texts_periods}
科目: {msg_texts_subject}
教員: {msg_texts_teachers}
備考: {msg_texts_remark}"""
    end = datetime.datetime.timestamp(datetime.datetime.combine(date, datetime.time()) + period[min(periods)])
    for notify_dict in notify_list:
        dest = notify_dict.get('dest') or default_notify_dest(user_id)
        if not dest:
            continue
        if notify_dict["type"] == "day":
            time_day=datetime.datetime(date.year,date.month,date.day)+datetime.timedelta(seconds=notify_dict['offset'])
            make_dict(scraping_hash, message, end, dest, user_id, time_day.timestamp())
        elif notify_dict["type"] == "lecture":
            notify_lecture = datetime.datetime.combine(date, datetime.time()) + period[min(periods)] + datetime.timedelta(seconds=notify_dict["offset"])
            time_lecture = datetime.datetime.timestamp(notify_lecture)
            make_dict(scraping_hash, message, end, dest, user_id, time_lecture)
        elif notify_dict["type"] == "scraping":
            notify_scraping = datetime.datetime.fromtimestamp(canceled_lecture['time'])+datetime.timedelta(seconds=notify_dict["offset"])
            time_scraping = notify_scraping.timestamp()
            make_dict(scraping_hash, message, end, dest, user_id, time_scraping)


def search_lectures():
    '''
    ユーザーの講義情報とシラバス番号から対象の休講情報を検索する
    '''
    users = list(get_collection('users').find({}))
    c_lectures = get_collection('lectures')

    for u in users:
        for ul in u.get('lectures', []):
            lecture = c_lectures.find_one({'class_num': ul.get('class_num')})
            if lecture:
                make_notification_dict2(u, ul, lecture)


def lectures_class_nums(lecture, syllabus):
    '''
    lectureからシラバス番号を求める
    syllabusはリスト
    '''
    l_dayofweek = datetime.datetime.fromtimestamp(lecture.get('date')).weekday()
    l_times = [10*l_dayofweek+p for p in lecture.get('periods')]
    result=[]
    for s in syllabus:
        if s.get('when', {}).get('type') == 'time':
            s_times = map(lambda t: t['dayofweek']*10+t['period'], s['when'].get('times'))
            if teachers_similarity(lecture.get('teachers', ''), s.get('teachers', '')) > .5 and \
                    subject_similarity(lecture.get('subject', ''), s.get('subject', '')) > .5 and \
                    (set(s_times) & set(l_times)):
                print(s.get('class_num'))
                result.append(s.get('class_num'))
    if not result:
        log(__name__,f'Cannot determine class numbers: {lecture}',5)
    return result


if not isinpackage:
    syllabus = list(get_collection('syllabus').find({}))
    lectures = list(get_collection('lectures').find({}))
    for l in lectures:
        print(lectures_class_nums(l, syllabus))
