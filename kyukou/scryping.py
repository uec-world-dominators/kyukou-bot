import requests
from datetime import datetime
from bs4 import BeautifulSoup
from pprint import pprint
import datetime,re
import hashlib
import time
from .scheduler import add_task
from .db import get_collection
from .util import log


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
        limit={
            "date":date.timestamp(),
            "teachers":a[4].text,
            "periods":list(map(int, a[2].text.split('・'))),
            "class":a[0].text,
            "subject":a[3].text,
            "remark":a[5].text.replace(u'\xa0',''),
            "hash":hashlib.sha256(tr.text.encode()).hexdigest()
        }

        limits.append(limit)
    return limits


def compare(new,old_collection):
    c_insert=0
    c_delete=0
    for x in new:
        if not old_collection.find_one({'hash':x['hash']}):
            # 新しい情報
            old_collection.insert_one(x)
            c_insert+=1
    # oldの今日以降の予定を見ていって、newになければ削除された
    for x in old_collection.find({'date':{'$gt':time.time()}}):
        if not next(filter(lambda e:e['hash']==x['hash'],new),None):
            # 消された
            old_collection.delete_one({'hash':x['hash']})
            c_delete+=1
    log(__name__,f'Scraped: {len(new)} , Insert: {c_insert} , Delete: {c_delete}')

def run():
    compare(kyuukou(),get_collection('lectures'))

add_task(3600,run)