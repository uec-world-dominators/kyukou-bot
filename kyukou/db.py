from pprint import pprint
from pymongo import MongoClient
import datetime
from .util import log

db = None


def init(url):
    client = MongoClient(url)
    global db
    db = client.kyukou
    log(__name__, f'Connected to DB: "{url}"')
    log(__name__, '-'*50)
    log(__name__, f'Number of Users   : {get_collection("users").count()}')
    log(__name__, f'Number of Lectures: {get_collection("lectures").count()}')
    log(__name__, '-'*50)


def get_collection(name):
    return db[name]


__all__ = ["init", "get_collection"]
