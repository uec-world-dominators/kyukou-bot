import requests
from datetime import datetime
from bs4 import BeautifulSoup
from pprint import pprint
import re
import hashlib
import time
from .db import get_collection
from .util import log


def mdnum(month, day):
    return month*100+day


def getyear(month, day):
    now = datetime.now()
    mdnum_now = mdnum(now.month, now.day)
    if 401 <= mdnum_now <= 1231:
        return (not mdnum_now <= mdnum(month, day) <= 1231) + now.year
    elif 101 <= mdnum_now <= 331:
        return (not 101 <= mdnum(month, day)) + now.year


def testdata():
    data = [{
        "date": datetime(2019, 10, 14).timestamp(),
        "teachers": "皆川",
        "subject": "キャリア教育基礎",
        "periods": [1]
    }, {
        "date": datetime(2019, 10, 15).timestamp(),
        "teachers": "MOREAU ROBERT",
        "subject": "Academic Spoken English Ⅰ",
        "periods": [1]
    }, {
        "date": datetime(2019, 10, 18).timestamp(),
        "teachers": "小林",
        "subject": "基礎科学実験B",
        "periods": [3, 4]
    }, {
        "date": datetime(2019, 10, 14).timestamp(),
        "teachers": "○八百",
        "subject": "健康・体力つくり実習（テニス）",
        "periods": [4]
    }]
    for d in data:
        d["hash"] = hashlib.sha256((str(d['date'])+d['subject']).encode()).hexdigest()
    return data


def kyuukou():

    req = requests.get('http://kyoumu.office.uec.ac.jp/kyuukou/kyuukou.html')
    req.encoding = 'shift_jis'
    html = req.text

    doc = BeautifulSoup(html, 'html.parser')

    limits = []
    c = re.compile(r'(\d+)月(\d+)日\(.\)')
    for tr in doc.select('tr')[1:]:
        a = tr.select('td')
        m = c.match(a[1].text)
        month, day = int(m.group(1)), int(m.group(2))
        date = datetime(getyear(month, day), month, day)
        limit = {
            "date": date.timestamp(),
            "teachers": a[4].text,
            "periods": list(map(int, a[2].text.split('・'))),
            "class": a[0].text,
            "subject": a[3].text,
            "remark": a[5].text.replace(u'\xa0', ''),
            "hash": hashlib.sha256((str(date.timestamp())+tr.text).encode()).hexdigest()
        }

        limits.append(limit)
    return limits


def compare(new, old_collection):
    c_insert = 0
    c_delete = 0
    for x in new:
        if not old_collection.find_one({'hash': x['hash']}):
            # 新しい情報
            old_collection.insert_one(x)
            c_insert += 1
    # oldの今日以降の予定を見ていって、newになければ削除された
    for x in old_collection.find({'date': {'$gt': time.time()}}):
        if not next(filter(lambda e: e['hash'] == x['hash'], new), None):
            # 消された
            old_collection.delete_one({'hash': x['hash']})
            c_delete += 1
    log(__name__, f'Scraped: {len(new)} , Insert: {c_insert} , Delete: {c_delete}')


def run():
    compare(kyuukou(), get_collection('lectures'))
    get_collection('lectures').insert_many(testdata())

