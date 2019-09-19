import random


def dict_to_tuples(d):
    return [(key, value) for key, value in d.items()]


id_string = 'abcdefghijklmnopqrstuvwxyz0123456789'


def generate_id(n):
    return ''.join([random.choice(id_string) for i in range(n)])
