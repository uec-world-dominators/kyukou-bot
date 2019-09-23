import requests
from datetime import datetime
from bs4 import BeautifulSoup
from pprint import pprint
import datetime,re
import hashlib
import time
from .scheduler import add_task
from .db import get_collection


def kyuukou():

    req=requests.get('http://kyoumu.office.uec.ac.jp/kyuukou/kyuukou.html')
    req.encoding='shift_jis'
    html=req.text

    doc=BeautifulSoup(html,'html.parser')

    limits=[]
    c = re.compile(r'(\d+)月(\d+)日\(.\)')
    for tr in doc.select('tr')[1:]:
        a=tr.select('td')
        m = c.match(a[1].text)
        date = datetime.datetime(2019, int(m.group(1)), int(m.group(2)))
        # if "○" in a[4].text:
        #     tmp = a[4].text.replace("o", "")
        # else:
        #     tmp = a[4].text
        limit={
            "date":date.timestamp(),
            "teachers":a[4].text, # tmp
            "periods":list(map(int, a[2].text.split('・'))),
            "class":a[0].text,
            "subject":a[3].text,
            "remark":a[5].text.replace(u'\xa0',''),
            "hash":hashlib.sha256(tr.text.encode()).hexdigest()
        }

        limits.append(limit)

    return limits


def compare(new,old_collection):
    for x in new:
        if not old_collection.find_one({'hash':x['hash']}):
            # 新しい情報
            old_collection.insert_one(x)
    # oldの今日以降の予定を見ていって、newになければ削除された
    for x in old_collection.find({'date':{'$gt':time.time()}}):
        if not next(filter(lambda e:e['hash']==x['hash'],new),None):
            # 消された
            old_collection.delete_one({'hash':x['hash']})

def run():
    compare(kyuukou(),get_collection('lectures'))

add_task(3600,run)


pprint(kyuukou())