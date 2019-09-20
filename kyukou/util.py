import random


def dict_to_tuples(d):
    return [(key, value) for key, value in d.items()]


id_string = 'abcdefghijklmnopqrstuvwxyz0123456789'


def generate_id(n):
    return ''.join([random.choice(id_string) for i in range(n)])


class ArgDict():
    def __init__(self, d):
        self.__dict__ = d
        for k in d.keys():
            if isinstance(d[k], dict):
                d[k] = ArgDict(d[k])

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return get_nested_item(self.__dict__, *key)
        else:
            return get_nested_item(self.__dict__, key)

    def __contains__(self, key):
        return key in self.__dict__


def get_nested_item_basic(d, keys, default=None):
    if not (isinstance(d, dict) or isinstance(d, ArgDict) and keys[0] in d):
        return default
    if len(keys) == 1:
        return d[keys[0]]
    else:
        return get_nested_item_basic(d[keys[0]], keys[1:], default)


def get_nested_item(d, keys_src, default=None):
    return get_nested_item_basic(d, keys_src.split('.'), default)


__all__ = ["ArgDict", "dict_to_tuples", "generate_id", "get_nested_item"]
