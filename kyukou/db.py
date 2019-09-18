from pprint import pprint
from pymongo import MongoClient
import datetime


class Db:
    @classmethod
    def init(cls, url):
        cls._client = MongoClient(url)
        print(f'connected to mongo db with url {url} .')
        cls._db = cls._client.kyukou
        cls._users = cls._db.users
        cls._lectures = cls._db.lectures

    @classmethod
    def get_users_db(cls):
        return cls._users

    @classmethod
    def get_lectures_db(cls):
        return cls._lectures
