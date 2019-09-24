from datetime import datetime
import random
import inspect
from threading import Lock
import sys

def dict_to_tuples(d):
    return [(key, value) for key, value in d.items()]


id_string = 'abcdefghijklmnopqrstuvwxyz0123456789'
log_lock = Lock()


def log(__name__, message):
    from .settings import settings
    msg = f'{datetime.now()}  |  [{__name__.ljust(20)}]  {message}'
    with log_lock:
        sys.stdout.write(msg)
        sys.stdout.write('\n')
        sys.stdout.flush()
        with open(settings.logfile(), 'at', encoding='utf-8') as f:
            f.write(msg+'\n')


def generate_id(n):
    return ''.join([random.choice(id_string) for i in range(n)])


class Just(object):
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
            return Just(f(object.__getattribute__(self, 'a')))
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


__all__ = ["dict_to_tuples", "generate_id", "Just", "Curry"]
