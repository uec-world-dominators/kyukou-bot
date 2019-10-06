from pprint import pprint
from pymongo import MongoClient
from urllib.parse import quote_plus
import datetime
isinpackage = not __name__ in ['db', '__main__']
if isinpackage:
    from .util import log
    from .settings import settings
else:
    from settings import settings
    def log(module, msg):
        print(module, msg)
db = None


def init(url):
    if settings.mongod():
        url_ = url.replace("{username}", quote_plus(settings.mongod.username())).replace("{password}", quote_plus(settings.mongod.password()))
    else:
        url_ = url
    client = MongoClient(url_)
    global db
    db = client.kyukou
    log(__name__, f'Connected to DB: "{url}"')
    log(__name__, '-'*50)
    log(__name__, f'Number of Users   : {len(list(get_collection("users").find({})))}')
    log(__name__, f'Number of Lectures: {len(list(get_collection("lectures").find({})))}')
    log(__name__, '-'*50)


def get_collection(name):
    return db[name]


if not isinpackage:
    from settings import settings
    init(settings.mongo_url())


__all__ = ["init", "get_collection"]
