from .scheduler import add_task
import time
isinpackage = not __name__ in ['publish', '__main__']
if isinpackage:
    from .db import get_collection
    from .settings import store, load, settings
    from .util import has_all_key
else:
    from db import get_collection
    from settings import store, load, settings
    from util import has_all_key

queue = get_collection('queue')


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
    assert has_all_key(data, 'hash', 'time', 'end', 'message', 'dest', 'user_id')
    if not queue.find_one(data):
        data.update({'finish': False})
        queue.insert_one(data)


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
    now = time.time()+0  # 安全のために少し早めに通知したいときはここを変える
    for data in queue.find({
            # 'time': {'$lte': last_publish},
            'finish': False
    }):
        if publish_one(data):
            queue.update_one({'_id': data['_id']}, {
                '$set': {'finish': True}
            })
    delete_old()
    store('last_publish', now)


add_task(60, publish_all)


def publish_one(data):
    '''
    通知を一つ処理する
    '''
    dest = data['dest']
    if dest == 'line':
        pass
    elif dest == 'twitter':
        pass
    print('PUBLISH', data['message'])
    return True
