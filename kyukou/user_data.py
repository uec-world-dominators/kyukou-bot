from bson import ObjectId
isinpackage = not __name__ in ['user_data', '__main__']
if isinpackage:
    from .db import get_collection
    from .util import Just, dayofweek
else:
    from db import get_collection
    from util import Just, dayofweek

users = get_collection('users')


def default_notify_dest(realid):
    user = Just(users.find_one({'_id': ObjectId(realid)}))
    if user.connections.twitter():
        return 'twitter'
    if user.connections.line():
        return 'line'
    return None


def format_course(lecture):
    return f"[{dayofweek[lecture.get('dayofweek',-1)]} {', '.join(lecture.get('periods'))}] {lecture.get('subject','-')}"


def list_of_courses(realid):
    '''
    履修科目一覧
    '''
    lectures = Just(users.find_one({'_id': ObjectId(realid)})).lectures([])
    return '\n'.join(map(format_course, lectures))


def syllabus_links(realid):
    pass
