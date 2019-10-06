import math
import datetime
from bson.objectid import ObjectId
isinpackage = not __name__ in ['notify', '__main__']

if isinpackage:
    from .settings import settings
    from . import util
    from .util import Just
    from .db import get_collection
else:
    from settings import settings
    from db import get_collection
    from util import Just

users = get_collection('users')


def add_notify(realid, data={
    'type': '',
    'offset': 0,
    'dest': ''
}):
    notifies = get_notifies(realid)
    if len(notifies) < 10 and not next(filter(lambda e: all(data[k] == v for k, v in e.items()), notifies), None):
        users.update_one({'_id': ObjectId(realid)}, {
            '$push': {'notifies': data}
        })
        return True
    else:
        # 最大10個までorすでに同じのがある
        return False


def get_notifies(realid):
    return Just(users.find_one({'_id': ObjectId(realid)})).notifies([])


offset2strfn = {
    'scraping': lambda tmp, td, offset: '休講情報を見つけた直後',
    'day': lambda tmp, td, offset: f'講義日の{abs(td.days)}日前の{tmp.hour}時{tmp.minute}分',
    'lecture': lambda tmp, td, offset: f'講義開始時間の{int(offset/3600)}時間前'
}


def day_hour_minute_to_day_offset(d, h, m):
    date0 = (datetime.datetime(2019, 1, 1, h, m, 0)+datetime.timedelta(days=d))
    date1 = datetime.datetime(2019, 1, 1, 0, 0, 0)
    return int((date0-date1).total_seconds())


def format_notify(data):
    offset = data['offset']
    _type = data['type']
    td = datetime.timedelta(seconds=offset)
    tmp = datetime.datetime(2019, 1, 1, 0, 0, 0)+td
    return f'{offset2strfn[_type](tmp,td,offset)}に{data.get("dest","デフォルトの通知先")}で通知'


def format_notifies(realid):
    s = []
    for i, e in enumerate(get_notifies(realid)):
        s.append(f'【{str(i+1).rjust(2)}】{format_notify(e)}')
    return '\n'.join(s)


def delete_notify(realid, num):
    if isinstance(num, int) and 1 <= num <= 10:
        users.update_one({'_id': ObjectId(realid)}, {
            '$unset': {f'notifies.{num-1}': None}
        })
        users.update_one({'_id': ObjectId(realid)}, {
            '$pull': {f'notifies': None}
        })


# print(add_notify('5d99a36bceda111bb76efa68', {'type': 'day', 'offset': -97200, 'dest': 'line'}))
# print(format_notifies('5d99a36bceda111bb76efa68'))
# print(delete_notify('5d99a36bceda111bb76efa68', 1))
