import time
from bson.objectid import ObjectId

isinpackage = not __name__ in ['publish', '__main__']
if isinpackage:
    from . import line_notify_api
    from . import twitter_api
    from .db import get_collection
    from .settings import store, load, settings
    from .util import has_all_key
    from .log import log
else:
    # import line_notify_api
    # import twitter_api
    from db import get_collection
    # from settings import store, load, settings
    # from util import has_all_key

queue = get_collection('queue')
# queue.drop()

def try_add_notification(data={
    'hash': '',
    'time': 0,
    'end': 0,
    'message': '',
    'dest': '',
    'user_id': ''
}):
    '''
    通知をキューに追加する（存在するかは考慮している）
    '''
    data['time']=int(data['time'])
    data['end']=int(data['end'])
    assert has_all_key(data, 'hash', 'time', 'end', 'message', 'dest', 'user_id')
    if data['end']>=time.time() and  not queue.find_one(data):
        # 古いものは受け付けない
        print(data)
        data.update({'finish': False})
        queue.insert_one(data) # 追加されてない

def delete_old():
    '''
    講義時間を過ぎた&通知済みの通知をキューから削除する
    '''
    queue.delete_many({'end': {'$lt': time.time()}, 'finish': True})


def publish_all():
    '''
    通知を実行する。今よりも通知時間が古いものを持ってきて
    '''
    last_publish = load('last_publish', 0)
    now = time.time()+60
    for data in queue.find({
            'time': {'$lte': last_publish},
            'finish': False
    }):
        # print(data)
        if True or publish_one(data):
            print('set to True')
            print(data['_id'])
            queue.update_one({'_id': data['_id']}, {
                '$set': {'finish': True}
            }) # これをすると、try_add_notificationsで追加される
    delete_old()
    store('last_publish', now)


def publish_one(data):
    '''
    通知を一つ処理する
    通知に成功したらTrueを返す
    '''
    dest = data['dest']
    realid = data.get('user_id')
    if dest == 'line':
        return line_notify_api.has_account(realid) and line_notify_api.send(realid, data.get('message'))
    elif dest == 'twitter':
        twitter_id = twitter_api.get_twitter_user_id(realid)
        return twitter_id and twitter_api.send(twitter_id, data.get('message'))
    else:
        return False

def remove_queue(realid):
    queue.delete_many({'user_id':realid,'time':{'$gt':time.time()}})