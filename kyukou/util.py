import os
import json
from datetime import datetime
import random
import inspect
from threading import Lock
import sys
import traceback

dayofweek = '月火水木金土日'


def ignore_error(fn_args_list=[]):
    def _ignore_error():
        for fn, *args in fn_args_list:
            try:
                fn(*args)
            except:
                log(__name__, traceback.format_exc())
    return _ignore_error


def mdnum(month, day):
    return month*100+day


def getyear(month, day):
    now = datetime.now()
    mdnum_now = mdnum(now.month, now.day)
    if 401 <= mdnum_now <= 1231:
        return (not mdnum_now <= mdnum(month, day) <= 1231) + now.year
    elif 101 <= mdnum_now <= 331:
        return (not 101 <= mdnum(month, day)) + now.year


def dict_to_tuples(d):
    return [(key, value) for key, value in d.items()]


id_string = 'abcdefghijklmnopqrstuvwxyz0123456789'
log_lock = Lock()
log_file = None


def log(__name__, message, log_level=2):
    from .settings import settings
    global log_file
    log_file = log_file or os.path.join(os.path.dirname(__file__), settings.logfile())
    msg = f'{datetime.now()}  |  [{__name__.ljust(20)}]  {message}'
    with log_lock:
        if log_level >= settings.log_level(0):
            sys.stdout.write(msg)
            sys.stdout.write('\n')
            sys.stdout.flush()
        with open(log_file, 'at', encoding='utf-8') as f:
            f.write(msg+'\n')


def generate_id(n):
    return ''.join([random.choice(id_string) for i in range(n)])


def has_all_key(d, *keys):
    for key in keys:
        if not key in d:
            return False
    return True


class Just(json.JSONEncoder):
    """
    # Maybe Monad
    ## usage
    ```
    d = {
        "a": {
            "b": 1
        }
    }
    ```
    ### Get Value from Maybe Monad
    ```
    Just(d).a() # {'b': 1}
    Just(d).a.b() # 1
    Just(d).a.b.c() # None
    ```
    ### None Propagation
    ```
    Just(d).b.c() # None
    ```
    ### Default Value
    ```
    Just(d).b.c('Default') # 'Default'
    ```
    ### Function
    ```
    Just(d).a.b[lambda n:n*10]() # 10
    ```
    """

    def __init__(self, a):
        object.__setattr__(self, 'a', a)

    def __call__(self, default=None):
        a = object.__getattribute__(self, 'a')
        return default if a == None else a

    def __getattribute__(self, key):
        a = object.__getattribute__(self, 'a')
        if isinstance(a, dict) and (key in a):
            return Just(a[key])
        else:
            return Just(None)

    def __getitem__(self, f):
        if callable(f):
            try:
                r = f(object.__getattribute__(self, 'a'))
            except:
                r = None
            return Just(r)
        elif isinstance(f, str):
            return object.__getattribute__(self, 'a')[f]  # 既存コードとの互換性のためJustは返さない
        else:
            raise RuntimeError

    def __rshift__(self, f):
        if callable(f):
            return Just(f(object.__getattribute__(self, 'a')))


class Curry(object):
    """
    # Curry
    ```
    def f(a, b):
        return a+b
    print(Just([1, 2, 3])[Curry(map, 2)[lambda n:n**2]][list][sum]())
    # 14
    ```
    """

    def __init__(self, f, argc=None):
        self.f = f
        self.argv = []
        self.argc = argc or len(inspect.getfullargspec(f).args)

    def __getitem__(self, x):
        if isinstance(x, tuple):
            self.argv += list(x)
        else:
            self.argv.append(x)
        if len(self.argv) > self.argc:
            raise RuntimeError
        return self

    def __call__(self, *args):
        if len(self.argv)+len(args) != self.argc:
            raise RuntimeError
        else:
            return self.f(*self.argv, *args)


def ld(x, y):
    lx, ly = len(x), len(y)
    if lx < ly:
        return ld(y, x)
    if ly == 0:
        return lx
    p = range(len(y)+1)
    for i, cx in enumerate(x):
        c = [i+1]
        for j, cy in enumerate(y):
            c.append(min(p[j+1]+1, c[j]+1, p[j]+(cx != cy)))
        p = c
    return p[-1]


def ldn(s1, s2):
    return 1-ld(s1, s2)/max(len(s1), len(s2))


def find_index(array, e, default=-1):
    if not e:
        return default
    for i, c in enumerate(array):
        if c == e:
            return i
    return default


def strip_brackets(x):
    result = ''
    nest = 0
    begin, end = '([{（「【［〈《', '}])）」】］〉》'
    for c in x:
        if find_index(begin, c) > -1:
            nest += 1
        elif find_index(end, c) > -1:
            nest -= 1
        elif not nest:
            result += c
    return result


def remove_them(x, array='1234'):
    result = ''
    for c in x:
        if not c in array:
            result += c
    return result

trans = str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})
