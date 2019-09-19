from pprint import pprint
from pymongo import MongoClient
import datetime

db = None


def init(url):
    client = MongoClient(url)
    global db
    db = client.kyukou
    print(f'Connected to DB: "{url}"')
    print('-'*50)
    print(f'Number of Users: {get_collection("users").count()}')
    print('-'*50)


def get_collection(name):
    return db[name]


__all__ = ["init", "get_collection"]
