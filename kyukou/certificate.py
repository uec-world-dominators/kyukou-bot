from . import scheduler
from .db import get_collection
import time
from bson.objectid import ObjectId
from . import util

certificate = get_collection('certificate')


def generate_token(real_user_id, type, options={}, expire_in=3600):
    certificate.delete_many({"real_user_id": real_user_id, 'type': type})
    while True:
        token = util.generate_id(50)
        if not certificate.find_one({"token": token}):
            break
    default = {"real_user_id": real_user_id, 'type': type, "token": token, "expire_at": time.time()+expire_in}
    default.update(options)
    certificate.insert_one(default)
    return token


def validate_token(type, real_user_id, token, expire=True):
    data = certificate.find_one({"token": token, 'type': type})
    if data:
        if expire:
            certificate.delete_one({"token": token, 'type': type})
        return data["real_user_id"] == real_user_id and data
    else:
        return False


def delete_expired():
    certificate.delete_many({"expire_at": {"$lt": time.time()}})


def register_state(state, type, options={}, expire_in=3600):
    d = {
        'state': state,
        'type': type,
        "expire_at": time.time()+expire_in
    }
    d.update(options)
    certificate.delete_many({"state": state, 'type': type})
    certificate.insert_one(d)


def validate_state(state, type, expire=True):
    d = {
        'state': state,
        'type': type,
        'expire_at': {'$gt': time.time()}
    }
    data = certificate.find_one(d)
    if expire:
        certificate.delete_one(d)
    return data


scheduler.add_task(60, delete_expired)
