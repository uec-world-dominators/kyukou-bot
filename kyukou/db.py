from pprint import pprint
from pymongo import MongoClient
import datetime

from .settings import settings


class Db:
    @classmethod
    def init(cls, url):
        cls.client = MongoClient(url)
        print(f'connected to mongo db with url {settings["mongo_url"]} .')
        cls.db = cls.client.kyukou
        cls.users = cls.db.users
        cls.lectures = cls.db.lectures
