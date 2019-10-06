from bson import ObjectId
isinpackage = not __name__ in ['user_data', '__main__']
if isinpackage:
    from .db import get_collection
    from .util import Just
else:
    from db import get_collection

users = get_collection('users')


def default_notify_dest(realid):
    user = Just(users.find_one({'_id': ObjectId(realid)}))
    if user.connections.twitter():
        return 'twitter'
    if user.connections.line():
        return 'line'
    return None


def syllabus_links(realid):
    pass
